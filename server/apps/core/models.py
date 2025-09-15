import datetime

from django.contrib.postgres.fields import ArrayField
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_ipv4_address,
)
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from server.apps.core.data.llm import LLM_TEMPLATE_DEFAULT, SYSTEM_LLM_PROMPT_DEFAULT
from server.apps.core.data.regions import COUNTRIES, REGIONS
from server.apps.users.models import User


class IncidentType(models.Model):
    model_path = models.CharField(max_length=100, null=True)
    treshold = models.FloatField("Treshold для модели", default=1)
    description = models.CharField(
        "Название модели", max_length=128, null=True, blank=True
    )
    llm_prompt = models.TextField("LLM промпт", null=True, blank=True)
    llm_system_prompt = models.TextField(
        "LLM системный промпт", null=True, blank=True, default=SYSTEM_LLM_PROMPT_DEFAULT
    )
    llm_template = models.TextField(
        "LLM шаблон", null=True, blank=True, default=LLM_TEMPLATE_DEFAULT
    )
    llm_model_name = models.CharField(
        "LLM модель", null=True, blank=True, max_length=100
    )
    is_active = models.BooleanField(verbose_name="Активный", default=False)
    should_sent_to_bot = models.BooleanField(
        default=True, verbose_name="Показывать в боте"
    )

    def __str__(self) -> str:
        return str(self.description)

    class Meta:
        verbose_name = "Тип инцидента"
        verbose_name_plural = "Типы инцидентов"


DEFAULT_COUNTRY_ID: int = 11  # Russia


class Country(models.Model):
    name = models.CharField("Страна", choices=COUNTRIES,
                            default="RUS", max_length=100)

    def __str__(self) -> str:
        return self.get_full_country_name()

    def get_full_country_name(self):
        return dict(COUNTRIES).get(self.name, "Unknown country")

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class Region(models.Model):
    name = models.CharField("Регион", choices=REGIONS,
                            default="ALL", max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.get_full_region_name()

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"

    def get_full_region_name(self):
        return dict(REGIONS).get(self.name, "Unknown region")


class BaseIncident(models.Model):
    UNPROCESSED = 0
    PROCESSED_AND_REJECTED = 1
    PROCESSED_AND_ACCEPTED = 2
    COMMUNICATION = 3
    IN_PROGRESS = 4
    COMPLETED = 5
    DELETED = 6
    STATUSES = [
        (UNPROCESSED, "Не обработан"),
        (PROCESSED_AND_REJECTED, "Отклонен"),
        (PROCESSED_AND_ACCEPTED, "Принят"),
        (COMMUNICATION, "Коммуникации"),
        (IN_PROGRESS, "В работе"),
        (COMPLETED, "Выполнен"),
        (DELETED, "Удален"),
    ]
    ACTIVE_STATUSES = (
        PROCESSED_AND_ACCEPTED,
        COMMUNICATION,
        IN_PROGRESS,
    )
    PUBLIC_STATUSES = (PROCESSED_AND_ACCEPTED, COMPLETED)

    title = models.TextField("Заголовок", null=True, blank=True)
    description = models.TextField("Описание", null=True, blank=True)
    status = models.IntegerField(
        "Статус", choices=STATUSES, null=False, blank=False, default=UNPROCESSED
    )
    create_date = models.DateTimeField("Дата создания", default=timezone.now)
    update_date = models.DateTimeField("Дата обновления", auto_now=True)
    assigned_to = models.ForeignKey(
        User,
        verbose_name="Пользователь, назначенный на заявку",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )
    related_article = models.ForeignKey(
        "Article",
        verbose_name="Статья",
        related_name="articles",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    incident_type = models.ForeignKey(
        IncidentType, null=True, on_delete=models.SET_NULL
    )
    count = models.PositiveIntegerField("Количество ограничений", default=1)
    urls = ArrayField(
        models.URLField(blank=True, default="", null=True), blank=True, null=True
    )
    public_title = models.CharField(
        "Публичное название", max_length=512, null=True, blank=True
    )
    public_description = models.TextField(
        "Публичное описание", null=True, blank=True)

    @property
    def source(self):
        """Get the source of the related article if it exists."""
        if hasattr(self, 'related_article') and self.related_article:
            return self.related_article.source
        return None

    class Meta:
        abstract = True

    def __str__(self):
        return self.any_title()

    def any_title(self):
        return self.public_title or self.title or self.any_description()[:200] + "..."

    def any_description(self):
        if self.public_description:
            return self.public_description

        if self.description:
            return self.description
        return ""


class MediaIncident(BaseIncident):
    duplicate = models.ForeignKey(
        "self",
        verbose_name="Дубликат",
        on_delete=models.SET_NULL,
        related_name="duplicates",
        null=True,
        blank=True,
    )
    downvote = models.PositiveSmallIntegerField(
        "Downvoted", default=0, null=True, blank=True
    )

    def get_absolute_url(self):
        return reverse("core:dashboard-mediaincident-update", args=[self.pk])

    class Meta:
        verbose_name = "Инцидент из СМИ"
        verbose_name_plural = "Инциденты из СМИ"


class Source(models.Model):
    url = models.TextField(
        verbose_name="URL списка новостей", null=False, unique=True)
    is_active = models.BooleanField(verbose_name="Активен", default=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        default=DEFAULT_COUNTRY_ID,
    )
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, default=None, null=True, blank=True
    )
    is_telethon = models.BooleanField(
        verbose_name="Парсинг через телетон", default=False
    )
    public_tg_channel_link = models.CharField(
        verbose_name="Название источника", max_length=255, null=True, blank=True
    )
    needs_proxy = models.BooleanField(
        verbose_name=_("Требуется прокси"), default=False)

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"

    def clean(self):
        super().clean()
        if self.is_telethon and not self.public_tg_channel_link:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                {'public_tg_channel_link': 'Это поле обязательно, если включен парсинг через телетон.'}
            )

    def __str__(self):
        return "Source [{}]".format(self.url)


class Article(models.Model):
    source = models.ForeignKey(
        Source,
        verbose_name="Источник",
        related_name="article",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    url = models.URLField(verbose_name="URL", max_length=1024, primary_key=True)
    title = models.TextField(
        verbose_name="Заголовок", default="", blank=True, null=True
    )
    text = models.TextField(verbose_name="Текст",
                            default="", blank=True, null=True)
    is_downloaded = models.BooleanField(verbose_name="Скачана", default=False)
    is_parsed = models.BooleanField(verbose_name="Обработана", default=False)
    is_incident_created = models.BooleanField(
        verbose_name="Инцидент создан", default=False
    )
    is_duplicate = models.BooleanField(verbose_name="Дубликат", default=False)
    duplicate_url = models.URLField(
        verbose_name="Дубликат чего", max_length=1024, null=True, blank=True
    )
    is_redirect = models.BooleanField(verbose_name="Редирект", default=False)
    is_incorrect = models.BooleanField(
        verbose_name="Некорректная статья", default=False)
    redirect_url = models.URLField(
        verbose_name="Редирект куда", max_length=1024, null=True, blank=True
    )

    rate = models.JSONField(
        verbose_name="Оценка релевантности", default=dict, blank=True, null=True)
    incident = models.OneToOneField(
        MediaIncident,
        verbose_name="Инцидент",
        related_name="article",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    create_date = models.DateTimeField("Дата создания", default=timezone.now)
    publication_date = models.DateField(
        "Дата публикации", null=True, blank=True)

    def save(self, *args, **kwargs):
        self.title = self.any_title()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Cтатья"
        verbose_name_plural = "Статьи"

    def any_title(self):
        if self.title:
            return self.title
        if not self.text:
            return ""

        try:
            first_sentence_end = self.text.index(".")
        except ValueError:
            first_sentence_end = 0

        if first_sentence_end > 20:
            return self.text[:first_sentence_end]
        if len(self.text) > 200:
            return self.text[:200] + "..."

        return self.text

    @property
    def region(self):
        if self.source and self.source.region:
            return self.source.region
        # Get default region with name 'ALL' for the default country
        default_country = Country.objects.get(name="RUS")
        return Region.objects.get(name="ALL", country=default_country)

    @property
    def country(self):
        if self.source:
            return self.source.country
        return Country.objects.get(name="RUS")  # Get default country instance


class Proxy(models.Model):
    ip = models.GenericIPAddressField(
        _("IP адрес"), protocol="IPv4", validators=[validate_ipv4_address], unique=True
    )
    port = models.PositiveIntegerField(
        _("Порт"),
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
    )
    login = models.CharField(_("Логин"), max_length=128, null=True, blank=True)
    password = models.CharField(
        _("Пароль"), max_length=128, null=True, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, verbose_name=_("Страна")
    )
    is_active = models.BooleanField(_("Активен"), default=True)
    last_check = models.DateTimeField(
        _("Последняя проверка"), null=True, blank=True)
    error_type = models.CharField(
        _("Тип ошибки"), max_length=50, null=True, blank=True)
    error_message = models.TextField(
        _("Сообщение об ошибке"), blank=True, null=True)

    class Meta:
        verbose_name = _("Прокси")
        verbose_name_plural = _("Прокси")
        unique_together = ("ip", "port")
        ordering = ["country", "ip", "port"]

    def __str__(self):
        return f"{self.ip}:{self.port}"

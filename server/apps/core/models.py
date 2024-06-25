# -*- coding: utf-8 -*-
import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from server.apps.core.data.regions import COUNTRIES, REGIONS
from server.apps.core.logic.region import region_code
from server.apps.users.models import User


from server.settings.components.common import MODELS_DIR


class IncidentType(models.Model):
    model_path = models.CharField(max_length=100, null=True)
    treshold = models.FloatField("Treshold для модели", default=1)
    description = models.CharField(
        "Название модели", max_length=128, null=True, blank=True
    )
    chat_gpt_prompt = models.TextField("Chat-GPR промпт", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="Активный", default=False)
    should_sent_to_bot = models.BooleanField(
        default=True, verbose_name="Показывать в боте"
    )

    @property
    def model_directory(self):
        return MODELS_DIR.joinpath(self.model_path) if self.model_path else None

    @classmethod
    def get_choices(cls):
        return [
            (incident_type.id, incident_type.description)
            for incident_type in cls.objects.all()
        ]

    def __str__(self) -> str:
        return str(self.description)

    class Meta:
        verbose_name = "Тип инцидента"
        verbose_name_plural = "Типы инцидентов"


DEFAULT_COUNTRY_ID: int = 11  # RUssia


class Country(models.Model):
    name = models.CharField("Страна", choices=COUNTRIES, default="RUS", max_length=100)

    def __str__(self) -> str:
        return self.name

    def get_full_country_name(self):
        return dict(COUNTRIES).get(self.name, "Unknown country")

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class Region(models.Model):
    name = models.CharField("Регион", choices=REGIONS, default="ALL", max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name}, {self.country.name}"

    def get_full_region_name(self):
        return dict(REGIONS).get(self.name, "Unknown region")

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"


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
    create_date = models.DateField("Дата создания", default=datetime.date.today)
    update_date = models.DateField("Дата обновления", auto_now=True)
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
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

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
    public_description = models.TextField("Публичное описание", null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "[{}]".format(self.any_title())

    def processed(self):
        return self.status != self.UNPROCESSED

    def processed_and_accepted(self):
        return self.status in self.ACTIVE_STATUSES

    def any_title(self):
        return self.public_title or self.title or self.any_description()[:200] + "..."

    def any_description(self):
        if self.public_description:
            return self.public_description

        if self.description:
            return self.description
        return ""

    def status_color(self):
        try:
            return ["danger", "warning", "success", "success", "success", "secondary"][
                self.status
            ]
        except IndexError:
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

    def get_absolute_url(self):
        return reverse("core:dashboard-mediaincident-update", args=[self.pk])

    def get_description(self):
        if self.public_description:
            return (
                self.public_description[150] + "..."
                if len(self.public_description) >= 160
                else self.public_description
            )
        return ""

    class Meta:
        verbose_name = "Инцидент из СМИ"
        verbose_name_plural = "Инциденты из СМИ"


class Source(models.Model):
    url = models.TextField(verbose_name="URL списка новостей", null=False, unique=True)
    is_active = models.BooleanField(verbose_name="Активен", default=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        default=11,
    )
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, default=None, null=True, blank=True
    )

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"

    def __str__(self):
        return "Source [{}]".format(self.url)


class Article(models.Model):
    source = models.ForeignKey(
        Source,
        verbose_name="Источник",
        related_name="articles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    url = models.TextField(primary_key=True, verbose_name="URL", default="", blank=True)
    title = models.TextField(
        verbose_name="Заголовок", default="", blank=True, null=True
    )
    text = models.TextField(verbose_name="Текст", default="", blank=True, null=True)
    is_downloaded = models.BooleanField(verbose_name="Скачана", default=False)
    is_parsed = models.BooleanField(verbose_name="Обработана", default=False)
    is_incident_created = models.BooleanField(
        verbose_name="Инцидент создан", default=False
    )
    is_duplicate = models.BooleanField(verbose_name="Дубликат", default=False)
    rate = models.JSONField(verbose_name="Оценка релевантности", default=dict)
    incident = models.OneToOneField(
        MediaIncident,
        verbose_name="Инцидент",
        related_name="article",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    create_date = models.DateField("Дата создания", auto_now_add=True)
    publication_date = models.DateField("Дата публикации", null=True, blank=True)

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
        region = self.source.region if self.source else "ALL"
        return region

    @property
    def country(self):
        country = self.source.country if self.source else "RUS"
        return country

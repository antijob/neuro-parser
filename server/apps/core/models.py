# -*- coding: utf-8 -*-
import os
import datetime
import re
import uuid
import shutil

from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from htmldocx import HtmlToDocx
from io import BytesIO
import pdfkit

from server.apps.core.logic.banned_organizations import (
    annotate_banned_organizations
)
from server.apps.core.logic.documents import (
    date_in_words, format_dd_month_yyyy, format_if_date
)
from server.apps.core.logic.grabber import article_parser, source_parser
from server.apps.core.logic.grabber.classificator import (
    category, cosine, markers
)
from server.apps.core.logic.grabber.region import region_code
from server.apps.core.logic.morphy import normalize_text, normalize_words
from server.apps.core.incident_types import IncidentType
from server.apps.users.models import User
from server.apps.core.logic.reposts import check_repost


class BaseIncident(models.Model):
    UNPROCESSED = 0
    PROCESSED_AND_REJECTED = 1
    PROCESSED_AND_ACCEPTED = 2
    COMMUNICATION = 3
    IN_PROGRESS = 4
    COMPLETED = 5
    DELETED = 6
    STATUSES = [
        (UNPROCESSED, 'Не обработан'),
        (PROCESSED_AND_REJECTED, 'Отклонен'),
        (PROCESSED_AND_ACCEPTED, 'Принят'),
        (COMMUNICATION, 'Коммуникации'),
        (IN_PROGRESS, 'В работе'),
        (COMPLETED, 'Выполнен'),
        (DELETED, 'Удален'),
    ]
    ACTIVE_STATUSES = (PROCESSED_AND_ACCEPTED, COMMUNICATION, IN_PROGRESS,)
    PUBLIC_STATUSES = (PROCESSED_AND_ACCEPTED, COMPLETED)
    REGIONS = [
        ('RU', 'Россия'),
        ('RU-AMU', 'Амурская область'),
        ('RU-ARK', 'Архангельская область'),
        ('RU-AST', 'Астраханская область'),
        ('RU-BEL', 'Белгородская область'),
        ('RU-BRY', 'Брянская область'),
        ('RU-VLA', 'Владимирская область'),
        ('RU-VGG', 'Волгоградская область'),
        ('RU-VLG', 'Вологодская область'),
        ('RU-VOR', 'Воронежская область'),
        ('RU-IVA', 'Ивановская область'),
        ('RU-IRK', 'Иркутская область'),
        ('RU-KGD', 'Калининградская область'),
        ('RU-KLU', 'Калужская область'),
        ('RU-KEM', 'Кемеровская область'),
        ('RU-KIR', 'Кировская область'),
        ('RU-KOS', 'Костромская область'),
        ('RU-KGN', 'Курганская область'),
        ('RU-KRS', 'Курская область'),
        ('RU-LEN', 'Ленинградская область'),
        ('RU-LIP', 'Липецкая область'),
        ('RU-MAG', 'Магаданская область'),
        ('RU-MOS', 'Московская область'),
        ('RU-MUR', 'Мурманская область'),
        ('RU-NIZ', 'Нижегородская область'),
        ('RU-NGR', 'Новгородская область'),
        ('RU-NVS', 'Новосибирская область'),
        ('RU-OMS', 'Омская область'),
        ('RU-ORE', 'Оренбургская область'),
        ('RU-ORL', 'Орловская область'),
        ('RU-PNZ', 'Пензенская область'),
        ('RU-PSK', 'Псковская область'),
        ('RU-ROS', 'Ростовская область'),
        ('RU-RYA', 'Рязанская область'),
        ('RU-SAM', 'Самарская область'),
        ('RU-SAR', 'Саратовская область'),
        ('RU-SAK', 'Сахалинская область'),
        ('RU-SVE', 'Свердловская область'),
        ('RU-SMO', 'Смоленская область'),
        ('RU-TAM', 'Тамбовская область'),
        ('RU-TVE', 'Тверская область'),
        ('RU-TOM', 'Томская область'),
        ('RU-TUL', 'Тульская область'),
        ('RU-TYU', 'Тюменская область'),
        ('RU-ULY', 'Ульяновская область'),
        ('RU-CHE', 'Челябинская область'),
        ('RU-YAR', 'Ярославская область'),
        ('RU-AD', 'Республика Адыгея'),
        ('RU-BA', 'Республика Башкортостан'),
        ('RU-BU', 'Республика Бурятия'),
        ('RU-DA', 'Республика Дагестан'),
        ('RU-IN', 'Республика Ингушетия'),
        ('RU-KB', 'Кабардино-Балкарская Республика'),
        ('RU-KL', 'Республика Калмыкия'),
        ('RU-KC', 'Карачаево-Черкесская Республика'),
        ('RU-KR', 'Республика Карелия'),
        ('UA-43', 'Республика Крым'),
        ('RU-ME', 'Республика Марий Эл'),
        ('RU-MO', 'Республика Мордовия'),
        ('RU-AL', 'Республика Алтай'),
        ('RU-KO', 'Республика Коми'),
        ('RU-SA', 'Республика Саха (Якутия)'),
        ('RU-SE', 'Республика Северная Осетия — Алания'),
        ('RU-TA', 'Республика Татарстан'),
        ('RU-TY', 'Республика Тыва'),
        ('RU-UD', 'Удмуртская Республика'),
        ('RU-KK', 'Республика Хакасия'),
        ('RU-CE', 'Чеченская Республика'),
        ('RU-CU', 'Чувашская Республика'),
        ('RU-ALT', 'Алтайский край'),
        ('RU-ZAB', 'Забайкальский край'),
        ('RU-KAM', 'Камчатский край'),
        ('RU-KDA', 'Краснодарский край'),
        ('RU-KYA', 'Красноярский край'),
        ('RU-PER', 'Пермский край'),
        ('RU-PRI', 'Приморский край'),
        ('RU-STA', 'Ставропольский край'),
        ('RU-KHA', 'Хабаровский край'),
        ('RU-NEN', 'Ненецкий автономный округ'),
        ('RU-KHM', 'Ханты-Мансийский автономный округ — Югра'),
        ('RU-CHU', 'Чукотский автономный округ'),
        ('RU-YAN', 'Ямало-Ненецкий автономный округ'),
        ('RU-YEV', 'Еврейская автономная область'),
        ('RU-SPE', 'Санкт-Петербург'),
        ('RU-MOW', 'Москва'),
        ('UA-40', 'Севастополь'),
    ]

    title = models.TextField('Заголовок', null=True, blank=True)
    description = models.TextField('Описание', null=True, blank=True)
    status = models.IntegerField('Статус', choices=STATUSES, null=False, blank=False, default=UNPROCESSED)
    create_date = models.DateField('Дата создания', default=datetime.date.today)
    update_date = models.DateField('Дата обновления', auto_now=True)
    assigned_to = models.ForeignKey(
        User, verbose_name='Пользователь, назначенный на заявку',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )
    region = models.CharField('Регион', choices=REGIONS, default='RU', max_length=16)
    incident_type = models.ForeignKey(IncidentType, null=True, on_delete=models.CASCADE) # OnCascade?
    count = models.PositiveIntegerField('Количество ограничений', default=1)
    tags = ArrayField(models.CharField(max_length=32, blank=True, default='', null=True), blank=True, null=True)
    urls = ArrayField(models.URLField(blank=True, default='', null=True), blank=True, null=True)
    public_title = models.CharField('Публичное название', max_length=512, null=True, blank=True)
    public_description = models.TextField('Публичное описание', null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '[{}]'.format(self.any_title())

    def processed(self):
        return self.status != self.UNPROCESSED

    def processed_and_accepted(self):
        return self.status in self.ACTIVE_STATUSES

    def any_title(self):
        return (self.public_title or
                self.title or
                self.any_description()[:200] + '...')

    def any_description(self):
        if self.public_description:
            return self.public_description

        if self.description:
            return self.description
        return ''

    def status_color(self):
        try:
            return ['danger', 'warning', 'success',
                    'success', 'success', 'secondary'][self.status]
        except IndexError:
            return ''

    def apply_tag(self, tag):
        if self.tags and tag.name.lower() in self.tags:
            return
        if not tag.markers:
            return
        text = self.description or self.public_description or ''
        words = set(re.split(r'[^\w]', text))
        normalized_words = normalize_words(words)
        if not (set(normalized_words).intersection(tag.markers)):
            return
        if self.tags:
            self.tags.append(tag.name.lower())
        else:
            self.tags = [tag.name.lower()]
        self.save()

    def region_name(self):
        return dict(self.REGIONS).get(self.region)

    def category_name(self):
        return self.incident_type.description

    @classmethod
    def available_statuses(cls):
        available_statuses = list(cls.ACTIVE_STATUSES) + [cls.COMPLETED]
        return [(status, name)
                for status, name in cls.STATUSES
                if status in available_statuses]


class MediaIncident(BaseIncident):
    duplicate = models.ForeignKey('self',
                                  verbose_name='Дубликат',
                                  on_delete=models.SET_NULL,
                                  related_name='duplicates',
                                  null=True,
                                  blank=True)

    def get_absolute_url(self):
        return reverse('core:dashboard-mediaincident-update', args=[self.pk])

    def get_description(self):
        if self.public_description:
            return (
                self.public_description[150] + "..."
                if len(self.public_description) >= 160
                else self.public_description
            )
        return ''

    class Meta:
        verbose_name = 'Инцидент из СМИ'
        verbose_name_plural = 'Инциденты из СМИ'


class UserIncident(BaseIncident):
    form_data = models.JSONField('Данные из формы', null=True, blank=True)
    applicant_messenger = models.CharField(
        'Аккаунт в мессенджере', max_length=128, null=True, blank=True)
    applicant_email = models.CharField('Email', max_length=128)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def clean_form_data(self):
        data = {field["name"]: field["userData"][0]
                for field in self.form_data}
        return data

    def get_absolute_url(self):
        return reverse('core:dashboard-incident-update', args=[self.pk])

    class Meta:
        verbose_name = 'Инцидент'
        verbose_name_plural = 'Инциденты'


class UserIncidentFile(models.Model):
    file = models.FileField(upload_to="documents")
    incident = models.ForeignKey(UserIncident,
                                 on_delete=models.CASCADE,
                                 related_name='files')

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = 'Файлы инцидентов по заявкам'
        verbose_name_plural = 'Файл инцидента по заявке'


class MediaIncidentFile(models.Model):
    file = models.FileField(upload_to="documents")
    incident = models.ForeignKey(MediaIncident,
                                 on_delete=models.CASCADE,
                                 related_name='files')

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = 'Файлы инцидентов из СМИ'
        verbose_name_plural = 'Файл инцидента из СМИ'

class Source(models.Model):
    ALGORITHMS = [
        ('marker', 'По маркерам'),
        ('cosine', 'Косинусные расстояния'),
        # ('cossmi', 'Косинусные расстояния для СМИ'),
    ]
    DEFAULT_ALGORITHM = 'cosine'
    ALGORITHMS_MAP = {
        'marker': markers,
        'cosine': cosine,
    }
    url = models.TextField(verbose_name='URL списка новостей',
                           null=False,
                           unique=True)
    is_active = models.BooleanField(verbose_name='Активен', default=True)
    region = models.CharField('Регион',
                              choices=BaseIncident.REGIONS,
                              default='RU',
                              max_length=6)
    algorithm = models.CharField('Алгоритм оценки',
                                 choices=ALGORITHMS,
                                 default=DEFAULT_ALGORITHM,
                                 max_length=6)

    banned = models.BooleanField(
        'Запрещенная на территории РФ организация',
        default=False,
    )

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'

    def add_articles(self, urls):
        p = re.compile(r'https?\:\/\/(?P<url_without_method>.+)')
        added = []
        for url in urls:
            match = p.match(url)
            if not match:
                continue
            url_without_method = match.group('url_without_method')
            if Article.objects.filter(url__iendswith=url_without_method).exists():
                continue
            added += [Article.objects.create(url=url, source=self)]
        return added

    def update(self):
        urls = source_parser.extract_all_news_urls(self.url)
        if not urls:
            return
        self.add_articles(urls)
        self.save()

    def grab_archive(self, first_page_url=None, first_page=1):
        return source_parser.grab_archive(self, first_page_url, first_page)

    def __str__(self):
        return "Source [{}]".format(self.url)


class Article(models.Model):
    source = models.ForeignKey(Source,
                               verbose_name='Источник',
                               related_name='articles',
                               on_delete=models.DO_NOTHING,
                               null=True,
                               blank=True)
    url = models.TextField(verbose_name='URL', default='', blank=True)
    title = models.TextField(verbose_name='Заголовок', default='', blank=True)
    text = models.TextField(verbose_name='Текст', default='', blank=True)
    is_downloaded = models.BooleanField(verbose_name='Скачана', default=False)
    is_incident_created = models.BooleanField(verbose_name='Инцидент создан',
                                              default=False)
    is_duplicate = models.BooleanField(verbose_name='Дубликат', default=False)
    relevance = models.IntegerField(verbose_name='Оценка релевантности',
                                    null=True, blank=True)
    incident = models.OneToOneField(MediaIncident,
                                    verbose_name='Инцидент',
                                    related_name='article',
                                    null=True, blank=True,
                                    on_delete=models.SET_NULL)
    create_date = models.DateField('Дата создания', auto_now_add=True)
    publication_date = models.DateField('Дата публикации',
                                        null=True,
                                        blank=True)
    terms = ArrayField(models.CharField(max_length=32,
                                        blank=True,
                                        default='',
                                        null=True),
                       blank=True,
                       null=True)

    class Meta:
        verbose_name = 'Cтатья'
        verbose_name_plural = 'Статьи'

    def save(self, *args, **kwargs):
        self.title = self.title or self.text[:200]
        super().save(*args, **kwargs)

    def download(self):
        data = article_parser.get_article(self.url)
        if data:
            self.title, self.text, publication_date, self.url = data
            if publication_date:
                self.publication_date = publication_date
        self.is_downloaded = True
        if check_repost(self.text):
            self.is_duplicate = True
        self.save()

    def any_title(self):
        if self.title:
            return self.title
        first_sentence_end = self.text.index(".")
        if first_sentence_end > 20:
            return self.text[:first_sentence_end]
        return self.text[:200] + '...'

    def rate_relevance(self):
        is_duplicate = Article.objects.filter(text=self.text,
                                              pk__lt=self.pk).exists()
        if is_duplicate:
            self.relevance = -1
            self.save()
            return
        words = normalize_text(self.text)


        if not words:
            self.relevance = -1
        else:

            algorithm = (Source.ALGORITHMS_MAP.get(
                self.source.algorithm, 'cosine')
                         if self.source
                         else cosine)
            if(self.source.algorithm == 'cosine'):
                self.relevance = (
                        algorithm.rate(self.text) * settings.RELEVANCE_TRESHOLD)
            else:
                self.relevance = (
                        algorithm.rate(words) * settings.RELEVANCE_TRESHOLD)
        self.save()


    # ToDo: made self.incident field contain multiple incidents
    def create_incident(self):
        if self.is_incident_created:
            return self.incident
        if not self.text.strip():
            return
        normalized_text = normalize_text(self.text)
        incident_types = category.predict_incident_type(normalized_text)

        if not incident_types:
            return None

        region = self.source.region if self.source else 'RU'
        if region == 'RU':
            region = region_code("{} {}".format(self.title, self.text))
        public_title = self.any_title()
        annotated_title = annotate_banned_organizations(public_title)
        if annotated_title:
            public_title = annotated_title
        for incident_type in incident_types:
            self.incident = MediaIncident.objects.create(
                urls=[self.url],
                status=MediaIncident.UNPROCESSED,
                title=self.any_title(),
                public_title=public_title,
                create_date=self.publication_date or datetime.date.today(),
                description=self.text,
                public_description=self.text,
                incident_type=incident_type,
                region=region)
        self.is_incident_created = True
        self.save()
        return self.incident


class Tag(models.Model):
    name = models.CharField('Имя тега', max_length=32,
                            null=False, blank=False, unique=True)
    markers = ArrayField(models.CharField(max_length=32, blank=True, null=True),
                         verbose_name='Маркеры в тексте', blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Активен', default=True)
    create_date = models.DateField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def save(self, *args, **kwargs):
        self.markers = list(normalize_words(self.markers))
        super().save(*args, **kwargs)

    def apply(self):
        incidents = MediaIncident.objects.filter(
            Q(status__in=MediaIncident.ACTIVE_STATUSES) |
            Q(status=MediaIncident.UNPROCESSED))
        for incident in incidents:
            incident.apply_tag(self)
        incidents = UserIncident.objects.filter(
            Q(status__in=MediaIncident.ACTIVE_STATUSES) |
            Q(status=MediaIncident.UNPROCESSED))
        for incident in incidents:
            incident.apply_tag(self)

    def __str__(self):
        return 'Tag <{}>'.format(self.name)


class Post(models.Model):
    TITLE_ONLY = 0
    TITLE_BG_IMAGE = 1
    TITLE_IMAGE_DESCRIPTION = 2

    CARD_TYPE_CHOICES = [
        (TITLE_ONLY, 'По умолчанию (только название)'),
        (TITLE_BG_IMAGE, 'Название на фоне изображения'),
        (TITLE_IMAGE_DESCRIPTION, 'Название, изображение и описание'),
    ]

    BLUE = '#375ABB'
    MIRAGE = '#1B1F3B'
    GERALDINE = '#FB8F8A'

    CARD_COLOR_CHOICES = [
        (BLUE, 'Синий «Azure»'),
        (MIRAGE, 'Темный «Mirage»'),
        (GERALDINE, 'Светлый «Geraldine»'),
    ]

    title = models.CharField('Заголовок', max_length=250)
    text = RichTextUploadingField('Текст')
    author = models.ForeignKey(
        User, verbose_name='Автор',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )
    image = models.FileField(verbose_name="Картинка поста",
                             null=True,
                             blank=True, )
    create_date = models.DateTimeField('Дата создания', auto_now_add=True)
    publication_date = models.DateTimeField('Дата опубликования',
                                            default=datetime.datetime.now)

    card_type = models.IntegerField(
        verbose_name='Тип карточки',
        choices=CARD_TYPE_CHOICES,
        default=TITLE_ONLY,
    )
    color = models.CharField(
        verbose_name='Цвет карточки',
        max_length=12,
        choices=CARD_COLOR_CHOICES,
        default=BLUE,
        null=True,
        blank=True,
    )
    card_text = models.TextField('Текст на карточке', default='', blank=True)
    public = models.BooleanField('Опубликовать', default=False)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def get_absolute_url(self):
        return reverse('core:dashboard-post-update', args=[self.pk])

    def has_title_only(self):
        return self.card_type == self.TITLE_ONLY

    def has_title_and_bg_image(self):
        return self.card_type == self.TITLE_BG_IMAGE

    def has_title_and_description(self):
        return self.card_type == self.TITLE_IMAGE_DESCRIPTION

class Stage(models.Model):
    title = models.TextField("Заголовок")
    summary = models.TextField("Краткое описание")
    text = RichTextUploadingField('Текст')
    create_date = models.DateTimeField("Дата создания",
                                       default=timezone.now)

    def get_absolute_url(self):
        return reverse('core:dashboard-stage-form-update', kwargs={'pk': self.pk})


class Explanation(models.Model):
    title = models.TextField("Заголовок")
    text = models.TextField('Текст')
    emphasized = models.BooleanField("Выделенный", default=False)
    create_date = models.DateTimeField("Дата создания", auto_now_add=True)

    def get_absolute_url(self):
        return reverse('core:dashboard-explanation-form-update', kwargs={'pk': self.pk})


class DataLeak(models.Model):
    phone = models.CharField(max_length=12, null=False, blank=False, db_index=True)
    data = models.JSONField()
    def __str__(self):
        return f"{self.__class__.__name__} <{self.phone}>"

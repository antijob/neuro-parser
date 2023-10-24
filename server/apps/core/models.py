# -*- coding: utf-8 -*-
import datetime
import re
import time


from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from server.apps.core.logic.grabber import article_parser, source_parser
from server.apps.core.logic.grabber.classificator import (
    category
)
from server.apps.core.logic.grabber.region import region_code
from server.apps.core.logic.morphy import normalize_text
from server.apps.core.incident_types import IncidentType
from server.apps.users.models import User


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
    status = models.IntegerField(
        'Статус', choices=STATUSES, null=False, blank=False, default=UNPROCESSED)
    create_date = models.DateField('Дата создания', default=datetime.date.today)
    update_date = models.DateField('Дата обновления', auto_now=True)
    assigned_to = models.ForeignKey(
        User, verbose_name='Пользователь, назначенный на заявку',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )
    related_article = models.ForeignKey(
        'Article',
        verbose_name='Статья',
        related_name='articles',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )
    region = models.CharField('Регион', choices=REGIONS,
                              default='RU', max_length=16)
    incident_type = models.ForeignKey(
        IncidentType, null=True, on_delete=models.SET_NULL)
    count = models.PositiveIntegerField('Количество ограничений', default=1)
    urls = ArrayField(models.URLField(blank=True, default='',
                      null=True), blank=True, null=True)
    public_title = models.CharField(
        'Публичное название', max_length=512, null=True, blank=True)
    public_description = models.TextField(
        'Публичное описание', null=True, blank=True)

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


class Source(models.Model):

    url = models.TextField(verbose_name='URL списка новостей',
                           null=False,
                           unique=True)
    is_active = models.BooleanField(verbose_name='Активен', default=True)
    region = models.CharField('Регион',
                              choices=BaseIncident.REGIONS,
                              default='RU',
                              max_length=6)

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
            try:
                added += [Article.objects.create(url=url, source=self)]
            except Exception as e:
                raise type(e)(
                    f'When add_articles with {url} exception happend: ' + e)
        return added

    def update(self):
        urls = source_parser.extract_all_news_urls(self.url)
        if not urls:
            return 0
        added = self.add_articles(urls)
        self.save()
        return len(added)

    def grab_archive(self, first_page_url=None, first_page=1):
        return source_parser.grab_archive(self, first_page_url, first_page)

    def __str__(self):
        return "Source [{}]".format(self.url)


class Article(models.Model):
    source = models.ForeignKey(Source,
                               verbose_name='Источник',
                               related_name='articles',
                               on_delete=models.SET_NULL,
                               null=True,
                               blank=True)
    url = models.TextField(
        primary_key=True, verbose_name='URL', default='', blank=True)
    title = models.TextField(verbose_name='Заголовок',
                             default='', blank=True, null=True)
    text = models.TextField(verbose_name='Текст',
                            default='', blank=True, null=True)
    is_downloaded = models.BooleanField(verbose_name='Скачана', default=False)
    is_parsed = models.BooleanField(verbose_name='Обработана', default=False)
    is_incident_created = models.BooleanField(verbose_name='Инцидент создан',
                                              default=False)
    is_duplicate = models.BooleanField(verbose_name='Дубликат', default=False)
    rate = models.JSONField(
        verbose_name='Оценка релевантности', default=dict)
    incident = models.OneToOneField(MediaIncident,
                                    verbose_name='Инцидент',
                                    related_name='article',
                                    null=True, blank=True,
                                    on_delete=models.SET_NULL)
    create_date = models.DateField('Дата создания', auto_now_add=True)
    publication_date = models.DateField('Дата публикации',
                                        null=True,
                                        blank=True)

    class Meta:
        verbose_name = 'Cтатья'
        verbose_name_plural = 'Статьи'

    def save(self, *args, **kwargs):
        self.title = self.any_title()
        super().save(*args, **kwargs)

    def download(self):
        raw_data = article_parser.get_article(self.url)
        self.postprocess_raw_data(raw_data)

    def get_html_and_postprocess(self, data):
        postprocess_start_time = time.time()
        raw_data = article_parser.parse_article_raw_data(self.url, data)
        self.postprocess_raw_data(raw_data)
        postprocess_end_time = time.time()
        return postprocess_end_time - postprocess_start_time

    def postprocess_raw_data(self, data):
        if data:
            self.title, self.text, publication_date, self.url = data
            if publication_date:
                self.publication_date = publication_date
            else:
                self.publication_date = datetime.date.today()
        self.is_downloaded = True
        self.save()

    def any_title(self):
        if self.title:
            return self.title
        if not self.text:
            return ''

        try:
            first_sentence_end = self.text.index(".")
        except ValueError:
            first_sentence_end = 0

        if first_sentence_end > 20:
            return self.text[:first_sentence_end]
        if len(self.text) > 200:
            return self.text[:200] + '...'

        return self.text

    # ToDo: made self.incident field contain multiple incidents
    def create_incident(self, force=False):
        if self.is_incident_created and not force:
            return self.incident
        if not self.text or not self.text.strip():
            return
        normalized_text = normalize_text(self.text)
        incident_types = category.predict_incident_type(normalized_text, self)
        if not incident_types:
            return None

        region = self.source.region if self.source else 'RU'
        if region == 'RU':
            region = region_code("{} {}".format(self.title, self.text))
        public_title = self.any_title()
        for incident_type in incident_types:
            self.incident = MediaIncident.objects.create(
                urls=[self.url],
                status=MediaIncident.UNPROCESSED,
                title=self.any_title(),
                public_title=public_title,
                related_article=self,
                create_date=self.publication_date or datetime.date.today(),
                description=self.text,
                public_description=self.text,
                incident_type=incident_type,
                region=region)
        self.is_incident_created = True
        self.save()
        return self.incident

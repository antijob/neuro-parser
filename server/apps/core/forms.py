# -*- coding: utf-8 -*-

import re

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.conf import settings
from django.contrib.postgres.forms import SimpleArrayField
from django.core.mail import BadHeaderError, send_mail
from django.utils import formats

from server.apps.core.logic import notifier

from server.apps.core.models import (
    Campaign,
    CampaignPage,
    Document,
    Explanation,
    MediaIncident,
    Post,
    Stage,
    Tag,
    UserIncident,
    IncidentType)


class BootstrapDatePicker(forms.DateInput):
    format_re = re.compile(r'(?P<part>%[bBdDjmMnyY])')

    def __init__(self, attrs=None, format=None):
        final_attrs = {
            'data-provide': 'datepicker',
            'data-date-format': self.get_date_format(format=format),
            'data-date-autoclose': 'true',
        }
        if attrs is not None:
            classes = attrs.get('class', '').split(' ')
            classes.append('datepicker')
            attrs['class'] = ' '.join(classes)
            final_attrs.update(attrs)
        super().__init__(attrs=final_attrs, format=format)

    def get_date_format(self, format=None):
        format_map = {
            '%d': 'dd',
            '%j': 'd',
            '%m': 'mm',
            '%n': 'm',
            '%y': 'yy',
            '%Y': 'yyyy',
            '%b': 'M',
            '%B': 'MM',
        }
        if format is None:
            format = formats.get_format(self.format_key)[0]
        return re.sub(self.format_re, lambda x: format_map[x.group()], format)


class IncidentCreateForm(forms.ModelForm):
    region = forms.ChoiceField(
        label='', required=False,
        choices=UserIncident.REGIONS,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'placeholder': 'Регион',
            },
        ),
    )
    applicant_email = forms.EmailField(
        label='', required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Для обратной связи',
                'type': 'email',
            },
        ),
    )
    applicant_messenger = forms.CharField(
        label='', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            },
        ),
    )
    description = forms.CharField(
        label='',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Опишите проблему',
            },
        )
    )
    robot = forms.CharField(
        label='',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите "Нет"',
                'type': 'robot',
            },
        ),
    )
    count = forms.IntegerField(
        label='Количество нарушений', required=False, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserIncident
        fields = (
            'region',
            'applicant_email',
            'applicant_messenger',
            'description',
        )

    def send_slack_message(self):
        robot = self.cleaned_data.get('robot', "")
        email = self.cleaned_data.get('applicant_email')
        messanger = self.cleaned_data.get('applicant_messenger')
        description = self.cleaned_data.get('description')
        message = f'[DRI] Запрос обратной связи от {email}\n\n'
        message += f"{description}\n\n"

        if messanger is not None:
            message += f"Аккаунт в мессенджере: {messanger}"

        if robot.lower().strip() == 'нет':
            notifier.slack_message_legal_aid(message)


class UserIncidentUpdateForm(forms.ModelForm):
    public_title = forms.CharField(
        label='',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    public_description = forms.CharField(
        label='',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    create_date = forms.DateField(
        widget=BootstrapDatePicker(attrs={'class': 'form-control'}))

    incident_type = forms.ChoiceField(
        label='', required=False,
        choices=IncidentType.get_choices(),
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            },
        ),
    )

    count = forms.IntegerField(
        label='Количество нарушений', required=True, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    region = forms.ChoiceField(
        label='Регион',
        required=True,
        choices=UserIncident.REGIONS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = False

    class Meta:
        model = UserIncident
        fields = (
            'public_title',
            'public_description',
            'create_date',
            'incident_type',
            'region',
            'count',
            'tags',
            'form_data',
            'files',
            'status'
        )


class ContactForm(forms.Form):
    email = forms.EmailField(
        label='', required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ваш email',
                'type': 'email',
            },
        ),
    )
    message = forms.CharField(
        label='', required=True,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Сообщение',
            },
        ),
    )

    def send_email(self):
        from_email = self.cleaned_data['email']
        message = self.cleaned_data['message']
        subject = '[DRI] Запрос обратной связи от {}'.format(from_email)
        try:
            send_mail(subject, message, from_email, settings.CONTACT_FORM_EMAILS)
            return True
        except BadHeaderError:
            return False


class MediaIncidentCreateForm(forms.ModelForm):
    region = forms.ChoiceField(
        label='Регион', required=False,
        choices=MediaIncident.REGIONS,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            },
        ),
    )
    title = forms.CharField(
        label='Заголовок',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            },
        )
    )
    description = forms.CharField(
        label='Описание',
        required=True,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control'
            },
        )
    )
    tags = forms.CharField(
        label='Теги через запятую',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            },
        )
    )
    urls = forms.CharField(
        label='Ссылки через запятую',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            },
        )
    )
    incident_type = forms.ChoiceField(
        label='Категория', required=False,
        choices=IncidentType.get_choices(),
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            },
        ),
    )

    count = forms.IntegerField(
        label='Количество нарушений', required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    create_date = forms.DateField(
        label='Дата инцидента', required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'class': 'form-control'}))

    status = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = MediaIncident
        fields = (
            'title',
            'description',
            'region',
            'incident_type',
            'create_date',
            'tags',
            'urls',
            'count',
            'files',
            'status',
        )

    def clean_tags(self):
        string = self.cleaned_data['tags']
        return [tag.strip() for tag in string.split(',')]

    def clean_urls(self):
        string = self.cleaned_data['urls']
        return [url.strip() for url in string.split(',')]


class MediaIncidentUpdateForm(forms.ModelForm):
    region = forms.ChoiceField(
        label='', required=False,
        choices=UserIncident.REGIONS,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'placeholder': 'Регион',
            },
        ),
    )
    public_title = forms.CharField(
        label='',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок',
            },
        )
    )
    public_description = forms.CharField(
        label='',
        required=True,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Опишите проблему',
            },
        )
    )

    create_date = forms.DateField(
        widget=BootstrapDatePicker(attrs={'class': 'form-control'}))

    incident_type = forms.ChoiceField(
        label='Категория', required=False,
        choices=IncidentType.get_choices(),
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            },
        ),
    )

    count = forms.IntegerField(
        label='Количество нарушений', required=True, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    tags = SimpleArrayField(
        forms.CharField(),
        label='Теги через запятую',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            },
        )
    )

    urls = SimpleArrayField(
        forms.CharField(),
        label='Ссылки через запятую',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            },
        )
    )

    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = False

    class Meta:
        model = MediaIncident
        fields = (
            'public_title',
            'public_description',
            'region',
            'incident_type',
            'create_date',
            'tags',
            'urls',
            'count',
            'status',
            'files',
        )


class CampaignForm(forms.ModelForm):
    # Warning: form_json is JSONField and should not be overrided

    name = forms.CharField(
        label='', required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Название'
            },
        )
    )

    description = forms.CharField(
        label='Описание', required=True,
        widget=CKEditorWidget()
    )

    slug = forms.CharField(
        label='', required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Название в URL'
            },
        )
    )

    document = forms.CharField(
        label='Документ', required=False,
        widget=CKEditorWidget()
    )

    instruction = forms.CharField(
        label='Инструкция', required=False,
        widget=CKEditorWidget()
    )

    generate = forms.BooleanField(required=False)

    chart_field = forms.CharField(
        label='', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    chart_description = forms.CharField(
        label='', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    applicant_messenger_required = forms.BooleanField(required=False)
    description_required = forms.BooleanField(required=False)
    files_required = forms.BooleanField(required=False)

    form_title = forms.CharField(
        label='', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    form_description = forms.CharField(
        label='', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )

    notify_email = forms.CharField(
        label='', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'email'})
    )

    reply_email_text = forms.CharField(
        label='', required=False,
        widget=CKEditorWidget()
    )

    background_color = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'color'})
    )

    text_color = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'color'})
    )

    thanks_header = forms.CharField(
        label='Заголовок спасибо-страницы',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    thanks_text = forms.CharField(
        label='Текст спасибо-страницы', required=False,
        widget=CKEditorWidget()
    )

    class Meta:
        model = Campaign
        fields = ['document', 'instruction', 'slug', 'description', 'name',
                  'form_json', 'picture', 'is_background', 'public', 'generate',
                  'chart_field', 'chart_description',
                  'applicant_messenger_required', 'description_required',
                  'files_required', 'form_title', 'notify_email',
                  'send_reply_email',
                  'reply_email_text', 'reply_email_image', 'form_description',
                  'background_color', 'text_color', 'submit_button_text',
                  'use_custom_thanks', 'thanks_text', 'thanks_header'
                  ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "instance" in kwargs and hasattr(kwargs["instance"], "document"):
            instance = kwargs["instance"]
            self.fields["document"].initial = (
                Document.objects.get(pk=instance.document.pk).template)
            self.fields["instruction"].initial = (
                Document.objects.get(pk=instance.document.pk).instruction)


class CampaignIncidentForm(forms.ModelForm):
    description = forms.CharField(
        label='Описание', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    count = forms.CharField(
        label='Количество нарушений', required=False, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    region = forms.ChoiceField(
        label='Регион', required=False, choices=UserIncident.REGIONS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    applicant_email = forms.CharField(
        label='Email', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'email'})
    )

    applicant_messenger = forms.CharField(
        label='Аккаунт в мессенджере', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'class': 'form-control'})
    )

    class Meta:
        model = UserIncident
        fields = (
            'description',
            'count',
            'region',
            'applicant_email',
            'applicant_messenger',
            'form_data',
            'files',
        )


class UserIncidentCreateForm(forms.ModelForm):
    public_title = forms.CharField(
        label='Публичный заголовок', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    public_description = forms.CharField(
        label='Публичное описание', required=True,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    incident_type = forms.ChoiceField(
        label='Категория', required=False,
        choices=IncidentType.get_choices(),
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            },
        ),
    )

    count = forms.IntegerField(
        label='Количество нарушений', required=True, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    region = forms.ChoiceField(
        label='Регион', required=True, choices=UserIncident.REGIONS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    create_date = forms.DateField(
        label='Дата инцидента', required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    tags = SimpleArrayField(
        forms.CharField(),
        label='Теги через запятую',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            },
        )
    )

    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'class': 'form-control'})
    )
    status = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = UserIncident
        fields = (
            'public_title',
            'public_description',
            'region',
            'incident_type',
            'count',
            'tags',
            'files',
            'create_date',
            'status',
        )


class TagForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    markers = SimpleArrayField(
        forms.CharField(max_length=32),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    is_active = forms.BooleanField(required=False)

    class Meta:
        model = Tag
        fields = '__all__'


class PostForm(forms.ModelForm):
    title = forms.CharField(
        label='Заголовок',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    text = forms.CharField(
        label='Текст',
        required=True,
        widget=CKEditorWidget()
    )
    card_type = forms.ChoiceField(
        label='Тип карточки', required=False,
        choices=Post.CARD_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    color = forms.ChoiceField(
        label='Цвет карточки', required=False,
        choices=Post.CARD_COLOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    card_text = forms.CharField(
        label='Текст для карточки',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    public = forms.BooleanField(
        label='Опубликовать',
        required=False
    )

    class Meta:
        model = Post
        exclude = ['author', 'publication_date', ]


class StageForm(forms.ModelForm):
    title = forms.CharField(
        label='Заголовок',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    summary = forms.CharField(
        label='Текст карточки',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows': 2})
    )
    text = forms.CharField(
        label='Текст',
        widget=CKEditorWidget()
    )

    class Meta:
        model = Stage
        fields = ["title", "summary", "text"]


class ExplanationForm(forms.ModelForm):
    title = forms.CharField(
        label='Заголовок',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    text = forms.CharField(
        label='Текст',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Explanation
        fields = ["title", "text", "emphasized"]


class CampaignPageForm(forms.ModelForm):
    campaign = forms.ModelChoiceField(
        queryset=None,
        empty_label="- Выберите кампанию -",
        label='Кампания',
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            },
        ),
    )
    title = forms.CharField(
        label='Заголовок',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    slug = forms.CharField(
        label='Название в url',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    text = forms.CharField(
        label='Текст',
        required=True,
        widget=CKEditorWidget()
    )
    public = forms.BooleanField(
        label='Опубликовать',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['campaign'].queryset = Campaign.objects.filter()

    class Meta:
        model = CampaignPage
        fields = ["campaign", "title", "slug", "text", "public"]

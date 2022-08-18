# -*- coding: utf-8 -*-

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin

from server.apps.core.models import (
    Article,
    Campaign,
    CampaignPage,
    Document,
    Explanation,
    MediaIncident,
    MediaIncidentFile,
    Post,
    Source,
    Stage,
    Tag,
    UserIncident,
    UserIncidentFile,
)

admin.site.register(Campaign)
admin.site.register(CampaignPage)
admin.site.register(Explanation)
admin.site.register(MediaIncidentFile)
admin.site.register(Stage)
admin.site.register(Tag)
admin.site.register(UserIncidentFile)
admin.site.register(Document)


@admin.register(MediaIncident)
class MediaIncidentAdmin(admin.ModelAdmin):
    list_display = ('any_title', 'status')


@admin.register(UserIncident)
class UserIncidentAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)
    list_display = ('any_title', 'status')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_downloaded', 'title', 'relevance')


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('url', 'region', 'is_active')


class PostAdminForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = '__all__'


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'create_date', 'public')
    ordering = ['-create_date']


admin.site.register(Post, PostAdmin)

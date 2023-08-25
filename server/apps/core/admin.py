# -*- coding: utf-8 -*-

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin

from server.apps.core.models import (
    Article,
    Explanation,
    MediaIncident,
    MediaIncidentFile,
    Post,
    Source,
    Stage,
    Tag,
    IncidentType,
    UserIncident,
    UserIncidentFile,
)
admin.site.register(Explanation)
admin.site.register(MediaIncidentFile)
admin.site.register(Stage)
admin.site.register(Tag)
admin.site.register(UserIncidentFile)

@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display = ('description', 'zip_file')

    actions=['really_delete_selected']

    def get_actions(self, request):
        actions = super(IncidentTypeAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 IncidentType entry was"
        else:
            message_bit = "%s IncidentTypes entries were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)
    really_delete_selected.short_description = "Delete selected entries"


@admin.register(MediaIncident)
class MediaIncidentAdmin(admin.ModelAdmin):
    list_display = ('any_title', 'status')


@admin.register(UserIncident)
class UserIncidentAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)
    list_display = ('any_title', 'status')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('url', 'publication_date', 'is_downloaded', 'is_duplicate', 'title', 'relevance')


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('url', 'region', 'is_active')

    def save_model(self, request, obj, form, change):
        urls = obj.url.split()
        for url in urls:
            if not url:
                continue
            if Source.objects.filter(url=url).exists():
                continue

            new_source = Source(
                url=url,
                is_active=obj.is_active,
                region=obj.region,
                algorithm=obj.algorithm,
                banned=obj.banned
            )
            new_source.save()


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

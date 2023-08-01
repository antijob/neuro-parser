import os
import shutil

# from django.conf import settings
from django.db import models
from django.core.files.storage import FileSystemStorage, default_storage

# from server.apps.core.logic.grabber.classificator import (
#     category, cosine, markers
# )
from server.apps.core.logic.files import unpack_file, extract_filename_without_extension, validate_file_extension

from server.settings.components.common import BASE_DIR


# should be complex logig? override only files from this IncidentType?
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class IncidentType(models.Model):
    zip_dir   = 'models_archives' # inside settings.MEDIA_ROOT
    model_dir = BASE_DIR.joinpath('server', 'apps',
                    'core', 'logic', 'grabber', 'classificator', 'data')

    description = models.CharField('Вид ограничения', max_length=128, null=True, blank=True)
    zip_file = models.FileField('Архив с моделью', 
                    help_text = "архивы .zip, .tar, .tar.gz",
                    upload_to=zip_dir, 
                    null=True, blank=True, 
                    storage=OverwriteStorage(), 
                    validators=[validate_file_extension])


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = None
        self.model = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Unpack the uploaded file
        if self.zip_file:
            file_path = self.zip_file.path

            # assume that unpacked directory has the same name
            unpack_file(file_path, self.model_dir)

    def delete(self, *args, **kwargs):
        file_name = extract_filename_without_extension(self.zip_file.name)
        unpacked_files_path = self.model_dir.joinpath(file_name)

        if os.path.exists(unpacked_files_path):
            shutil.rmtree(unpacked_files_path)

        if self.zip_file:
            storage_path = self.zip_file.path
            if default_storage.exists(storage_path):
                default_storage.delete(storage_path)

        super().delete(*args, **kwargs)

    def get_tokenizer(self):
        if self.tokenizer is None:
            from transformers import AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir.joinpath(self.zip_file.name), use_fast=False)
        return self.tokenizer

    def get_model(self):
        if self.model is None:
            from transformers import BertForSequenceClassification
            self.model = BertForSequenceClassification.from_pretrained(self.model_dir.joinpath(self.zip_file.name))
            self.model.eval()
        return self.model

    @classmethod
    def types_list(cls):
        return [(it.id, it.description) for it in cls.objects.all()]

    @classmethod
    def get_choices(cls):
        return [(incident_type.id, incident_type.description) for incident_type in cls.objects.all()]

    def __str__(self):
        return str(self.description)

    class Meta:
        verbose_name = 'Тип инцидента'
        verbose_name_plural = 'Типы инцидентов'

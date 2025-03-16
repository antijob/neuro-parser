import os

from django import forms

from server.settings.components.common import MODELS_DIR

from .models import IncidentType, Source


class IncidentTypeForm(forms.ModelForm):
    class Meta:
        model = IncidentType
        fields = "__all__"

    model_path = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["model_path"].choices = self.get_model_folders()

    def get_model_folders(self):
        try:
            folders = [
                (folder, folder)
                for folder in os.listdir(MODELS_DIR)
                if os.path.isdir(os.path.join(MODELS_DIR, folder))
            ]
        except Exception as _:
            folders = []

        folders.insert(0, ("", "Без модели"))
        return folders


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get("country")
        region = cleaned_data.get("region")
        if region is None:
            return
        elif country != region.country:
            self.add_error("region", "Регион и страна не соответствуют друг другу")
        
        # Validate that public_tg_channel_link is provided when is_telethon is True
        is_telethon = cleaned_data.get("is_telethon")
        public_tg_channel_link = cleaned_data.get("public_tg_channel_link")
        if is_telethon and not public_tg_channel_link:
            self.add_error("public_tg_channel_link", "Это поле обязательно, если включен парсинг через телетон.")

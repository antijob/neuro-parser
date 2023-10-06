import os

from django import forms
from .models import IncidentType
from server.settings.components.common import MODELS_DIR


class IncidentTypeForm(forms.ModelForm):
    class Meta:
        model = IncidentType
        fields = '__all__'

    model_path = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model_path'].choices = self.get_model_folders()

    def get_model_folders(self):
        try:
            folders = [(folder, folder) for folder in os.listdir(MODELS_DIR) if os.path.isdir(os.path.join(MODELS_DIR, folder))]
        except Exception as e:
            folders = [] 

        folders.insert(0, ('', 'Без модели'))
        return folders

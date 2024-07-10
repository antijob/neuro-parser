from django import forms
from django.forms import Textarea
from .models import ChannelCountry


class ChannelCountryForm(forms.ModelForm):
    class Meta:
        model = ChannelCountry
        fields = "__all__"
        widgets = {"enabled_regions": Textarea(attrs={"rows": 10, "cols": 80})}

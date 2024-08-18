from django import forms
from django.forms import Textarea, widgets

from .models import Channel, ChannelCountry


# Bigger Textarea for regions field
class ChannelCountryForm(forms.ModelForm):
    class Meta:
        model = ChannelCountry
        fields = "__all__"
        widgets = {"enabled_regions": Textarea(attrs={"rows": 10, "cols": 80})}


# Form for sending messages to chats
class BroadcastForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    channels = forms.ModelMultipleChoiceField(
        queryset=Channel.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        selected_channels = kwargs.pop("selected_channels", None)
        super(BroadcastForm, self).__init__(*args, **kwargs)
        if selected_channels:
            self.fields["channels"].initial = selected_channels

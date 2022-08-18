from django import forms
from django.db.models import Count
from django.utils import timezone
from tracking.models import Pageview


class BootstrapDateInput(forms.DateInput):
    def __init__(self, attrs=None, *args, **kwargs):
        super().__init__({"type": "date", "class": "form-control"})


class DashboardForm(forms.Form):
    """
    Filter form for dashboard page
    """

    start = forms.DateField(required=False, widget=BootstrapDateInput())
    end = forms.DateField(required=False, widget=BootstrapDateInput())
    url = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={"class": "form-control"})
    )

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

        # set default values for dates
        today = timezone.now().date()
        if not self.cleaned_data["start"]:
            self.cleaned_data["start"] = today
        if not self.cleaned_data["end"]:
            self.cleaned_data["end"] = today

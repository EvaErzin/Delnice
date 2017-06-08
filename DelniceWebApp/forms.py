from .models import *
from django.forms import ModelForm, DateField, DateInput


class PortfolioForm(ModelForm):
    datum = DateField(widget=DateInput(attrs={'class': 'datepicker'}))

    class Meta:
        model = Portfolio
        fields = ['simbol', 'datum', 'vrednost', 'kolicina']


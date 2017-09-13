from .models import *
from django.forms import ModelForm, DateField, DateInput, ModelChoiceField, Select, CharField, FloatField, NumberInput
from django.utils.translation import ugettext_lazy as _

class PortfolioForm(ModelForm):
    datum = DateField(widget=DateInput(attrs={'class': 'datepicker form-control'}),label=_('Datum'))
    simbol = ModelChoiceField(widget=Select(attrs={'class':'form-control'}),label=_('Simbol'),queryset=Podjetje.objects.all())
    vrednost = FloatField(widget=NumberInput(attrs={'class': 'form-control'}),label=_('Vrednost'))
    kolicina = FloatField(widget=NumberInput(attrs={'class': 'form-control'}),label=_('Količina'))

    class Meta:
        model = Portfolio
        fields = ['simbol', 'datum', 'vrednost', 'kolicina']


from .models import *
import django_tables2 as tables
from django_tables2.utils import A
from django.utils.translation import ugettext_lazy as _

class PortfolioTabela(tables.Table):
    simbol = tables.LinkColumn('portfolioDetailed', text= lambda record: record['simbol'], args=[A('simbol')], verbose_name=_('Simbol'))
    kolicinaSkupaj = tables.Column(verbose_name=_('Skupaj kupljeno'))

    class Meta:
        model = Portfolio
        attrs = {'class': 'mytable', 'span': 'true'}
        fields = ('simbol', 'kolicinaSkupaj')

class PortfolioTabela1(tables.Table):

    class Meta:
        model = Portfolio
        attrs = {'class': 'mytable', 'span': 'true'}
        fields = ('datum', 'vrednost', 'kolicina')

    def render_vrednost(self, value):
        return round(value, 3)
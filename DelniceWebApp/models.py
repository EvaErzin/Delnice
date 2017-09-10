from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class Podjetje(models.Model):
    simbol = models.CharField(max_length=8, verbose_name=_('Simbol'), primary_key=True)
    polnoIme = models.TextField(verbose_name=_('Polno ime'))
    lokacija = models.TextField(verbose_name=_('Lokacija'))
    sektor = models.TextField(verbose_name=_('Sektor'))
    industrija = models.TextField(verbose_name=_('Industrija'))
    ipo = models.TextField(verbose_name=_('IPO'))

    def __str__(self):
        return self.simbol

class PoslovniPodatki(models.Model):
    simbol = models.ForeignKey(Podjetje, verbose_name=_('Simbol'))
    leto = models.IntegerField(verbose_name=_('Leto'))
    cetrtletje = models.IntegerField(verbose_name=_('Četrtletje'))
    promet = models.FloatField(verbose_name=_('Promet'))
    dobicek = models.FloatField(verbose_name=_('Dobicek'))

    class __Meta__:
        unique_together = ('simbol', 'leto', 'cetrtletje')

    def __str__(self):
        return self.simbol

class Delnica(models.Model):
    simbol = models.ForeignKey(Podjetje, verbose_name=_('Simbol'), db_index=True)
    datum = models.DateField(db_index=True,verbose_name=_('Datum'))
    odpiralniTecaj = models.FloatField(verbose_name=_('Odpiralni tečaj'))
    zapiralniTecaj = models.FloatField(verbose_name=_('Zapiralni tečaj'))
    nepopravljenZapiralniTecaj = models.FloatField(verbose_name=_('Nepopravjen zapiralni tečaj'))
    volumenTrgovanja = models.BigIntegerField(verbose_name=_('Volumen trgovanja'))
    steviloDelnic = models.BigIntegerField(verbose_name=_('Število vseh delnic'))

    class __Meta__:
        unique_together = ('simbol', 'datum')

    def __str__(self):
        return self.simbol

class Dividenda(models.Model):
    simbol = models.ForeignKey(Podjetje, verbose_name=_('Simbol'))
    datum = models.DateField(verbose_name=_('Datum'))
    vrednost = models.FloatField(verbose_name=_('Vrednost'))

    class __Meta__:
        unique_together = ('simbol', 'datum')

    def __str__(self):
        return self.simbol

class Portfolio(models.Model):
    uporabnik = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Uporabnik'))
    simbol = models.ForeignKey(Podjetje, verbose_name=_('Simbol'), db_index=True)
    datum = models.DateField(verbose_name=_('Datum'), db_index=True)
    vrednost = models.FloatField(verbose_name=_('Vrednost'))
    kolicina = models.BigIntegerField(verbose_name=_('Količina'))

    def __str__(self):
        return self.simbol

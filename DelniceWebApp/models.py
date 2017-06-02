from django.db import models
from django.conf import settings

class Podjetje(models.Model):
    simbol = models.CharField(max_length=8, verbose_name='Simbol', primary_key=True)
    polnoIme = models.TextField(verbose_name='Polno ime')
    lokacija = models.TextField(verbose_name='Lokacija')
    sektor = models.TextField(verbose_name='Sektor')
    industrija = models.TextField(verbose_name='Industrija')
    ipo = models.TextField(verbose_name='IPO')

class PoslovniPodatki(models.Model):
    simbol = models.ForeignKey(Podjetje, verbose_name='Simbol')
    leto = models.IntegerField(verbose_name='Leto')
    cetrtletje = models.IntegerField(verbose_name='Četrtletje')
    promet = models.FloatField(verbose_name='Promet')
    dobicek = models.FloatField(verbose_name='Dobicek')

    class __Meta__:
        unique_together = ('simbol', 'leto', 'cetrtletje')

class Delnica(models.Model):
    simbol = models.ForeignKey(Podjetje, verbose_name='Simbol')
    datum = models.DateField(verbose_name='Datum')
    odpiralniTecaj = models.FloatField(verbose_name='Odpiralni tečaj')
    zapiralniTecaj = models.FloatField(verbose_name='Zapiralni tečaj')
    nepopravljenZapiralniTecaj = models.FloatField(verbose_name='Nepopravjen zapiralni tečaj')
    volumenTrgovanja = models.IntegerField(verbose_name='Volumen trgovanja')
    steviloDelnic = models.IntegerField(verbose_name='Število vseh delnic')

    class __Meta__:
        unique_together = ('simbol', 'datum')

class Dividenda(models.Model):
    simbol = models.ForeignKey(Podjetje, verbose_name='Simbol')
    datum = models.DateField(verbose_name='Datum')
    vrednost = models.FloatField(verbose_name='Vrednost')

    class __Meta__:
        unique_together = ('simbol', 'datum')

class Portfolio(models.Model):
    uporabnik = models.ForeignKey(settings.AUTH_USER_MODEL)
    simbol = models.ForeignKey(Podjetje, verbose_name='Simbol')
    datum = models.DateField(verbose_name='Datum')
    vrednost = models.FloatField(verbose_name='Vrednost')
    kolicina = models.IntegerField(verbose_name='Količina')



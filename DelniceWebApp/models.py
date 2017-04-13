from django.db import models
from django.conf import settings

class Podjetje(models.Model):
    simbol = models.CharField(max_length=4, verbose_name='Simbol', primary_key=True)
    polno_ime = models.TextField(verbose_name='Polno ime')
    lokacija = models.TextField(verbose_name='Lokacija')
    panoga = models.TextField(verbose_name='Panoga')
    ipo = models.DateField(verbose_name='IPO')

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
    odpiralni_tecaj = models.FloatField(verbose_name='Odpiralni tečaj')
    uradni_tecaj = models.FloatField(verbose_name='Uradni tečaj')

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



from django.core.management.base import BaseCommand, CommandError
from DelniceWebApp.models import *
import urllib.request as urre
from bs4 import BeautifulSoup
import re
from datetime import date


class Command(BaseCommand):

    def handle(self, *args, **options):

        for podjetje in Podjetje.objects.all():
            podatki = PoslovniPodatki.objects.filter(simbol=podjetje)
            if podatki.count() == 3:
                for podatek in podatki:
                    podatek.cetrtletje = 0
                    podatek.save()
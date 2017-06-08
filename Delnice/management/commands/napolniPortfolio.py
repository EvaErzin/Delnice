from DelniceWebApp.models import *
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from datetime import date, timedelta
import random


class Command(BaseCommand):

    def handle(self, *args, **options):

        u = User.objects.get(username='eva')
        for podjetje in Podjetje.objects.all()[:10]:
            i = random.randint(0, 150)
            vr = random.random()*100
            datum = date.today() - timedelta(days=3)
            p = Portfolio(uporabnik=u, simbol=podjetje, kolicina=i, vrednost=vr, datum=datum)
            p.save()



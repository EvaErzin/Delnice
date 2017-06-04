from django.core.management.base import BaseCommand, CommandError
from DelniceWebApp.models import *
import urllib.request
import re
class Command(BaseCommand):

    def handle(self, *args, **options):
        pattern = re.compile(
            r'"researchDevelopment".*?"grossProfit":.*?"raw":(?P<profit>\d+?),.*?"endDate".*?"fmt":"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})".*?totalRevenue":{"raw":(?P<revenue>\d+?),'
        )


        for podjetje in Podjetje.objects.all():
            simbol = podjetje.simbol
            print(simbol)
            (filename, header) = urllib.request.urlretrieve('https://finance.yahoo.com/quote/{}/financials?p={}'.format(simbol, simbol))
            with open(filename, encoding='utf8') as f:
                content = f.read()
                result = re.finditer(pattern, content)
            f.close()


            for r in result:
                d = r.groupdict()
                year = int(d['year'])
                month = int(d['month'])
                if year < 2016 and podjetje.simbol != "BABA":
                    q = 0
                elif month <= 4:
                    q = 1
                elif month <= 7:
                    q = 2
                elif month <= 9:
                    q = 3
                else:
                    q = 4
                prft = int(d['profit'])
                rvn = int(d['revenue'])
                print(simbol, prft, rvn, year, q)
                try:
                    bd = PoslovniPodatki.objects.get(simbol=podjetje,leto=year,cetrtletje=q)
                    if bd:
                        bd = PoslovniPodatki()
                        bd.simbol = podjetje
                        bd.dobicek = prft
                        bd.promet = rvn
                        bd.leto = year
                        bd.cetrtletje = 0
                        bd.save()
                except PoslovniPodatki.DoesNotExist:
                    bd = PoslovniPodatki()
                    bd.simbol = podjetje
                    bd.dobicek = prft
                    bd.promet = rvn
                    bd.leto = year
                    bd.cetrtletje = q
                    bd.save()

            print('Done')
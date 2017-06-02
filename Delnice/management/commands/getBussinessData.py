from django.core.management.base import BaseCommand, CommandError
from DelniceWebApp.models import *
import urllib.request
import re
class Command(BaseCommand):

    def handle(self, *args, **options):
        pattern = re.compile(
            r'"date":"(?P<date>\dQ201\d)","revenue":{"raw":.*?"longFmt":"(?P<revenue>.*?)"'
        )
        pattern1 = re.compile(
            r'"grossProfit":.*?"longFmt":"(?P<profit4q>.+?)".*?"grossProfit":.*?"longFmt":"(?P<profit3q>.+?)".*?"grossProfit":.*?"longFmt":"(?P<profit2q>.+?)".*?"grossProfit":.*?"longFmt":"(?P<profit1q>.+?)".*?'
        )

        for podjetje in Podjetje.objects.all():
            simbol = podjetje.simbol
            (filename, header) = urllib.request.urlretrieve('https://finance.yahoo.com/quote/{}/financials?p={}'.format(simbol, simbol))
            with open(filename, encoding='utf8') as f:
                content = f.read()
                result = re.finditer(pattern, content)
                result1 = re.finditer(pattern1, content)
            f.close()


            for r in result1:
                profits = r.groupdict()
                break


            for r in result:
                d = r.groupdict()
                date = d['date']
                [q, year] = map(int, date.split('Q'))
                rvn = d['revenue']
                prft = profits['profit{}q'.format(q)]
                bd = PoslovniPodatki()
                bd.simbol = podjetje
                bd.dobicek = prft
                bd.promet = rvn
                bd.leto = year
                bd.cetrtletje = q
                bd.save()

            print('Done')
            return
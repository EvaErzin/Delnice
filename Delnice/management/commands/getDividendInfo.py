from django.core.management.base import BaseCommand
from DelniceWebApp.models import *
import urllib.error
import yahoo_quote_download.yahoo_quote_download.yqd as yqd
from datetime import date, timedelta

class Command(BaseCommand):

    def  handle(self, *args, **options):

        for podjetje in Podjetje.objects.all():
            symbol = podjetje.simbol
            try:
                startDate = Dividenda.objects.filter(simbol=podjetje).latest('datum').datum + timedelta(days=1)
                startDate = startDate.isoformat().replace('-','')
            except:
                startDate = '20100101'
            endDate = date.today().isoformat().replace('-','')

            while True:
                try:
                    dividends = yqd.load_yahoo_quote(symbol, startDate, endDate, info='dividend')[1:]
                    break
                except urllib.error.HTTPError:
                    continue

            for result in dividends:
                if result != '':
                    result = result.split(',')
                    datum = result[0].split('-')
                    datum = date(year=int(datum[0]), month=int(datum[1]), day=int(datum[2]))
                    value = float(result[1])
                    d = Dividenda(simbol=podjetje, vrednost=value, datum=datum)
                    d.save()

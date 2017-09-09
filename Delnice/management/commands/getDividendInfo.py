from django.core.management.base import BaseCommand
from DelniceWebApp.models import *
import urllib.error
import yahoo_quote_download.yahoo_quote_download.yqd as yqd
from datetime import date, timedelta

class Command(BaseCommand):

    def  handle(self, *args, **options):

        i = 1
        for podjetje in Podjetje.objects.all():
            symbol = podjetje.simbol
            print('Starting {}'.format(symbol))
            try:
                startDate = Dividenda.objects.filter(simbol=podjetje).latest('datum').datum + timedelta(days=1)
                startDate = startDate.isoformat().replace('-','')
            except:
                startDate = '20150101'
            endDate = date.today().isoformat().replace('-','')

            j = 1
            while True:
                try:
                    dividends = yqd.load_yahoo_quote(symbol, startDate, endDate, info='dividend')[1:]
                    break
                except urllib.error.HTTPError:
                    if j == 5:
                        print('Could not load yahoo finance share for {}'.format(symbol))
                        break
                    j += 1

            for result in dividends:
                if result != '':
                    result = result.split(',')
                    datum = result[0].split('-')
                    datum = date(year=int(datum[0]), month=int(datum[1]), day=int(datum[2]))
                    value = float(result[1])
                    d = Dividenda(simbol=podjetje, vrednost=value, datum=datum)
                    d.save()

            print('Finished {} out of 100.'.format(i))
            i+=1

from django.core.management.base import BaseCommand, CommandError
from DelniceWebApp.models import *
import urllib.request as urre
from bs4 import BeautifulSoup
import re
from datetime import date

class Command(BaseCommand):

    def  handle(self, *args, **options):

        for podjetje in Podjetje.objects.all():
            simbol = podjetje.simbol
            resp = urre.urlopen('http://www.nasdaq.com/symbol/{}/dividend-history'.format(simbol))
            cont = resp.read()
            soup = BeautifulSoup(cont, 'html.parser')
            table = soup.findAll('tbody')[1]
            table = str(table)
            reg = r'<span id="quotes_content_left_dividendhistoryGrid_exdate_\d+?">(?P<exdate>\d{1,2}/\d{1,2}/\d{4})</span>\s*?</td><td>.*?</td><td>\s*?<span id="quotes_content_left_dividendhistoryGrid_CashAmount_\d+?">(?P<cash>\d+?\.\d+?)</span>'
            regex = re.compile(reg)
            results = re.finditer(regex, table)
            for result in results:
                gd = result.groupdict()
                dat = gd['exdate'].split('/')
                datum = date(day=dat[1], month=dat[0], year=dat[2])
                vrednost = gd['cash']
                div = Dividenda(simbol = podjetje, datum=datum, vrednost=vrednost)
                div.save()

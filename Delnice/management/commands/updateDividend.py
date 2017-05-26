from django.core.management.base import BaseCommand, CommandError
from DelniceWebApp.models import *
import urllib.request as urre
from bs4 import BeautifulSoup
import re
from datetime import date


class Command(BaseCommand):

    def handle(self, *args, **options):

        for podjetje in Podjetje.objects.all():
            simbol = podjetje.simbol
            resp = urre.urlopen('http://www.nasdaq.com/symbol/{}/dividend-history'.format(simbol))
            cont = resp.read()
            soup = BeautifulSoup(cont, 'html.parser')
            table = soup.findAll('tbody')[1]
            table = str(table)
            reg = r'<span id="quotes_content_left_dividendhistoryGrid_exdate_\d+?">(?P<exdate>\d{1,2}/\d{1,2}/\d{4})</span>\s*?</td><td>.*?</td><td>\s*?<span id="quotes_content_left_dividendhistoryGrid_CashAmount_\d+?">(?P<cash>\d+?\.\d+?)</span>'
            regex = re.compile(reg)
            results = re.search(regex, table)
            dat = results['exdate'].split('/')
            datum = date(day=dat[1], month=dat[0], year=dat[2])
            vrednost = results['cash']
            obstojeca = Dividenda.objects.filter(simbol=podjetje).latest('datum')
            if datum > obstojeca.datum:
                d = Dividenda(simbol=podjetje, vrednost=vrednost, datum=datum)
                d.save()

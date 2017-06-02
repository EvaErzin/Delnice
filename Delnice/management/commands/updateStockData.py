from django.core.management.base import BaseCommand, CommandError
from ...dataLoadingScripts import *
class Command(BaseCommand):

    def handle(self, *args, **options):
        updateStockQuotes(getExistingCompanies())
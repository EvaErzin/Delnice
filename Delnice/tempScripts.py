import yahoo_finance as yfn
from DelniceWebApp.models import *

class Company(Object):

    def __init__(self, ticker, preexisting):
        self.tickerSymbol = ticker
        self.stockArray = None
        self.dataLoaded = preexisting

#add exceptions and consider updating all data at every querry
    def update(self):
        #access to yahoo querry language library
        self.stockHandle = yfn.Share(self.ticker)
        # access to django class
        self.djangoHandle = Podjetje()
        if not self.dataLoaded:
            try:
            self.djangoHandle.simbol = self. tickerSymbol
            self.djangoHandle.polnoIme = self.stockHandle.get_name()
            self.djangoHandle.lokacija = self.getLocation()
            self.djangoHandle.panoga = self.getSector()
            self.djangoHandle.ipo = self.getIpo()
            except:
                return
            self.dataLoaded = True

    def getLocation(self):
        return self.stockHandle.get_name()



#GET EXISTING SHARES FROM DATABASE

#SCRUB TOP n COMPANY NAMES




#GET COMPANY DATA

#PUSH COMPANY DATA INTO DATABASE
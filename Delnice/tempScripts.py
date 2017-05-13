import yahoo_finance as yfn
#from DelniceWebApp.models import *
import pandas as pd

class Company():

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
def convertMarketCap(capString):
    """Converts string representation of market capitalisation to integer"""
    # not interested in sub million companies
    coeficient = 0
    try:
        if capString[-1] == "T":
            #short scale meaning (data source is US based)
            coeficient = 10**12
        elif capString[-1] == "B":
            coeficient = 10**9
        elif capString[-1] == "M":
            coeficient = 10**6

        return int(float(capString[1:-1]) * coeficient)
    except:
        #not interested in incorrectly defined companies
        return 0


def getCompanies(companyDict, N=500):
    nasdaqURL = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download"
    nyseURL = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download"

    # ['Symbol', 'MarketCap', 'IPOyear', 'Sector', 'industry']
    nasdaq = pd.read_csv(nasdaqURL, sep = ",", header = 0, usecols = [0,3,4,5,6])
    nyse = pd.read_csv(nyseURL, sep=",", header = 0, usecols = [0,3,4,5,6])
    nasdaq.set_index('Symbol')
    nyse.set_index('Symbol')

    companies = pd.concat([nyse, nasdaq])
    companies['MarketCap'] = companies['MarketCap'].map(lambda s : convertMarketCap(s))
    companies = companies.sort(["MarketCap"], ascending=False)


    for i in companies[:N].itertuples():
        if i[1] not in companyDict:
            companyDict[i[1]] = Company(i[1], False)

    return companyDict

#GET COMPANY DATA

#PUSH COMPANY DATA INTO DATABASE

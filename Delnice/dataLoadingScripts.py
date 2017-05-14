import yahoo_finance as yfn
import DelniceWebApp.models as djangoModels
import pandas as pd
from pyquery import PyQuery
from countries import countries


class Company:

    def __init__(self, ticker, preexisting, ipo=None, sector=None, industry=None):
        self.stockArray = None
        self.stockHandle = None
        self.djangoPodjetje = None
        self.djangoDelnica = None
        self.lastStockDate = None
        self.handlesSet = False
        self.tickerSymbol = ticker
        self.sector = sector
        self.industry = industry
        self.ipo = ipo
        self.dataLoaded = preexisting


    def setup(self):
        try:
            #access to yahoo querry language library
            self.stockHandle = yfn.Share(self.tickerSymbol)
            #access to django class
            self.djangoPodjetje = djangoModels.Podjetje(simbol=self.tickerSymbol)

            self.handlesSet = True
        except Exception as exc:
            print("Setting handles failed: ", exc)

        if not self.dataLoaded and self.handlesSet:
            try:
                self.djangoPodjetje.simbol = self.tickerSymbol
                self.djangoPodjetje.polnoIme = self.stockHandle.get_name()
                self.djangoPodjetje.lokacija = self.getLocation()
                if self.sector:
                    self.djangoPodjetje.sektor = self.sector
                if self.industry:
                    self.djangoPodjetje.industrija = self.industry
                if self.ipo:
                    self.djangoPodjetje.ipo = self.ipo

                self.djangoPodjetje.save()
                print("{} added to database".format(self.stockHandle.get_name()))
            except Exception as exc:
                print("Pushing into database failed: ", exc)
                return
            self.dataLoaded = True
        else:
            try:
                self.lastStockDate = djangoModels.Delnica.objects.filter(simbol=self.tickerSymbol).latest('datum').datum
            except:
                print("Zadnji datum posodabljanja delnic za {} ni na voljo".format(self.tickerSymbol))

#add exception handling
    def getLocation(self):
        """Retrieves country data from yahoo finance webpage and extracts country"""

        url = "https://finance.yahoo.com/quote/{}/profile?p={}".format(self.tickerSymbol, self.tickerSymbol)

        pq = PyQuery(url)
        #company data happens to be the first paragraph on the page
        info = pq('p:first').text()

        info = info.split(" ")
        webAddr = info.pop()

        tempInfo = info
        try:
            while info[-1][-1].isdigit():
                info.pop()

            country = r"n\a"
            for i in range(1, len(info)):
                if " ".join(info[-i:]) in countries:
                    country = " ".join(info[-i:])
                    # address = " ".join(info[:-1])
        except Exception as exc:
            print(exc)
            print(self.tickerSymbol, " - ", tempInfo)

        return country


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


def getExistingCompanies():
    """Retrieves present companies from database"""

    companyList = djangoModels.Podjetje.objects.values_list('simbol', flat=True)

    companyDict = {}
    for i in companyList:
        companyDict[i] = Company(i, True)
        companyDict[i].setup()

    print("Existing companies loaded from database.\n")

    return companyDict


#sort out exception handling
def getTopCompanies(companyDict, N=500, forceUpdate = False):
    """Retrieves list of companies from NASDAQ website and adds top N to dataset"""

    nasdaqURL = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download"
    nyseURL = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download"

    # ['Symbol', 'MarketCap', 'IPOyear', 'Sector', 'industry']
    try:
        nasdaq = pd.read_csv(nasdaqURL, sep=",", header=0, usecols=[0, 3, 4, 5, 6])
        nyse = pd.read_csv(nyseURL, sep=",", header=0, usecols=[0, 3, 4, 5, 6])
    except Exception as exc:
        print(".csv retrieval failed: ", exc)
        return None

    companies = pd.concat([nyse, nasdaq]).drop_duplicates(subset='Symbol')
    companies['MarketCap'] = companies['MarketCap'].map(lambda s : convertMarketCap(s))
    companies = companies.sort_values(by=["MarketCap"], ascending=False)


    print("Company list successfully retrieved from NASDAQ website.\n")

    for i in companies[:N].itertuples():
        if i[1] not in companyDict or forceUpdate:
            companyDict[i[1]] = Company(i[1], False, ipo=i[3], sector=i[4], industry=i[5])
            companyDict[i[1]].setup()

    return companyDict


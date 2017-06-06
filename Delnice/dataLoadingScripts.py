import yahoo_finance as yfn
import yahoo_quote_download.yahoo_quote_download.yqd as yqd
import DelniceWebApp.models as djangoModels
import pandas as pd
import urllib
from pyquery import PyQuery
from Delnice.countries import countries
import datetime
import time

class Company:

    def __init__(self, ticker, preexisting, fullName=None, ipo=None, sector=None, industry=None):
        self.lastStockDate = None
        self.tickerSymbol = ticker
        self.fullName = fullName
        self.sector = sector
        self.industry = industry
        self.ipo = ipo
        self.dataLoaded = preexisting


#add aditional attempts to handles
    def setup(self):
        """Loads last know stock date for existing stock and sets up new ones"""

        if not self.dataLoaded:
            try:
                #access to django class
                djangoPodjetje = djangoModels.Podjetje(simbol=self.tickerSymbol)
            except Exception as exc:
                print("Setting django handle failed: ", exc)
                return None

            try:
                djangoPodjetje.simbol = self.tickerSymbol
                location = self.getLocation()
                if location:
                    djangoPodjetje.lokacija = location
                else:
                    print("Incomplete data for {}, company will not be added to database".format(self.tickerSymbol))
                    return None
                if self. fullName and self.sector and self.industry and self.ipo:
                    djangoPodjetje.polnoIme = self.fullName
                    djangoPodjetje.sektor = self.sector
                    djangoPodjetje.industrija = self.industry
                    djangoPodjetje.ipo = self.ipo
                else:
                    print("Incomplete data for {}, company will not be added to database".format(self.tickerSymbol))
                    return None

                djangoPodjetje.save()
                print("{} added to database".format(self.fullName))
            except Exception as exc:
                print("Pushing into database failed: ", exc)
                return None
            self.dataLoaded = True
        else:
            self.fullName = djangoModels.Podjetje.objects.get(simbol=self.tickerSymbol).polnoIme
            try:
                self.lastStockDate = djangoModels.Delnica.objects.filter(simbol=self.tickerSymbol).latest('datum').datum
            except:
                self.lastStockDate = None
        return 1

#add exception handling
    def getLocation(self):
        """Retrieves country data from yahoo finance webpage and extracts country"""

        url = "https://finance.yahoo.com/quote/{}/profile?p={}".format(self.tickerSymbol, self.tickerSymbol)

        pq = PyQuery(url)
        #company data happens to be the first paragraph on the page
        info = pq('p').contents()

        country = r"n\a"
        for i in info:
            try:
                if i in countries:
                    country = i
            except:
                pass
        return country

#change to loading from oldest to newest
    def loadStockData(self, startDate):
        """Retrieves stock history since either the startDate or latest known update"""

        def isoToPlain(iso):
            return iso[:4]+iso[5:7]+iso[8:]

        share = yfn.Share(self.tickerSymbol)

        if self.lastStockDate == None:
            start = startDate
        elif (datetime.date.today() - self.lastStockDate).days <= 1:
            return
        else:
            start = self.lastStockDate.isoformat()

        #total volume calculated from current price and market cap
        totalVolume = convertMarketCap(share.get_market_cap()) // float(share.get_price())

        failedAttempts = 0
        while True:
            try:
                stockArray = yqd.load_yahoo_quote(self.tickerSymbol, isoToPlain(start), isoToPlain(datetime.date.today().isoformat()))[1:][::-1]
                splitArray = yqd.load_yahoo_quote(self.tickerSymbol, isoToPlain(start), isoToPlain(datetime.date.today().isoformat()), info = "split")[1:]
                break
            except urllib.error.HTTPError:
                time.sleep(1)
                failedAttempts += 1
                if failedAttempts == 5:
                    print("Loading stock data for {} failed".format(self.tickerSymbol))
                continue

        splitDict = {}
        for i in splitArray:
            if i == '':
                continue
            data = i.split(',')
            ratio = list(map(float, data[1].split("/")))
            splitDict[data[0]] =ratio[0]/ratio[1]

        year = ""
        for i in stockArray:
            if i == '':
                continue

            data = i.split(',')

            if data[0][:4] != year:
                year = data[0][:4]
                print("Loading data for ", year)

            delnica = djangoModels.Delnica(simbol=djangoModels.Podjetje.objects.get(simbol=self.tickerSymbol), datum = datetime.date(int(data[0][:4]), int(data[0][5:7]), int(data[0][8:])))
            delnica.odpiralniTecaj = float(data[1])
            delnica.zapiralniTecaj = float(data[5])
            delnica.nepopravljenZapiralniTecaj = float(data[4])
            delnica.volumenTrgovanja = float(data[6])
            delnica.steviloDelnic = int(totalVolume)
            delnica.save()

            if data[0] in splitDict:
                totalVolume = round(totalVolume / splitDict[data[0]], 0)

        print("Stock history between {} and {} loaded for {}".format(data[0], datetime.date.today().isoformat(), self.fullName))




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

        if capString[0].isdigit():
            return int(float(capString[:-1]) * coeficient)
        else:
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

    # ['Symbol', 'Name', 'MarketCap', 'IPOyear', 'Sector', 'industry']
    try:
        nasdaq = pd.read_csv(nasdaqURL, sep=",", header=0, usecols=[0, 1, 3, 4, 5, 6])
        nyse = pd.read_csv(nyseURL, sep=",", header=0, usecols=[0, 1, 3, 4, 5, 6])
    except Exception as exc:
        print(".csv retrieval failed: ", exc)
        return None

    companies = pd.concat([nyse, nasdaq]).drop_duplicates(subset='Symbol')
    companies['MarketCap'] = companies['MarketCap'].map(lambda s : convertMarketCap(s))
    companies = companies.sort_values(by=["MarketCap"], ascending=False)


    print("Company list successfully retrieved from NASDAQ website.\n")

    first = 0
    last = N
    totalFailedCOmpanies = 0
    while True:
        failedCompanies = 0
        for i in companies[first:last].itertuples():
            if i[1] not in companyDict or forceUpdate:
                companyDict[i[1]] = Company(i[1], False, fullName=i[2], ipo=i[4], sector=i[5], industry=i[6])
                if companyDict[i[1]].setup() == None:
                    del companyDict[i[1]]
                    failedCompanies += 1
        if failedCompanies != 0 and last+failedCompanies <= len(companies):
            first = last
            last = last + failedCompanies
            totalFailedCOmpanies += failedCompanies
        else:
            break

    print("\nTop {} companies loaded into database with {} failures".format(N, failedCompanies))

    return companyDict

def updateStockQuotes(companyDict, startDate = "2000-01-01"):
    """Updates stock data for all companies in companyDict starting at either the startDate or last know date"""
    if companyDict == None:
        return None
    n = 0
    for i in companyDict:
        n += 1
        try:
            print("Loading stock data for {}  ({}/{})".format(i, n, len(companyDict)))
            companyDict[i].loadStockData(startDate)
        except Exception as exc:
            print("Error loading stock data: ", exc)

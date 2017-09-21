from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user
from .models import *
from .forms import *
from .tables import *
from django.db.models import Count, Min, Sum, Avg, F, DecimalField, ExpressionWrapper, Value, IntegerField
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components
from django.utils.translation import ugettext as _
from bokeh.palettes import Viridis256 as pal #@UnresolvedImport
from django_tables2 import RequestConfig
import time
import numpy as np
import itertools


import pdb
import datetime

# Create your views here.


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserCreationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')

    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def portfolio(request):
    user = get_user(request)
    if user.is_anonymous:
        return redirect('login')
    else:
        d = Delnica.objects.all()
        portf = Portfolio.objects.filter(uporabnik=user)
        portf1 = portf.values('simbol').annotate(kolicinaSkupaj=Sum('kolicina'))
        slovar = {}
        simboli = portf.distinct('simbol').values('simbol')
        datumi = d.order_by('datum').values_list('datum').distinct()
        datumi = np.array(datumi)
        sk_cena = 0
        sk_vrednost = 0
        for simbol in simboli:
            n = np.array(portf.filter(simbol=simbol['simbol']).order_by('datum').values_list('kolicina', 'vrednost', 'datum'))
            rez = None
            for nak in n:
                if rez is not None:
                    rez = rez + np.where(datumi> nak[2], np.array([nak[0]*nak[1],nak[0]]), 0)
                else:
                    rez = np.where(datumi> nak[2], np.array([nak[0]*nak[1],nak[0]]), 0)
                sk_cena += nak[0] * nak[1]
                sk_vrednost += nak[0] * d.filter(simbol=simbol['simbol']).latest('datum').zapiralniTecaj
            temp = np.transpose(np.array(d.filter(simbol=simbol['simbol']).order_by('datum').values_list('zapiralniTecaj').distinct()))*rez[:,1] - rez[:,0]
            slovar[simbol['simbol']] = list(temp.flatten())
        datumi = datumi.flatten()

        plot = figure(plot_width=600, plot_height=400, x_axis_type='datetime')
        for simbol, barva in zip(simboli, pal[::256//len(simboli)]):
            plot.line(datumi,slovar[simbol['simbol']], line_width=1, line_alpha=0.7, color=barva, legend=simbol['simbol'])
        skupaj = [sum([list[i] for list in slovar.values()]) for i in range(len(datumi))]
        plot.line(datumi, skupaj, line_width=1.5, color='firebrick', legend=_('Profit'))
        plot.legend.background_fill_alpha = 0.95
        plot.legend.location = 'top_left'
        plot.legend.click_policy = 'hide'
        script, div = components(plot)
        table = PortfolioTabela(portf1)
        context = {
            'scr': script,
            'div': div,
            'sk_cena': np.round(sk_cena,2),
            'sk_vrednost': np.round(sk_vrednost,2),
            'diffp': np.round(sk_vrednost - sk_cena,2),
            'diffn': np.round(sk_cena - sk_vrednost,2),
            'portfolio': table
        }
        return render(request, 'portfolio.html', context)


def portfolioDetailed(request, simbol):
    user = get_user(request)
    if user.is_anonymous:
        return redirect('login')
    else:
        podjetje = Podjetje.objects.get(simbol=simbol)
        delnice = Delnica.objects.filter(simbol=podjetje).order_by('datum')
        portf = Portfolio.objects.filter(uporabnik=user, simbol=podjetje).order_by('datum')
        datumi = np.array(delnice.filter(datum__gte=portf[0].datum).values_list('datum').distinct())
        if len(datumi) == 0 or len(datumi) == 1:
            datumi = np.array([delnice.latest('datum').datum])
        arr = np.array(portf.values_list('kolicina', 'vrednost'))
        kol = np.sum(arr[:,0])
        avg = np.sum(arr[:,0]*arr[:,1])/kol
        datumi = datumi.flatten()
        vrednosti = np.array(delnice.filter(datum__gte=datumi[0]).values_list('zapiralniTecaj')).flatten()
        povprecne = np.ones(datumi.shape)*avg

        izplacano = 0
        dvd = Dividenda.objects.filter(simbol=simbol, datum__gte=datumi[0])
        for dv in dvd:
            temp = portf.filter(datum__lte=dv.datum).values('simbol').annotate(vsota=Sum('kolicina'))
            de = delnice.get(datum=dv.datum).zapiralniTecaj
            izplacano += np.round(temp[0]['vsota']*dv.vrednost*de/100, 2)

        plot = figure(plot_height=400, plot_width=600, x_axis_type='datetime')
        plot.line(datumi, vrednosti, line_width=1, color='black', legend=_('Zapiralni tečaj'))
        plot.line(datumi, povprecne, line_width=1, color='firebrick', legend=_('Povprečna vrednost kupljenih delnic'))
        plot.legend.background_fill_alpha = 0.95
        plot.legend.location = 'top_left'
        script, div = components(plot)
        table = PortfolioTabela1(portf)
        deln = delnice.latest('datum')
        context = {
            'scr1': script,
            'div1': div,
            'portfolio': table,
            'simbol': simbol,
            'podjetje': podjetje,
            'izplacano': izplacano,
            'povp': round(povprecne[-1], 2),
            'skupna': round(kol*avg, 2),
            'uradna': round(kol*deln.zapiralniTecaj, 2),
            'deln': round(deln.zapiralniTecaj,2),
            'prof': round(kol*(deln.zapiralniTecaj - avg),2)
        }
    return render(request, 'portfolioDetailed.html', context)

def companyList(request):
    lastDate = Delnica.objects.latest('datum').datum
    companies = Podjetje.objects.select_related().filter(delnica__datum=lastDate).annotate(marketCap=ExpressionWrapper(F('delnica__steviloDelnic')*F('delnica__zapiralniTecaj') /1000000, output_field=IntegerField()))

    table = CompaniesTabela(companies)
    RequestConfig(request, paginate={'per_page':20}).configure(table)
    context = {
        'companies': table
    }
    return render(request, 'companyList.html', context)

def companyDetails(request, simbol):
    podjetje = Podjetje.objects.get(simbol=simbol)
    dividends = Dividenda.objects.filter(simbol=simbol)
    stock = Delnica.objects.filter(simbol=simbol).order_by('datum')
    values = stock.values_list('zapiralniTecaj')
    value = stock.latest('datum').zapiralniTecaj
    dates = stock.values_list('datum')
    dates = [i[0] for i in dates]

    plot = figure(plot_width=600, plot_height=400, x_axis_type='datetime')
    # plot.circle(dates,values, size=2, line_color = 'firebrick')
    plot.line(dates,values, line_width=1, line_color = 'firebrick')
    plot.xaxis.formatter = DatetimeTickFormatter(days=["%d %B %Y"])
    plot.xaxis.major_label_orientation = 'horizontal'
    script, div = components(plot)
    valueTable = CompanyDetailsTabela(stock)
    RequestConfig(request, paginate={'per_page': 50}).configure(valueTable)
    dividendTable = DividendsTabela(dividends)
    #RequestConfig(request, paginate={'per_page': 10}).configure(dividendTable)
    context = {
        'scr': script,
        'div': div,
        'delnice': valueTable,
        'dividende' : dividendTable,
        'podjetje': podjetje,
        'zadnjaVrednost' : value
    }
    return render(request, 'companyDetails.html', context)

def newPurchase(request):
    user = get_user(request)
    if user.is_anonymous:
        return redirect('login')
    else:
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = PortfolioForm(request.POST)
            user = get_user(request)
            # pdb.set_trace()
            # check whether it's valid:
            if form.is_valid() and (not user.is_anonymous):
                nakup = form.save(commit=False)
                nakup.uporabnik = user
                nakup.save()
                return HttpResponseRedirect('/portfolio/')
            elif user.is_anonymous:
                return redirect('login')
            else:
                return render(request, 'newPurchase.html', {'form': form})
        else:
            data = {'datum': datetime.date.today()}
            if request.GET.get('podjetje'):
                data['simbol'] = Podjetje.objects.get(simbol=request.GET.get('podjetje'))
                # pdb.set_trace()
            if request.GET.get('vrednost'):
                data['vrednost'] = request.GET.get('vrednost')
            form = PortfolioForm(initial=data)

            return render(request, 'newPurchase.html', {'form': form})

def brisiNakup(request, id):
    n = Portfolio.objects.get(id=id)
    p = n.simbol
    n.delete()
    return portfolioDetailed(request, p)

def indexno(request):
    return redirect('index')
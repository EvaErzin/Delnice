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
        portf = Portfolio.objects.filter(uporabnik=user)
        portf1 = portf.values('simbol').annotate(kolicinaSkupaj=Sum('kolicina'))
        simboli = portf.values('simbol').distinct()
        slovar = {}
        datumi = []
        for simbol in simboli:
            zapravljeno = 0
            kolicina = 0
            podjetje = Podjetje.objects.get(simbol=simbol['simbol'])
            nakupi = portf.filter(simbol=podjetje)
            delnice = Delnica.objects.filter(simbol=podjetje)
            datumi = Delnica.objects.all().order_by('-datum').values('datum').distinct()[:80][::-1]
            datumi = [i['datum'] for i in datumi]
            profiti = []
            nak = nakupi.filter(datum__lt=datumi[0])
            for n in nak:
                zapravljeno += n.kolicina * n.vrednost
                kolicina += n.kolicina
            for datum in datumi:
                nak = nakupi.filter(datum=datum)
                for n in nak:
                    zapravljeno += n.kolicina * n.vrednost
                    kolicina += n.kolicina
                try:
                    zapiralni = delnice.get(datum=datum).zapiralniTecaj
                except Delnica.DoesNotExist:
                    zapiralni = 0
                profiti.append(kolicina*zapiralni - zapravljeno)
            slovar[simbol['simbol']] = profiti
        plot = figure(plot_width=600, plot_height=400, x_axis_type='datetime')
        for simbol, barva in zip(simboli, pal[::256//len(simboli)]):
            simbol = simbol['simbol']
            plot.line(datumi,slovar[simbol], line_width=2, color=barva, legend=simbol)
        skupaj = [sum([list[i] for list in slovar.values()]) for i in range(len(datumi))]
        plot.line(datumi, skupaj, line_width=4, color='firebrick', legend=_('Profit'))
        plot.legend.background_fill_alpha = 0.95
        plot.legend.location = 'top_left'
        plot.legend.click_policy = 'hide'
        script, div = components(plot)
        table = PortfolioTabela(portf1)
        context = {
            'scr': script,
            'div': div,
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
        portf = Portfolio.objects.filter(uporabnik=user, simbol=simbol)
        datumi = []
        vrednosti = []
        povprecne = []
        for delnica in delnice:
            datumi.append(delnica.datum)
            vrednosti.append(round(delnica.zapiralniTecaj, 3))
        vr = 0
        kol = 0
        for i in range(len(datumi)):
            nak = portf.filter(datum=datumi[i])
            for n in nak:
                vr += n.kolicina * n.vrednost
                kol += n.kolicina
            if kol != 0:
                povprecne.append(vr/kol)
            else: povprecne.append(0)
        povprecne =  list(map(lambda x: round(x,2), povprecne))
        t1 = datetime.datetime
        t2 = datetime.datetime
        datum1 = max(datumi)-datetime.timedelta(days=60)
        datum2 = max(datumi)
        t1 = t1.fromordinal(datum1.toordinal()).timestamp()
        t2 = t2.fromordinal(datum2.toordinal()).timestamp()
        plot = figure(plot_height=400, plot_width=600, x_axis_type='datetime', x_range=(t1*1000, t2*1000))
        # plot.circle(datumi, vrednosti, fill_color='white', line_color='black', size=8, legend=_('Zapiralni tečaj'))
        plot.line(datumi, vrednosti, line_width=3, color='black', legend=_('Zapiralni tečaj'))
        plot.line(datumi, povprecne, line_width=3, color='firebrick', legend=_('Povprečna vrednost kupljenih delnic'))
        plot.legend.background_fill_alpha = 0.95
        plot.legend.location = 'top_left'
        # plot.xaxis.major_label_orientation = 'vertical'
        # plot.xaxis.major_label_standoff = 35
        script, div = components(plot)
        table = PortfolioTabela1(portf)
        deln = delnice.latest('datum')
        context = {
            'scr1': script,
            'div1': div,
            'portfolio': table,
            'simbol': simbol,
            'podjetje': podjetje,
            'povp': round(povprecne[-1], 2),
            'skupna': round(kol*povprecne[-1], 2),
            'uradna': round(kol*deln.zapiralniTecaj, 2),
            'deln': round(deln.zapiralniTecaj,2),
            'prof': round(kol*(deln.zapiralniTecaj - povprecne[-1]),2)
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
    stock = Delnica.objects.filter(simbol=simbol)
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
    table = CompanyDetailsTabela(stock)
    RequestConfig(request, paginate={'per_page': 50}).configure(table)
    context = {
        'scr': script,
        'div': div,
        'delnice': table,
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
            pdb.set_trace()
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
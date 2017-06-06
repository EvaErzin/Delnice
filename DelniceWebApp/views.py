from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user
from .models import *
from .tables import *
from django.db.models import Count, Min, Sum, Avg, F, DecimalField, ExpressionWrapper, Value
from bokeh.plotting import figure
from bokeh.embed import components
from django.utils.translation import ugettext as _
from bokeh.palettes import Viridis256 as pal #@UnresolvedImport
from django_tables2 import RequestConfig
import itertools



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
            nakupi = portf.filter(simbol=simbol)
            delnice = Delnica.objects.filter(simbol=simbol)
            datumi = delnice.values('datum')
            profiti = []
            for datum in datumi:
                nak = nakupi.filter(datum=datum)
                for n in nak:
                    zapravljeno += nak.kolicina * nak.vrednost
                    kolicina += nak.kolicina
                profiti.append(kolicina*delnice.get(datum=datum).zapiralniTecaj - zapravljeno)
            slovar[simbol['simbol']] = profiti
        plot = figure(plot_width=600, plot_height=400, x_range=list(datumi))
        for simbol, barva in zip(simboli, pal[:len(simboli)]):
            simbol = simbol['simbol']
            plot.circle(datumi, slovar[simbol], fill_color='white', line_color=barva, size=8, legend=simbol)
            plot.line(datumi,slovar[simbol], line_width=3, color=barva, legend=simbol)
        plot.legend.background_fill_alpha = 0.95
        plot.legend.location = 'top_left'
        plot.legend.click_policy = 'hide'
        plot.xaxis.major_label_orientation = 'vertical'
        plot.xaxis.major_label_standoff = 55
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
        slovar = portf.aggregate(vr=Sum('vrednost'), kol=Sum('kolicina'))
        povp = slovar['vr']/slovar['kol']
        round(povp, 2)
        datumi = []
        vrednosti = []
        for delnica in delnice:
            datumi.append(delnica.datum.isoformat())
            vrednosti.append(round(delnica.zapiralniTecaj, 3))
        povprecja = [povp for i in datumi]
        plot = figure(plot_height=400, plot_width=600, x_range=datumi)
        plot.circle(datumi, vrednosti, fill_color='white', line_color='black', size=8, legend=_('Zapiralni tečaj'))
        plot.line(datumi, vrednosti, line_width=3, color='black', legend=_('Zapiralni tečaj'))
        plot.circle(datumi, povprecja, fill_color='white', line_color='firebrick', size=8, legend=_('Povprečna vrednost kupljenih delnic'))
        plot.line(datumi, povprecja, line_width=3, color='firebrick', legend=_('Povprečna vrednost kupljenih delnic'))
        plot.legend.background_fill_alpha = 0.95
        plot.legend.location = 'top_left'
        plot.xaxis.major_label_orientation = 'vertical'
        plot.xaxis.major_label_standoff = 55
        script, div = components(plot)
        table = PortfolioTabela1(portf)
        context = {
            'scr1': script,
            'div1': div,
            'portfolio': table,
            'simbol': simbol,
            'podjetje': podjetje,
        }
    return render(request, 'portfolioDetailed.html', context)

def companyList(request):
    lastDate = Delnica.objects.latest('datum').datum
    companies = Podjetje.objects.select_related().filter(delnica__datum=lastDate).annotate(marketCap=ExpressionWrapper(F('delnica__steviloDelnic')*F('delnica__zapiralniTecaj'), output_field=DecimalField(decimal_places=1)))

    table = CompaniesTabela(companies)
    RequestConfig(request, paginate={'per_page':20}).configure(table)
    context = {
        'companies': table
    }
    return render(request, 'companyList.html', context)
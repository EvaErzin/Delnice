from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user
from .models import *
from django.template import RequestContext

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
        portf = Portfolio.objects.all()
        table = PortfolioTabela(portf)
        context = {
            'portfolio': table
        }
        return render(request, 'portfolio.html', context)

def portfolioDet(request, simbol):
    return  render(request, 'portfolio.html')
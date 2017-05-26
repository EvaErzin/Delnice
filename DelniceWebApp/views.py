from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import *
from django.template import RequestContext

# Create your views here.
def index(request):
    template = loader.get_template('index.html')
    return render(request, 'index.html')
"""Delnice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from DelniceWebApp import views
import Delnice.settings as settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^/$', views.indexno, name='IndexNo')
]

urlpatterns += i18n_patterns(
    url(r'^$', views.index, name='Index'),
    url('^', include('django.contrib.auth.urls')),
    url('^register/$', views.register, name="register"),
    url('^portfolio/$', views.portfolio, name="portfolio"),
    url('^portfolio/(?P<simbol>.+?)$', views.portfolioDetailed, name='portfolioDetailed'),
    url('^companies/$', views.companyList, name="companyList"),
    url('^companies/(?P<simbol>.+?)$', views.companyDetails, name='companyDetails'),
    url('^novNakup/$', views.newPurchase, name='newPurchase'),
    url('^brisi/(?P<id>.+?)$', views.brisiNakup, name='brisiNakup')
)


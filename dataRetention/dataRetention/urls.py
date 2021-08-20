"""dataRetention URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf.urls import url

from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stayData', views.stayData, name='stayData'),
    url(r'^getStayId', views.getStayId, name='getStayId'),
    url(r'^allStays', views.allStays, name='allStays'),
    url(r'^removeStay', views.removeStay, name='removeStay'),
    url(r'^consentInformation', views.consentInformation, name='consentInformation'),
    url(r'^listConsent', views.listConsent, name='listConsent'),
    url(r'^userData', views.userData, name='userData'),
    url(r'^exportCsv', views.exportCsv, name='exportCsv'),
    url(r'^entityData', views.entityData, name='entityData'),
    url(r'^removeDataUser', views.removeDataUser, name='removeDataUser'),
    url(r'^receiptInformation', views.receiptInformation, name='receiptInformation'),
    url(r'^receiptsByStay', views.receiptsByStay, name='receiptsByStay'),
    url(r'^policyByDevice', views.policyByDevice, name='policyByDevice'),
    url(r'^listDevicesPolicies', views.listDevicesPolicies, name='listDevicesPolicies'),
    
    

    url(r'^int/datadeletion', views.requestDataDeletion, name='requestDataDeletion'),
    url(r'^int/stayinfo', views.getStayInfo, name='getStayInfo'),
    url(r'^int/dataexport', views.dataexportrequest, name='dataexportrequest'),
    url(r'^int/listreceipts', views.listReceipts, name='listReceipts'),


]

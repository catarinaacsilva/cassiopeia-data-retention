import json
import logging
import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django.shortcuts import render

logger = logging.getLogger(__name__)


'''
    Initial page just to init the demo
'''
def index(request):
    return render(request, 'index.html')

'''
    Receive data stay from cassiopeia
'''
@csrf_exempt
@api_view(('POST',))
def stayData():
    parameters = json.loads(request.body)
    datein = parameters['datein']
    dateout = parameters['dateout']
    email = parameters['email']

    try:
        Stay_Data.objects.create(email=email, datein=datein, dateout=dateout)
    except:
        return Response('Cannot create the data stay record', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)

'''
    Receive receipt identification from receipt generator
'''
@csrf_exempt
@api_view(('POST',))
def receiptData():
    parameters = json.loads(request.body)
    json_receipt = parameters['json_receipt']
    receipt_timestamp = json_receipt['Receipt Timestamp']
    id_receipt = json_receipt['Receipt ID']

    try:
        Receipt_Data.objects.create(id_receipt=id_receipt, receipt_timestamp=receipt_timestamp)
    except:
        return Response('Cannot create the data stay record', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)


'''
    Receive consent information from cassiopia
'''
@csrf_exempt
@api_view(('POST',))
def consentData():
    parameters = json.loads(request.body)
    policyid = parameters['policyid']
    consent = parameters['consent']
    email = parameters['email']
    timestamp = parameters['timestamp']

    try:
        Policy_Consent.objects.create(policyid=policyid, consent=consent, email=email, timestamp=timestamp)
    except:
        return Response('Cannot create the consent record', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)
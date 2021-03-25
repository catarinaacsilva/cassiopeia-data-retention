import json
import logging
import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django.shortcuts import render

from django.conf import settings

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
def receiptInformation():
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
def consentInformation():
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


'''
    Correlate devices data and user
'''
@csrf_exempt
@api_view(('POST'))
def userData(request):
    parameters = json.loads(request.body)
    id_stay = parameters['id']

    qs = Stay_Data.objects.get(id=id_stay)
    dataIn = qs.datain
    dataOut = qs.dataOut

    query = 'from(bucket:"cassiopeiainflux") |> range(start: dataIn, stop: dataOut)'

    result = settings.clientInflux.query_api().query(org='it', query=query)
    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_value(), record.get_field()))

    #TODO: store results on database? or just to remove: delete to the influxdb
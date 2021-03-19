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
    Receive receipt data from receipt generator
'''
@csrf_exempt
@api_view(('POST',))
def receiptData():
    parameters = json.loads(request.body)
    id_receipt = parameters['id_receipt']
    receipt_timestamp = parameters['receipt_timestamp']

    try:
        Receipt_Data.objects.create(id_receipt)
    except:
        return Response('Cannot create the data stay record', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)
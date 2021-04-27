import json
import csv
import logging
import requests
import datetime
import pytz
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.db import transaction

from django.shortcuts import render

from influxdb_client import InfluxDBClient

from django.conf import settings

from .models import Stay_Data, User, Policy_Consent, Receipt_Data

logger = logging.getLogger(__name__)


'''
    Initial page just to init the demo
'''
def index(request):
    return render(request, 'index.html')

'''
    Returns an ``InfluxDBClient`` instance.
'''
def get_influxdb_client():
    client = InfluxDBClient(
        url = settings.INFLUXDB_URL,
        token = settings.INFLUXDB_TOKEN,
        org = settings.INFLUXDB_ORG)
    return client

'''
    Receive data stay from cassiopeia
'''
@csrf_exempt
@api_view(('POST',))
def stayData(request):
    parameters = json.loads(request.body)
    datein = parameters['datein']
    dateout = parameters['dateout']
    email = parameters['email']

    try:
        # check if it exists
        qs = Stay_Data.objects.filter(email=email, datein=datein, dateout=dateout)
        if not qs.exists():
            with transaction.atomic():
                if not User.objects.filter(email=email).exists():
                    User.objects.create(email=email)
                user = User.objects.get(email=email)
                stay = Stay_Data.objects.create(email=user, datein=datein, dateout=dateout)
        else:
            stay = qs.first()

    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    
    print({'stay_id': stay.pk})
    return JsonResponse({'stay_id': int(stay.pk)}, status=status.HTTP_201_CREATED)

'''
    Send the stay id to cassiopeia
'''
@csrf_exempt
@api_view(('GET',))
def getStayId(request):
    email = request.GET['email']
    datein = request.GET['datein']
    dateout = request.GET['dateout']

    try:
        qs = Stay_Data.objects.filter(email=email, datein=datein, dateout=dateout)
        stay = qs.first()
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'email': email, 'datein':datein, 'dateout':dateout, 'stay_id':int(stay.pk)}, status=status.HTTP_201_CREATED)


'''
    List all the stays
'''
@csrf_exempt
@api_view(('GET',))
def allStays(request):
    email = request.GET['email']

    stay_info = Stay_Data.objects.filter(email=email)
    response = []
    for stay in stay_info:
        response.append({'id':stay.id, 'dateIn': stay.datein, 'dateOut': stay.dateout})

    return JsonResponse({'email': email, 'stays':response}, status=status.HTTP_201_CREATED)


'''
    Remove stay: For debug only
'''
@csrf_exempt
@api_view(('POST',))
def removeStay(request):
    parameters = json.loads(request.body)
    datein = parameters['datein']
    dateout = parameters['dateout']
    email = parameters['email']

    try:
        with transaction.atomic():
            user = User.objects.get(email=email)
            Stay_Data.objects.filter(email=user, datein=datein, dateout=dateout).delete()
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)


'''
    Receive consent information from cassiopeia
'''
@csrf_exempt
@api_view(('POST',))
def consentInformation(request):
    parameters = json.loads(request.body)
    policyid = parameters['policyid']
    consent = parameters['consent']
    timestamp = parameters['timestamp']
    stay_id = parameters['stay_id']

    try:
        with transaction.atomic():
            stay = Stay_Data.objects.get(pk=stay_id)
            if stay:
                Policy_Consent.objects.create(policy_id=policyid, consent=consent, stay_id=stay, timestamp=timestamp)
            else:
                return Response(f'Stay id ({stay_id}) does not exist', status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)


'''
    List consent information
'''
@csrf_exempt
@api_view(('GET',))
def listConsent(request):
    stay_id = request.GET['stay_id']

    consent_info = Policy_Consent.objects.filter(stay_id=stay_id)
    response = []
    for c in consent_info:
        response.append({'policyid':c.policy_id, 'consent': c.consent, 'timestamp': c.timestamp})

    return JsonResponse({'stay_id': stay_id, 'consents':response}, status=status.HTTP_201_CREATED)


'''
    Correlate devices data and user
'''
@csrf_exempt
@api_view(('GET',))
def userData(request):
    stay_id = request.GET['stay_id']
    email = request.GET['email']

    try:
        qs = Stay_Data.objects.get(id=stay_id)
        dateIn = qs.datein
        dateOut = qs.dateout

        query = f'from(bucket:"cassiopeiainflux") |> range(start: {dateIn}, stop: {dateOut})'

        client = get_influxdb_client()
        result = client.query_api().query(org='it', query=query)
        results = []

        for table in result:
            for record in table.records:
                results.append((record['_time'], record.get_measurement(), record['entity_id'], record.get_value()))
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    
    return JsonResponse({'email': email, 'data':results}, status=status.HTTP_201_CREATED) 


'''
    Export personal data to a CSV
'''
@csrf_exempt
@api_view(('GET',))
def exportCsv(request):
    stay_id = request.GET['stay_id']

    try:
        qs = Stay_Data.objects.get(id=stay_id)
        dateIn = qs.datein
        dateOut = qs.dateout

        query = f'from(bucket:"cassiopeiainflux") |> range(start: {dateIn}, stop: {dateOut})'
        
        client = get_influxdb_client()
        result = client.query_api().query(org='it', query=query)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        writer = csv.writer(response)
        for table in result:
            for record in table.records:
                writer.writerow([record['_time'], record.get_measurement(), record['entity_id'], record.get_value()])
        return response
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    return Response('Problem', status=status.HTTP_400_BAD_REQUEST)


'''
    Return entity ids of the sensors that collected data
'''
@csrf_exempt
@api_view(('GET',))
def entityData(request):
    stay_id = request.GET['stay_id']
    email = request.GET['email']

    try:
        qs = Stay_Data.objects.get(id=stay_id)
        dateIn = qs.datein
        dateOut = qs.dateout

        query = f'from(bucket:"cassiopeiainflux") |> range(start: {dateIn}, stop: {dateOut})'

        client = get_influxdb_client()
        result = client.query_api().query(org='it', query=query)
        results = []
       
        for table in result:
            for record in table.records:
                if not record['entity_id'] in results:
                    results.append(record['entity_id'])
                    
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    
    return JsonResponse({'email': email, 'entities':results}, status=status.HTTP_201_CREATED)


'''
    Remove user data of the influxdb by stay and the email
'''
@csrf_exempt
@api_view(('GET',))
def removeDataUser(request):
    try:
        stay_id = request.GET['stay_id']
        email = request.GET['email']

        user = User.objects.get(email=email)
        qs = Stay_Data.objects.get(id=stay_id, email=user)

        dateIn = qs.datein
        dateOut = qs.dateout

        #check if dateIn and dateOut are Date
        if isinstance(dateIn, datetime.date):
            print('convert dateIn to datetime')
            dateIn = datetime.datetime(year=dateIn.year, month=dateIn.month, day=dateIn.day)

        if isinstance(dateOut, datetime.date):
            print('convert dateOut to datetime')
            dateOut = datetime.datetime(year=dateOut.year, month=dateOut.month, day=dateOut.day)
        fmt = '%Y-%m-%dT%H:%M:%SZ'
        #utc = pytz.utc
        #dateIn = utc.localize(dateIn)
        dateIn = dateIn.strftime(fmt)
        dateOut = dateOut.strftime(fmt) 

        print(f'In {dateIn} Out {dateOut}')
        
        #query = f'influx delete --bucket cassiopeiainflux --start {dateIn} --stop {dateOut}'
        client = get_influxdb_client()
        client.delete_api().delete(dateIn, dateOut, '',  bucket='cassiopeiainflux', org='it')
       
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return Response('Data Removed', status=status.HTTP_200_OK)




'''
TESTED
##################################################################################################
NOT TESTED
'''


'''
    Receive receipt from CASSIOPEIA

@csrf_exempt
@api_view(('POST',))
def receiptInformation(request):
    try:
        parameters = json.loads(request.body)
        id_receipt = parameters['id_receipt']
        stay_id = parameters['stay_id']


        if User.objects.filter(email=email).email.exists():
            Receipt_Data.objects.create(id_receipt=id_receipt, stay_id=stay_id)
            
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return Response('Receipt ID stored', status=status.HTTP_201_CREATED)
'''

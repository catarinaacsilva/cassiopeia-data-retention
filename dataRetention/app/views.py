import json
import csv
import logging
import requests
import pytz
from datetime import datetime, date
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

from .models import Stay, User, Stay_Receipt

import traceback

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
    Receive data stay from privacy manager
'''
@csrf_exempt
@api_view(('POST',))
def stayData(request):
    parameters = json.loads(request.body)
    datein = datetime.strptime(parameters['datein'], '%Y-%m-%d %H:%M:%S')
    dateout = datetime.strptime(parameters['dateout'], '%Y-%m-%d %H:%M:%S')
    email = parameters['email']
    receipt_id = parameters['receipt_id']

    try:
        # check if it exists
        qs = Stay.objects.filter(email=email, datein=datein, dateout=dateout)
        if not qs.exists():
            with transaction.atomic():
                if not User.objects.filter(email=email).exists():
                    User.objects.create(email=email)
                user = User.objects.get(email=email)
                stay = Stay.objects.create(email=user, datein=datein, dateout=dateout)
        else:
            stay = qs.first()
        
        # Store receipt id
        Stay_Receipt.objects.create(stayid=stay, receiptid=receipt_id)

    except Exception as e:
        print(e)
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    
    print({'stay_id': stay.pk})
    return JsonResponse({'stay_id': int(stay.pk)}, status=status.HTTP_201_CREATED)


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
        qs = Stay.objects.get(id=stay_id)
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
        print(e)
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    
    return JsonResponse({'email': email, 'entities':results}, status=status.HTTP_201_CREATED)



'''
    Remove user data of the influxdb by stay and the email
'''
@csrf_exempt
@api_view(('DELETE',))
def removeDataUser(request):
    try:
        stay_id = request.GET['stay_id']
        email = request.GET['email']
        # get stay
        user = User.objects.get(email=email)
        qs = Stay.objects.get(id=stay_id, email=user)

        if qs.deleted:
            return Response('Data Removed', status=status.HTTP_200_OK)
        
        dateIn = qs.datein
        dateOut = qs.dateout

        #check if dateIn and dateOut are Date
        if isinstance(dateIn, date):
            print('convert dateIn to datetime')
            dateIn = datetime(year=dateIn.year, month=dateIn.month, day=dateIn.day)

        if isinstance(dateOut, date):
            print('convert dateOut to datetime')
            dateOut = datetime(year=dateOut.year, month=dateOut.month, day=dateOut.day)
        fmt = '%Y-%m-%dT%H:%M:%SZ'
        #utc = pytz.utc
        #dateIn = utc.localize(dateIn)
        dateIn = dateIn.strftime(fmt)
        dateOut = dateOut.strftime(fmt) 

        print(f'In {dateIn} Out {dateOut}')
        
        # query = f'influx delete --bucket cassiopeiainflux --start {dateIn} --stop {dateOut}'
        client = get_influxdb_client()

        # compute means and stddev
        query = f'from(bucket:"cassiopeiainflux") |> range(start: {dateIn}, stop: {dateOut}) |> mean()'
        result_means = client.query_api().query(org='it', query=query)
        query = f'from(bucket:"cassiopeiainflux") |> range(start: {dateIn}, stop: {dateOut}) |> stddev()'
        result_stddev = client.query_api().query(org='it', query=query)
        
        # store summary
        #TODO

        # purge data
        client.delete_api().delete(dateIn, dateOut, '',  bucket='cassiopeiainflux', org='it')

        # mark data as purged
        qs.deleted = True
        qs.save()

    except Exception as e:
        print(e)
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return Response('Data Removed', status=status.HTTP_200_OK)


@csrf_exempt
@api_view(('GET',))
def getStays(request):
    stays = []
    try:
        email = request.GET['email']

        receipt_object = Stay_Receipt.objects.filter(stayid__email=email)
        for r in receipt_object:
            
            url = settings.RECEIPTGET
            p = {'email': email, 'receiptid': r.receiptid}
            x = requests.get(url, params=p)
            print(x.text)
            receipt_object = json.loads(x.text)['receipt']
            ri = {'receipt': json.dumps(receipt_object), 'stayId': r.stayid.pk, 'din': r.stayid.datein, 'dout':r.stayid.dateout, 'deleted': r.stayid.deleted}
            stays.append(ri)
    except Exception as e:
        print(e) 
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'stays': stays}, status=status.HTTP_200_CREATED)

'''
##################################################################################################
                            INTERFACE
##################################################################################################
'''

def listReceipts(request):
    # get email from url parameter
    email = request.GET.get('email', None)

    receipts = []
    emails = []

    # get all users
    users = User.objects.all()
    for u in users:
        emails.append(u.email)
    
    # get the first email for available users
    if email is None and len(emails) > 0:
        email = emails[0]
    
    receipt_object = Stay_Receipt.objects.filter(stayid__email=email)
    for r in receipt_object:
        print(r.stayid.pk)
        url = settings.RECEIPTGET
        p = {'email': email, 'receiptid': r.receiptid}
        x = requests.get(url, params=p)
        #print(x.text)
        receipt_object = json.loads(x.text)['receipt']
        ri = {'receipt': json.dumps(receipt_object), 'stayId': r.stayid.pk, 'din': r.stayid.datein, 'dout':r.stayid.dateout, 'deleted': r.stayid.deleted}
        receipts.append(ri)
    return render(request, 'listReceipts.html', {'email':email, 'emails':emails, 'receipts': receipts}) 


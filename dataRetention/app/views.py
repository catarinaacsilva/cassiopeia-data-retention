import json
import logging
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.db import transaction

from django.shortcuts import render

from django.conf import settings

from .models import Stay_Data, User, Policy_Consent

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
def stayData(request):
    parameters = json.loads(request.body)
    datein = parameters['datein']
    dateout = parameters['dateout']
    email = parameters['email']

    try:
        with transaction.atomic():
            if not User.objects.filter(email=email).exists():
                User.objects.create(email=email)
            user = User.objects.get(email=email)
            Stay_Data.objects.create(email=user, datein=datein, dateout=dateout)
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)

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
    email = parameters['email']
    timestamp = parameters['timestamp']

    try:
        with transaction.atomic():
            if not User.objects.filter(email=email).exists():
                return Response('The user does not exist in the system', status=status.HTTP_400_BAD_REQUEST)
            Policy_Consent.objects.create(policy_id=policyid, consent=consent, email=email, timestamp=timestamp)
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)


'''
    List consent information
'''
@csrf_exempt
@api_view(('GET',))
def listConsent(request):
    email = request.GET['email']

    consent_info = Policy_Consent.objects.filter(email=email)
    response = []
    for c in consent_info:
        response.append({'policyid':c.policy_id, 'consent': c.consent, 'timestamp': c.timestamp})

    return JsonResponse({'email': email, 'consents':response}, status=status.HTTP_201_CREATED)


'''
TESTED
##################################################################################################
NOT TESTED
'''


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
    Correlate devices data and user
'''
@csrf_exempt
@api_view(('POST',)) #TODO: post or get
def userData(request):
    parameters = json.loads(request.body)
    id_stay = parameters['id']

    qs = Stay_Data.objects.get(id=id_stay)
    dataIn = qs.datain
    dataOut = qs.dataOut

    query = 'from(bucket:"cassiopeiainflux") |> range(start: dataIn, stop: dataOut)'

    result = settings.clientInflux.query_api().query(org='it', query=query)
    results = [] #TODO se for para guardar os dados alterar para create na db

    for table in result:
        for record in table.records:
            results.append((record.get_value(), record.get_field()))


'''
    Remove user data of the influxdb by stay
'''
@csrf_exempt
@api_view(('POST',)) # TODO: check if it is a post or get
def removeDataUser(request):
    parameters = json.loads(request.body)
    id_stay = parameters['id']

    try:
        qs = Stay_Data.objects.get(id=id_stay)
        dateIn = qs.datein
        dateOut = qs.dateOut
        try:
            query = 'influx delete --bucket cassiopeiainflux --start dateIn --stop dateOut'
            settings.clientInflux.query_api().query(org='it', query=query)
        except:
            return Response('Cannot remove the data', status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response('ID stay does not exit', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)

'''
    Export personal data to a CSV
'''
@csrf_exempt
@api_view(('GET',)) # TODO: check if it is a post or get
def exportCsv(request):
    parameters = json.loads(request.body)
    id_stay = parameters['id']

    qs = Stay_Data.objects.get(id=id_stay)
    dataIn = qs.datain
    dataOut = qs.dataOut

    try:

        query = 'from(bucket:"cassiopeiainflux") |> range(start: dataIn, stop: dataOut)'

        result = settings.clientInflux.query_api().query(org='it', query=query)
        results = []

        for table in result:
            for record in table.records:
                results.append((record.get_value(), record.get_field()))

        with open('data.csv', mode='w') as data_file:
            data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for i in results:
                data_writer.writerow([results[i]])
        return Response('Ok', status=status.HTTP_201_CREATED)
    except:
        return Response('Problem with csv', status=status.HTTP_400_BAD_REQUEST)
    return Response('Problem', status=status.HTTP_400_BAD_REQUEST)


'''
    List data based on the dateIn and dateOut
'''
@csrf_exempt
@api_view(('GET',))
def request_receipt(request):
    datein = request.GET['datein']
    dateout = request.GET['dateout']

    try:
        query = 'from(bucket:"cassiopeiainflux") |> range(start: dataIn, stop: dataOut)'
        result = settings.clientInflux.query_api().query(org='it', query=query)
        results = []

        for table in result:
            for record in table.records:
                results.append((record.get_value(), record.get_field()))
        return JsonResponse({'data':results}, status=status.HTTP_201_CREATED)
    except:
        return Response('Problem to return data', status=status.HTTP_400_BAD_REQUEST)
    
    return Response('Problem', status=status.HTTP_400_BAD_REQUEST)


'''
    List data based on the stayid
'''
@csrf_exempt
@api_view(('GET',))
def request_receipt(request):
    stayid = request.GET['stayid']
    email = request.GET['email']

    try:
        query = 'from(bucket:"cassiopeiainflux") |> filter(fn: (r) =>r.stayid == stayid and r.email == email'
        result = settings.clientInflux.query_api().query(org='it', query=query)
        results = []

        for table in result:
            for record in table.records:
                results.append((record.get_value(), record.get_field()))
        return JsonResponse({'data':results}, status=status.HTTP_201_CREATED)
    except:
        return Response('Problem to return data', status=status.HTTP_400_BAD_REQUEST)
    
    return Response('Problem', status=status.HTTP_400_BAD_REQUEST)




'''
    List all the receipts of the user
'''
@csrf_exempt
@api_view(('GET',))
def request_receipt(request):
    stayid = request.GET['stayid']
    email = request.GET['email']

    idReceipt = Stay_Data.objects.filter(id = stayid, email = email)

    #pedir os recibos ao receipt generator quando isso estiver alterado!

'''
    Return the state of the receipt
'''


'''
    Return active receipts
'''


'''
    Return revoked receipts
'''


'''
    Revoke a receipt
'''


'''
    Remove a receipt after revoked ??
'''


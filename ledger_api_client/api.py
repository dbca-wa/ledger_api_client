from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string, get_template
from rest_framework.decorators import api_view
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from ledger_api_client.mixins import AccountManagementPermissionMixin
from django.conf import settings
from django.template.loader import render_to_string
from ledger_api_client import utils as ledger_api_client_utils
from ledger_api_client import managed_models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Q
import datetime
import json
import requests 
import django
import urllib.request, json
import urllib.parse
import traceback


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

@csrf_exempt
#@api_view(['POST'])
def process_payment(request):

    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}

    context = {}
    cookies = {}
    #url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/preview/'
    url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/payment-details/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    basket_hash = ""

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','csrftoken': request.POST['payment-csrfmiddlewaretoken'],'LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id}
    for post_field in request.POST:
        if post_field == 'payment-csrfmiddlewaretoken':
             myobj['csrfmiddlewaretoken'] = request.POST[post_field]
        else:
            myobj[post_field] = request.POST[post_field]
    resp = ""
    proceed_to_ledger = True
    if 'number' in myobj:
        if len(myobj["number"]) != 16 and 'card' not in myobj:
            context ={"message": "The credit card number you provided is invalid"}
            resp = get_template('payments/payment-details-message.html').render(context)
            proceed_to_ledger = False

    if proceed_to_ledger is True:
        try:
            if myobj["payment_method"] != "card":
                print ("Not a Valid Card")
                context ={"message": "There was issue attempting to process your payment request.  The reason is due to invalid payment method selected."}
                resp = get_template('payments/payment-details-message.html').render(context)
            else:
                # Set payment method first to card
                resp = requests.post(url, data = myobj, cookies=cookies)
                # now process payment
                myobj['action'] = 'place_order'
                resp = requests.post(url, data = myobj, cookies=cookies)
        except Exception as e:
            context ={"message": "There was issue attempting to process your payment request.   Connection to the payment gateway failed please try again later"}
            resp = get_template('payments/payment-details-message.html').render(context)
    else:
        pass
        #resp = "ERROR Attempting to connect payment gateway please try again later"
    return HttpResponse(resp, content_type='plain/html')
    #return HttpResponse(json.dumps(jsondata), content_type='application/json')

@csrf_exempt
def process_refund(request):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    context = {}
    cookies = {}
    api_key = settings.LEDGER_API_KEY
    #url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/preview/'
    url = settings.LEDGER_API_URL+'/ledgergw/remote/process_refund/'+api_key+'/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    basket_hash = ""

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','csrftoken': request.POST['payment-csrfmiddlewaretoken'],'LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id,}
    for post_field in request.POST:
        if post_field == 'payment-csrfmiddlewaretoken':
             myobj['csrfmiddlewaretoken'] = request.POST[post_field]
        else:
            myobj[post_field] = request.POST[post_field]

    resp = ""
    try:
        resp = requests.post(url, data = myobj, cookies=cookies)
    except Exception as e:
        resp = "ERROR Attempting to connect payment gateway please try again later"
    return HttpResponse(resp, content_type='application/json')

@csrf_exempt
def process_zero(request):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    context = {}
    cookies = {}
    api_key = settings.LEDGER_API_KEY
    #url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/preview/'
    url = settings.LEDGER_API_URL+'/ledgergw/remote/process_zero/'+api_key+'/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    basket_hash = ""

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','csrftoken': request.POST['payment-csrfmiddlewaretoken'],'LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id,} 
    for post_field in request.POST:
        if post_field == 'payment-csrfmiddlewaretoken':
             myobj['csrfmiddlewaretoken'] = request.POST[post_field]
        else:
            myobj[post_field] = request.POST[post_field]

    resp = ""
    try:
        resp = requests.post(url, data = myobj, cookies=cookies)
    except Exception as e:
        resp = "ERROR Attempting to connect payment gateway please try again later"
    return HttpResponse(resp, content_type='application/json')


@csrf_exempt
def process_no(request):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    context = {}
    cookies = {}
    api_key = settings.LEDGER_API_KEY
    #url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/preview/'
    url = settings.LEDGER_API_URL+'/ledgergw/remote/process_no/'+api_key+'/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    basket_hash = ""

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','csrftoken': request.POST['payment-csrfmiddlewaretoken'],'LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id,}
    for post_field in request.POST:
        if post_field == 'payment-csrfmiddlewaretoken':
             myobj['csrfmiddlewaretoken'] = request.POST[post_field]
        else:
            myobj[post_field] = request.POST[post_field]

    resp = ""
    try:
        resp = requests.post(url, data = myobj, cookies=cookies)
    except Exception as e:
        resp = "ERROR Attempting to connect payment gateway please try again later"
    return HttpResponse(resp, content_type='application/json')

@csrf_exempt
def get_card_tokens(request):
    django_version = float(str(django.VERSION[0])+'.'+str(django.VERSION[1]))
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    context = {}
    cookies = {}
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/get-card-tokens/'+api_key+'/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    basket_hash = ""

    user_logged_in = None
    if django_version > 1.11:
          is_authen = request.user.is_authenticated
    else: 
          is_authen = request.user.is_authenticated()

    if is_authen:
           user_logged_in = request.user.id

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          #cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','csrftoken': request.POST['payment-csrfmiddlewaretoken'],'LEDGER_API_KEY': api_key,}
          cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id, 'user_logged_in' : user_logged_in}
    for post_field in request.POST:
        if post_field == 'payment-csrfmiddlewaretoken':
            myobj['csrfmiddlewaretoken'] = request.POST[post_field]
        else:
            myobj[post_field] = request.POST[post_field]

    resp = ""
    try:
        resp = requests.post(url, data = myobj, cookies=cookies)
    except Exception as e:
        resp = "ERROR Attempting to connect payment gateway please try again later"
    return HttpResponse(resp, content_type='application/json')


@csrf_exempt
def delete_card_token(request, card_token_id):
    django_version = float(str(django.VERSION[0])+'.'+str(django.VERSION[1]))
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    context = {}
    cookies = {}
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/delete-card-token/'+api_key+'/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    basket_hash = ""

    user_logged_in = None
    if django_version > 1.11:
          is_authen = request.user.is_authenticated
    else: 
          is_authen = request.user.is_authenticated()

    if is_authen:
           user_logged_in = request.user.id

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          #cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','csrftoken': request.POST['payment-csrfmiddlewaretoken'],'LEDGER_API_KEY': api_key,}
          cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id, 'card_token_id': card_token_id, 'user_logged_in' : user_logged_in}
    for post_field in request.POST:
        if post_field == 'payment-csrfmiddlewaretoken':
            myobj['csrfmiddlewaretoken'] = request.POST[post_field]
        else:
            myobj[post_field] = request.POST[post_field]

    resp = ""
    try:
        resp = requests.post(url, data = myobj, cookies=cookies)
    except Exception as e:
        resp = "ERROR Attempting to connect payment gateway please try again later"
    return HttpResponse(resp, content_type='application/json')

@csrf_exempt
def store_card(request):
    django_version = float(str(django.VERSION[0])+'.'+str(django.VERSION[1]))
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    context = {}
    cookies = {}
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/create-store-card-token/'+api_key+'/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    data = json.load(request)
    payload = data.get('payload')      

    user_logged_in = None
    if django_version > 1.11:
          is_authen = request.user.is_authenticated
    else: 
          is_authen = request.user.is_authenticated()

    if is_authen:
           user_logged_in = request.user.id

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          cookies = {'sessionid': payment_session, 'no_header': 'true', 'payment_api_wrapper': 'true','LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id, 'user_logged_in' : user_logged_in, 'payload': json.dumps(payload)}
    # for post_field in request.POST:
    #     if post_field == 'payment-csrfmiddlewaretoken':
    #         myobj['csrfmiddlewaretoken'] = request.POST[post_field]
    #     else:
    #         myobj[post_field] = request.POST[post_field]

    resp = ""
    try:
        print ("START")
        print (url)
        resp = requests.post(url, data = myobj, cookies=cookies)
        print (resp.text)
    except Exception as e:
        print (e)
        resp = "ERROR Attempting to connect payment gateway please try again later"
    return HttpResponse(resp, content_type='application/json')

@csrf_exempt
def set_primary_card(request):
    django_version = float(str(django.VERSION[0])+'.'+str(django.VERSION[1]))
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    context = {}
    cookies = {}
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/set-primary-card/'+api_key+'/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    data = json.load(request)
    payload = data.get('payload')      

    user_logged_in = None
    if django_version > 1.11:
          is_authen = request.user.is_authenticated
    else: 
          is_authen = request.user.is_authenticated()

    if is_authen:
           user_logged_in = request.user.id

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          cookies = {'sessionid': payment_session, 'no_header': 'true', 'payment_api_wrapper': 'true','LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id, 'user_logged_in' : user_logged_in, 'payload': json.dumps(payload)}

    resp = ""
    try:
        resp = requests.post(url, data = myobj, cookies=cookies)
        print (resp.text)
    except Exception as e:
        print (e)
        resp = "ERROR Attempting to connect payment gateway please try again later"
    return HttpResponse(resp, content_type='application/json')



@csrf_exempt
def store_card_old(request):

    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}

    context = {}
    cookies = {}
    url = settings.LEDGER_API_URL+'/ledgergw/remote/create-store-card-token/'
    project_code = settings.PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE
    system_id = settings.PAYMENT_INTERFACE_SYSTEM_ID
    api_key = settings.LEDGER_API_KEY
    payment_session = None
    basket_hash = ""

    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          basket_hash = request.session.get('basket_hash')
          cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id}
    for post_field in request.POST:
        if post_field == 'payment-csrfmiddlewaretoken':
             myobj['csrfmiddlewaretoken'] = request.POST[post_field]
        else:
            myobj[post_field] = request.POST[post_field]
    resp = ""
    proceed_to_ledger = True
    if 'number' in myobj:
        if len(myobj["number"]) != 16 and 'card' not in myobj:
            context ={"message": "The credit card number you provided is invalid"}
            resp = get_template('payments/payment-details-message.html').render(context)
            proceed_to_ledger = False

    if proceed_to_ledger is True:
        try:
            if myobj["payment_method"] != "card":
                print ("Not a Valid Card")
                context ={"message": "There was issue attempting to store your card.  The reason is due to invalid payment method selected."}
                resp = get_template('payments/payment-details-message.html').render(context)
            else:
                # Set payment method first to card
                resp = requests.post(url, data = myobj, cookies=cookies)
                # now process payment
                #myobj['action'] = 'place_order'
                #resp = requests.post(url, data = myobj, cookies=cookies)
        except Exception as e:
            context ={"message": "There was issue attempting to store your card.   Connection to the payment gateway failed please try again later"}
            resp = get_template('payments/payment-details-message.html').render(context)
    else:
        pass        
    return HttpResponse(resp, content_type='plain/html')
 
def get_settings(request):
    resp = {'status': 200, 'data': {}, 'message': '', 'config': settings.LEDGER_UI_ACCOUNTS_MANAGEMENT}
    return HttpResponse(json.dumps(resp), content_type='application/json')

def get_organisation_settings(request):
    resp = {'status': 200, 'data': {}, 'message': '', 'config': settings.LEDGER_UI_ORGANISATION_MANAGEMENT}
    return HttpResponse(json.dumps(resp), content_type='application/json')

def get_countries(request):
    resp = {'status': 404, 'data': {}, 'message': ''}
    json_response = {}
    url = settings.LEDGER_API_URL+"/ledgergw/public/api/get-countries"
    data = {}
    cache_name = "cache:"+url
    countries_cache = cache.get(cache_name)
    if countries_cache is None:
       try:
           ledger_resp = requests.get(url)
           json_response = ledger_resp.json()
           resp['status'] = 200
           resp['data'] = json_response['data']
           cache.set(cache_name, json.dumps(json_response['data']), 86400)
       except Exception as e:
            print (e)
            raise ValidationError('Error: Unable to create basket session - unable to connect to payment gateway')
    else:
       countries_loads = json.loads(countries_cache)
       resp['status'] = 200
       resp['data'] = countries_loads

    return HttpResponse(json.dumps(resp), content_type='application/json')


def update_organisation_details(request,org_id):
    resp = {'status': 404, 'data': {}, 'message': ''}
    json_response = {}
    api_key = settings.LEDGER_API_KEY
    data = json.load(request)
    payload = data.get('payload')    
    org_obj = payload
    org_obj["organisation_id"] = org_id
  
    resp_ledger = ledger_api_client_utils.update_organisation_obj(org_obj)
    try:
        if resp_ledger['status'] == 200: 
            resp['status'] = resp_ledger['status']
            resp['message'] = resp_ledger['message']
    except Exception as e:
        print (resp_ledger)
        print (e)
        resp = {'status': 500, 'data': {}, 'message': str(e)}
        
    return HttpResponse(json.dumps(resp), content_type='application/json', status=resp['status'])  

def get_organisation_details(request, org_id):
    resp = {'status': 404, 'data': {}, 'message': ''}

    ex_locals = {}
    allow_access = False
    is_authen = request.user.is_authenticated
    if is_authen:
        # allow_access = True
        if settings.ORGANISATION_PERMISSION_MODULE is not None:
            # To configure permissions create a new file called permission.py in your system directory with the following function. Modify the funcation to restrict the access correctly. 
            # def organisation_permissions(request, org_id):
            #                
            #    if orguser is allow access:
            #       return True
            #    else:
            #        return False
            #
            # ORGANISATION_PERMISSION_MODULE = '<system_app_name>.permission'
            # This should be the python path to the python file
            # the def must always be organisation_permissions
            #                 
            perm_module = __import__(settings.ORGANISATION_PERMISSION_MODULE, fromlist=['organisation_permissions'])
            allow_access = perm_module.organisation_permissions(request, org_id)               

    if allow_access is True:
        try:
            resp["data"] = ledger_api_client_utils.get_organisation(org_id)
            resp['status'] = 200
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))           

    # with urllib.request.urlopen(settings.LEDGER_API_URL+"/ledgergw/remote/organisationid/"+org_id+"/"+settings.LEDGER_API_KEY+"/", data) as url:
    #     json_response = json.loads(url.read().decode())

    return HttpResponse(json.dumps(resp), content_type='application/json')


def get_account_details(request, user_id):
    resp = {'status': 404, 'data': {}, 'message': '', 'config': settings.LEDGER_UI_ACCOUNTS_MANAGEMENT}
    json_response = {}
    data = {}

    #import time
    #time.sleep(3)

    allow_access = False
    is_authen = request.user.is_authenticated
    if is_authen:
        if int(request.user.id) == int(user_id): 
             allow_access = True
        if request.user.is_superuser is True:
             allow_access = True
        if  request.user.is_staff is True:
             allow_access = True

    if allow_access is True:
        with urllib.request.urlopen(settings.LEDGER_API_URL+"/ledgergw/remote/userid/"+user_id+"/"+settings.LEDGER_API_KEY+"/", data) as url:
              json_response = json.loads(url.read().decode())
        resp["information_status"] = json_response['information_status']
        if 'postal_same_as_residential' not in resp['data']:
            resp['data']['postal_same_as_residential'] = False

        for la in settings.LEDGER_UI_ACCOUNTS_MANAGEMENT:
            field_key = list(la.keys())[0]
            resp['data'][field_key] = ''
            if field_key in json_response['user']:
                  resp['data'][field_key] = json_response['user'][field_key]
            resp['status'] = 200

        # personal details validation
        if 'dob' in settings.LEDGER_UI_ACCOUNTS_MANAGEMENT:
            if len(resp['data']['dob']) == 10:
                resp['information_status']["personal_details_completed"] = True
        else:
            resp['information_status']["personal_details_completed"] = True

        # identification details validation
        if 'identification' in settings.LEDGER_UI_ACCOUNTS_MANAGEMENT:
            if len(resp['data']['identification']) == 2:
                resp['information_status']["identification_details_completed"] = True
        else:
            resp['information_status']["identification_details_completed"] = True            
        
        # contact details validation
        if 'phone_number' in resp['data']  or 'mobile_number' in resp['data']:  
            if  resp['data']['mobile_number'] is None:
                resp['data']['mobile_number'] = ''
            if  resp['data']['phone_number'] is None:
                resp['data']['phone_number'] = ''

            if len(resp['data']['mobile_number']) >= 10 or len(resp['data']['phone_number']) >= 10:   
                print ("TRIE")             
                resp['information_status']["contact_details_completed"] = True

        # address validation
        print (resp['data'])
        if 'postal_address' in resp['data']  and 'residential_address' in resp['data']: 
                if len(resp['data']['residential_address']['line1']) < 3 or len(resp['data']['residential_address']['locality']) < 3 or len(resp['data']['residential_address']['postcode']) < 3 or len(resp['data']['residential_address']['state']) < 2:
                    pass
                else:
                    if resp['data']['postal_same_as_residential'] is True:
                        resp['information_status']["address_details_completed"] = True
                    else:
                        if len(resp['data']['postal_address']['line1']) < 3 or len(resp['data']['postal_address']['locality']) < 3 or len(resp['data']['postal_address']['postcode']) < 3 or len(resp['data']['postal_address']['state']) < 2:
                            pass
                        else:
                            resp['information_status']["address_details_completed"] = True
                            
        else:
            if 'postal_address' in resp['data']:
                if len(resp['data']['postal_address']['line1']) < 3 or len(resp['data']['postal_address']['locality']) < 3 or len(resp['data']['postal_address']['postcode']) < 3 or len(resp['data']['postal_address']['state']) < 2:
                    pass
                else:
                    resp['information_status']["address_details_completed"] = True                     
            
            if 'residential_address' in resp['data']:
                if len(resp['data']['residential_address']['line1']) < 3 or len(resp['data']['residential_address']['locality']) < 3 or len(resp['data']['residential_address']['postcode']) < 3 or len(resp['data']['residential_address']['state']) < 2:
                    pass
                else:
                    resp['information_status']["address_details_completed"] = True                       
    else:
        resp['status'] = 403
        resp['message'] = "Denied"

    return HttpResponse(json.dumps(resp), content_type='application/json')

def update_account_details(request,user_id):
    resp = {'status': 404, 'data': {}, 'message': ''}
    json_response = {}
    api_key = settings.LEDGER_API_KEY
    data = json.load(request)
    payload = data.get('payload')

    allow_access = False
    is_authen = request.user.is_authenticated
    if is_authen:
        if request.user.id == int(user_id):
             allow_access = True
        if request.user.is_superuser is True:
             allow_access = True
        if  request.user.is_staff is True:
             allow_access = True

    keys_allowed = []
    if allow_access is True:
        for la in settings.LEDGER_UI_ACCOUNTS_MANAGEMENT:
            field_key = list(la.keys())[0]
            keys_allowed.append(field_key)

        payload_data_keys = list(payload.keys())
        url = settings.LEDGER_API_URL+'/ledgergw/remote/update-userid/'+str(user_id)+'/'+api_key+'/'
        myobj = {}
        myobj["authenticated_ledger_id"] = request.user.id
        for p in payload_data_keys:
            if p in keys_allowed:
               myobj[p] = payload[p]
               if p == 'residential_address':
                    myobj[p] = json.dumps(payload[p])
               if p == 'postal_address':
                    myobj[p] = json.dumps(payload[p])
        #resp = ""
        cookies = ""
        try:
            api_resp = requests.post(url, data = myobj, cookies=cookies)
        except Exception as e:
            print (e)
            resp['status'] = 501
            resp['message'] = "ERROR Attempting to connect payment gateway please try again later"

        resp['status'] = 200
    else:
        resp['status'] = 403
        resp['message'] = "Denied"

    return HttpResponse(json.dumps(resp), content_type='application/json')


class SystemUserAccountsList(AccountManagementPermissionMixin, views.APIView):
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    def enforce_csrf(self, *args, **kwargs):
        '''
        Bypass the CSRF checks altogether
        '''
        pass       
    def clean_string(self,value):
        if value is None:
            value = ""
        return value
    def post(self,request,format=None):
        print ("LOADING")
        # response = HttpResponse(json.dumps({"test": "test"}), content_type='application/json')    
        # return response
        try:
            http_status = status.HTTP_200_OK
            report = None
            pass
            is_auth = True
            if is_auth is True:
            # if helpers.is_account_admin(self.request.user) is True:
                request_body_json = json.loads(request.body.decode("utf-8"))                
                page_length = request_body_json['length']                 
                row_start = request_body_json['start']
                draw = request_body_json['draw']
                order_column_id = ''
                order_direction = ''
                if len(request_body_json['order']) > 0:
                    order_column_id = request_body_json['order'][0]['column']
                    order_direction = request_body_json['order'][0]['dir']

                order_dir = ""
                if order_direction == 'desc':
                    order_dir= "-"

                order_by = ["id",]
                if order_column_id == 0:
                    order_by = [order_dir+'id',]
                if order_column_id == 1:
                    order_by = [order_dir+'first_name', order_dir+'last_name']
                if order_column_id == 2:
                    order_by = [order_dir+'legal_first_name', order_dir+'legal_last_name']               
                if order_column_id == 3:
                    order_by = [order_dir+'legal_dob',]                                        
                if order_column_id == 4:
                    order_by = [order_dir+'email',]

                active = True
                if "active" in request_body_json:
                    active = request_body_json['active']
                search_value = request_body_json['search']['value']

                query = Q()
                query &= Q(is_active=active)
                
                if search_value:
                    if len(search_value) > 0:
                        if search_value.isnumeric() is True:
                            query &= Q(            
                                Q(id=search_value)
                                | Q(phone_number__icontains=search_value)
                                | Q(mobile_number__icontains=search_value)
                            )
                        else:
                            query &= Q(
                                Q(first_name__icontains=search_value) 
                                | Q(last_name__icontains=search_value)
                                | Q(legal_first_name__icontains=search_value)
                                | Q(legal_last_name__icontains=search_value)
                                | Q(email__icontains=search_value)
                          

                            )

                accounts_array= []
                accounts_total = managed_models.SystemUser.objects.all().count()                
                accounts_filtered = managed_models.SystemUser.objects.filter(query).count() 
                accounts_obj = managed_models.SystemUser.objects.filter(query).order_by(*order_by)[row_start:row_start+page_length]

                for acc in accounts_obj:
                    account_row = {}
                    account_row["id"] = acc.id
                    account_row["account_name"] = self.clean_string(acc.first_name) +' '+ self.clean_string(acc.last_name)
                    
                    account_row["legal_name"] = self.clean_string(acc.legal_first_name) + ' '+self.clean_string(acc.legal_last_name)                    
                    
                    account_row["legal_dob"] = ""
                    if acc.legal_dob:
                        account_row["legal_dob"] = acc.legal_dob.strftime("%d/%m/%Y")
        
                    account_row["email"] = acc.email
                    account_row["action"] = "<a class='btn btn-primary btn-sm' href='/ledger-ui/accounts-management/"+str(acc.id)+"/change/'>Change</a>"
                    accounts_array.append(account_row)
                


                # Generate Users
                dt_obj = {  "draw": draw,
                            "recordsTotal": accounts_total,
                            "recordsFiltered": accounts_filtered,                    
                            "data" : accounts_array
                        }
                
                
                
                if dt_obj:
                    response = HttpResponse(json.dumps(dt_obj), content_type='application/json')
                    return response
                else:
                    raise serializers.ValidationError('No report was generated.')
            else:
                 raise serializers.ValidationError('Access Forbidden')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))        
        


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class SystemUserAccountsLogsList(views.APIView,AccountManagementPermissionMixin):
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    def enforce_csrf(self, *args, **kwargs):
        '''
        Bypass the CSRF checks altogether
        '''
        pass

    def clean_string(self,value):
        if value is None:
            value = ""
        return value                
    def post(self,request,pk, format=None):
 
        try:
            http_status = status.HTTP_200_OK
            report = None
            # if helpers.is_account_admin(self.request.user) is True:                
            request_body_json = json.loads(request.body.decode("utf-8"))
            
            page_length = request_body_json['length']                 
            row_start = request_body_json['start']
            draw = request_body_json['draw']       

            order_column_id = ''
            order_direction = ''
            if len(request_body_json['order']) > 0:
                order_column_id = request_body_json['order'][0]['column']
                order_direction = request_body_json['order'][0]['dir']   

            order_dir = ""
            if order_direction == 'desc':
                order_dir= "-"

            query = Q()
            order_by = ["id",]
            if order_column_id == 0:
                order_by = [order_dir+'id',]
            if order_column_id == 1:
                order_by = [order_dir+'change_key',]
            if order_column_id == 2:
                order_by = [order_dir+'change_value',]
            if order_column_id == 3:
                order_by = [order_dir+'change_by',]   
            if order_column_id == 4:
                order_by = [order_dir+'created',]                    


            search_value = request_body_json['search']['value']

            query = Q(systemuser_id=pk)            
            if search_value:
                if len(search_value) > 0:
                    if search_value.isnumeric() is True:
                        query &= Q(            
                            Q(id=search_value)
                        )
                    else:
                        query &= Q(
                            Q(change_key__icontains=search_value) 
                            | Q(change_value__icontains=search_value)                                                          
                        )


            accounts_log_array= []
            accounts_log_total = managed_models.SystemUserChangeLog.objects.all().count()                
            accounts_log_filtered = managed_models.SystemUserChangeLog.objects.filter(query).count() 
            accounts_log_obj = managed_models.SystemUserChangeLog.objects.filter(query).order_by(*order_by)[row_start:row_start+page_length]
            for acc in accounts_log_obj:
                account_log_row = {}
                account_log_row["id"] = acc.id
                account_log_row["systemuser"] = self.clean_string(acc.systemuser.first_name) +' '+ self.clean_string(acc.systemuser.last_name)
                account_log_row["change_key"] = acc.change_key
                account_log_row["change_value"] = acc.change_value
                if acc.change_by:
                    account_log_row["change_by"] = self.clean_string(acc.change_by.first_name) +' '+ self.clean_string(acc.change_by.last_name) + ' ({})'.format(acc.change_by.id)
                else:
                    account_log_row["change_by"] = ''
                account_log_row["created"]  = acc.created.astimezone().strftime("%d %b %Y %H:%M %p")
                accounts_log_array.append(account_log_row)

            # Generate Users
            dt_obj = {  "draw": draw,
                        "recordsTotal": accounts_log_total,
                        "recordsFiltered": accounts_log_filtered,                    
                        "data" : accounts_log_array
                    }
            
            if dt_obj:
                response = HttpResponse(json.dumps(dt_obj), content_type='application/json')
                return response
            else:
                raise serializers.ValidationError('No data was generated.')                
            # else:
            #     raise serializers.ValidationError('Access Forbidden')                                    

        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))                                                            
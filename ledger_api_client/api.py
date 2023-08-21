from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string, get_template
from rest_framework.decorators import api_view
from django.conf import settings
from django.template.loader import render_to_string
from ledger_api_client import utils as ledger_api_client_utils
from django.core.cache import cache
from django.core.exceptions import ValidationError
import datetime
import json
import requests 
import django
import urllib.request, json
import urllib.parse

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



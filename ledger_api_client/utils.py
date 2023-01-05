import re
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import Decimal
import django
import requests
import json 
from decimal import InvalidOperation
from babel.numbers import format_currency
from django.utils.translation import get_language, to_locale
from django.core.cache import cache
from decimal import *

def oracle_parser(): 
    pass

def update_payments():
    pass

def create_basket_session(request, emailuser_id, parameters):
    # emailuser_id use to be request vairable.  This has been 
    # replaced with the user objects.  You will need to change 
    #request to request.user.id for this function
    payment_session = None
    cookies = None 
    print ('AQUI 3')
    if 'payment_session' in request.session:
          payment_session = request.session.get('payment_session')
          cookies = {'sessionid': payment_session}
    no_payment = False
    no_payment_hash = ''
    print ("AQUI 4")
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/create-basket-session/'+api_key+'/'
    myobj = {'parameters': json.dumps(parameters), 'emailuser_id': emailuser_id,}

    try:
        # send request to server to get file
        resp = requests.post(url, data = myobj, cookies=cookies)
    except Exception as e:
         raise ValidationError('Error: Unable to create basket session - unable to connect to payment gateway')

    if int(resp.json()['status']) == 200:
         for c in resp.cookies:
              if c.name ==  'sessionid':
                  request.session['payment_session'] = c.value
                  payment_session = request.session.get('payment_session')

         if 'no_payment' in parameters:
             no_payment = parameters['no_payment']
             if no_payment is None:
                 no_payment = False
             no_payment_hash = str(no_payment)+"|"+str(payment_session)

       

         request.session['basket_hash'] = resp.json()['data']['basket_hash']
         request.session['no_payment_hash'] = no_payment_hash

         return resp.json()['data']['basket_hash']
    else:
        raise ValidationError('Error: Unable to create basket session ') 

def create_checkout_session(request, checkout_parameters):

    django_version = float(str(django.VERSION[0])+'.'+str(django.VERSION[1]))

    checkout_parameters['user_logged_in'] = None
    is_authen = False
    if django_version > 1.11:
          is_authen = request.user.is_authenticated
    else: 
          is_authen = request.user.is_authenticated()
    if is_authen:
           checkout_parameters['user_logged_in'] = request.user.id
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/create-checkout-session/'+api_key+'/'
    myobj = {'checkout_parameters': json.dumps(checkout_parameters),}

    if 'basket_owner' in checkout_parameters:
        pass
    else:
        raise ValidationError('Error: "basket_owner" does not exist in create_checkout_session, this must have matching email user id')
          
    cookies = {}
    if 'payment_session' in request.session:
        payment_session = request.session.get('payment_session')
        cookies = {'sessionid': payment_session}
    session = requests.Session()
    try:
        # send request to server to get file
        resp = requests.post(url, data = myobj, cookies=cookies)
    except Exception as e:
         raise ValidationError('Error: Unable to create basket session - unable to connect to payment gateway')


    if int(resp.json()['status']) == 200:
        for c in resp.cookies:
            if c.name ==  'sessionid':
                 request.session['payment_session'] = c.value
    else:
        raise ValidationError('Error: Unable to create checkout session')    

def process_api_refund(request, basket_parameters, customer_id, return_url, return_preload_url):
    django_version = float(str(django.VERSION[0])+'.'+str(django.VERSION[1]))
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/process-api-refund/'+api_key+'/'
    cookies = {}

    user_logged_in = None
    if django_version > 1.11:
          is_authen = request.user.is_authenticated
    else:
          is_authen = request.user.is_authenticated()
    if is_authen:
          user_logged_in = request.user.id

    myobj = {'basket_parameters': json.dumps(basket_parameters),'customer_id': customer_id, 'return_url': return_url, 'return_preload_url': return_preload_url, 'user_logged_in': user_logged_in}

    try:
        # send request to server to get file
        resp = requests.post(url, data = myobj, cookies=cookies)
        print ("REFUND RES")
        print (resp.text)

    except Exception as e:
         raise ValidationError('Error: trying to process refund.')
    if int(resp.json()['status']) == 200:
        try:
           return resp.json()
        except Exception as e:
           print ("exception on url")
           print (e)
           return {"status": 501, "message": "error processing refund"}
    else:
        raise ValidationError('Error: Unable to create checkout session ')


def process_payment_with_token(request, card_token_id):

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
          cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','csrftoken': request.session['payment_session'],'LEDGER_API_KEY': api_key,}

    myobj = {'payment_method':'card','PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE': project_code,'PAYMENT_INTERFACE_SYSTEM_ID': system_id, 'csrfmiddlewaretoken' : request.session['payment_session'], 'payment_method' : 'card', 'checkout_token' : True, 'card': card_token_id}
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
                context ={"message": "There was issue attempting to process your payment request.  The reason is due to invalid payment method selected."}
            else:
                # Set payment method first to card
                resp = requests.post(url, data = myobj, cookies=cookies)
                # now process payment
                myobj['action'] = 'place_order'
                resp = requests.post(url, data = myobj, cookies=cookies)
                resp_json = {}
                jsondata['status'] = 200
                try: 
                    resp_json = resp.json()
                    jsondata['status'] = resp.json()['status']
                    jsondata['message'] = resp.json()['message']
                except: 
                    jsondata['status'] = 500
        except Exception as e:
            jsondata['status'] = 500
            context ={"message": "There was issue attempting to process your payment request.   Connection to the payment gateway failed please try again later"}
    else:
        pass
        #resp = "ERROR Attempting to connect payment gateway please try again later"
    jsondata['context'] = context
    return jsondata 

def payment_details_checkout(request):
    pass
#/ledger/checkout/checkout/payment-details/


def place_order_submission():
    pass


def use_existing_basket():
    pass

def use_existing_basket_from_invoice():
    pass

def get_invoice_properties(invoice_id):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/get-invoice/'+api_key+'/'
    myobj = {'data': json.dumps({'invoice_id': invoice_id})}
    cookies = {}
    resp = requests.post(url, data = myobj, cookies=cookies)
    resp_json = {}
    try:
        resp_json = resp.json()
        print (resp_json)
    except:
        resp_json = {}
    #print (resp.text)
    return resp_json 

def get_basket_total(basket_id):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/get-basket-total/'+api_key+'/'
    myobj = {'data': json.dumps({'basket_id': basket_id})}
    cookies = {}
    resp = requests.post(url, data = myobj, cookies=cookies)
    resp_json = {}
    try:
        resp_json = resp.json()
    except:
        resp_json = {}
    return resp_json

def get_refund_totals(system_id):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/get_failed_refund_totals/'+api_key+'/'+system_id+'/'
    
    resp = requests.get(url)
    resp_json = {}
    try:
        resp_json = resp.json()
    except:
        resp_json = {}
    return resp_json

def get_or_create(email):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/create_get_emailuser/'+api_key+'/'
    myobj = {'data': json.dumps({'email': email})}
    resp = requests.post(url, data=myobj)
    resp_json = {}
    try:
        print (resp.text)
        resp_json = resp.json()
    except:
        resp_json = {}
    return resp_json

def get_organisation(organisation_id):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/get_organisation/'+api_key+'/'
    myobj = {'data': json.dumps({'organisation_id': organisation_id})}
    resp = requests.post(url, data=myobj)
    resp_json = {}
    try:
        resp_json = resp.json()
    except:
        resp_json = {}
    return resp_json

def create_organisation(organisation_name, organisation_abn):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/create_organisation/'+api_key+'/'
    myobj = {'data': json.dumps({'organisation_name': organisation_name, 'organisation_abn': organisation_abn})}
    resp = requests.post(url, data=myobj)
    resp_json = {}
    try:        
        resp_json = resp.json()
    except:
        resp_json = {}
    return resp_json

def update_organisation(organisation_id, organisation_name, organisation_abn):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/update_organisation/'+api_key+'/'
    myobj = {'data': json.dumps({'organisation_id': organisation_id, 'organisation_name': organisation_name, 'organisation_abn': organisation_abn})}
    resp = requests.post(url, data=myobj)
    resp_json = {}
    try:        
        resp_json = resp.json()
    except:
        resp_json = {}
    return resp_json

def get_organisation(organisation_id):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/get_organisation/'+api_key+'/'
    myobj = {'data': json.dumps({'organisation_id': organisation_id,})}
    resp = requests.post(url, data=myobj)
    resp_json = {}
    try:
        resp_json = resp.json()
    except:
        resp_json = {}
    return resp_json

def get_primary_card_token_for_user(user_id):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/check-user-primary-card/'+api_key+'/'
    myobj = {'data': json.dumps({'user_id': user_id,})}
    resp = requests.post(url, data=myobj)
    resp_json = {}
    print (resp)
    print (resp.text)
    try:
        resp_json = resp.json()
        print (resp_json)
    except:
        resp_json = {}
    return resp_json


class OrderObject():
     def __init__(self):
           self.id = None
           self.number = None
           self.user_id = None
           

class Order:
     class objects:
         def get(**kwargs):
             api_key = settings.LEDGER_API_KEY
             url = settings.LEDGER_API_URL+'/ledgergw/remote/get_order_info/'+api_key+'/'
             myobj = {'data': json.dumps(kwargs)}
             cookies = {}
             session = requests.Session()
             # send request to server to get file
             resp = requests.post(url, data = myobj, cookies=cookies)
             o = OrderObject()
             o.id = resp.json()['data']['order']['id']
             o.number = resp.json()['data']['order']['number']
             o.user_id = resp.json()['data']['order']['user_id']
             
             return o 

class OrderLineObject():
    def __init__(self):
        self.id = None
        self.title = None
        self.oracle_code = None
        self.quantity = None
        self.price_incl_tax = None
        self.price_excl_tax = None
        self.paid = None
        self.unit_price_incl_tax = None
        self.unit_price_excl_tax = None

class OrderLine:
      class objects:
          def filter(**kwargs):
               api_key = settings.LEDGER_API_KEY
               url = settings.LEDGER_API_URL+'/ledgergw/remote/get_order_lines/'+api_key+'/'
               myobj = {'data': json.dumps(kwargs)}
               cookies = {}
               orderlines_array = []
               session = requests.Session()
               resp = requests.post(url, data = myobj, cookies=cookies)
               for ol_e in resp.json()['data']['orderlines']:
                  ol = OrderLineObject()
                  ol.id = ol_e['id']
                  ol.title = ol_e['title']
                  ol.oracle_code = ol_e['oracle_code']
                  ol.quantity = ol_e['quantity']
                  ol.price_incl_tax = Decimal(ol_e['price_incl_tax'])
                  ol.price_excl_tax = Decimal(ol_e['price_excl_tax'])
                  ol.unit_price_incl_tax = Decimal(ol_e['unit_price_incl_tax'])
                  ol.unit_price_excl_tax = Decimal(ol_e['unit_price_excl_tax'])
                  ol.paid = Decimal(ol_e['paid'])
                  orderlines_array.append(ol)
               return orderlines_array


def calculate_excl_gst(amount):
    TWELVEPLACES = Decimal(10) ** -12
    getcontext().prec = 22
    result = (Decimal(100.0) / Decimal(100 + settings.LEDGER_GST) * Decimal(amount)).quantize(TWELVEPLACES)
    return result

#@register.filter(name='currency')
def currency(value, currency=None):
    """
    Format decimal value as currency
    """
    try:
        value = Decimal(value)
    except (TypeError, InvalidOperation):
        return u""
    # Using Babel's currency formatting
    # http://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency
    OSCAR_CURRENCY_FORMAT = getattr(settings, 'OSCAR_CURRENCY_FORMAT', None)
    kwargs = {
        'currency': currency or settings.OSCAR_DEFAULT_CURRENCY,
        'locale': to_locale(get_language() or settings.LANGUAGE_CODE)
    }
    if isinstance(OSCAR_CURRENCY_FORMAT, dict):
        kwargs.update(OSCAR_CURRENCY_FORMAT.get(currency, {}))
    else:
        kwargs['format'] = OSCAR_CURRENCY_FORMAT
    return format_currency(value, **kwargs)


def get_system_group_user_by_name(system_group_name):
    from ledger_api_client import managed_models

    permission_list = []
    cache_name_pl = "managed_models.SystemGroup.objects.filter(name="+str(system_group_name)+")"
    pl_cache = cache.get(cache_name_pl)
    if pl_cache is None:
        system_groups = managed_models.SystemGroup.objects.filter(name=system_group_name)
        for sg in system_groups:
            for u in managed_models.SystemGroupPermission.objects.filter(system_group=sg,active=True):
                permission_list.append({"id":u.id, "emailuser_id" : u.emailuser.id,})
                cache.set(cache_name_pl,json.dumps(permission_list), 86400)
    else:
        permission_list = json.loads(pl_cache)

    return permission_list


def user_in_system_group(email_user_id, system_group_name):

    system_group_list = get_system_group_user_by_name(system_group_name)
    for sgl in system_group_list:
         if email_user_id == sgl['emailuser_id']:
              return True
    return False


class FakeRequestSessionObj():
     def __init__(self):
         self.session = {}
         self.user = None
         pass

     def __getitem__(self, item):
         return self.session[item]

     def build_absolute_uri(self):
         return ''


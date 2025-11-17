from django.conf import settings
from django.core.cache import cache
from ledger_api_client import managed_models
#from ledger.payments import models as ledger_payments_models
import logging
logger = logging.getLogger(__name__)

def is_valid_system(system_id):
    ''' Check if the system is in the itsystems register.
    :return: Boolean
    '''
    system_id_zeroed=system_id.replace('S','0')
    return system_id
    #ois = ledger_payments_models.OracleInterfaceSystem.objects.filter(system_id=system_id_zeroed,enabled=True)
    ois = oracle_interface_system(system_id_zeroed)
    #if ois.count() > 0:
    #    return ois[0].system_id
    #elif settings.VALID_SYSTEMS:
    #    return system_id in settings.VALID_SYSTEMS
    #else:
    #    logger.warn('VALID_SYSTEMS not set, ledger.payments.helpers.is_valid_system will always return true')
    #    return True


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    print ("ledger-api-client-belongs_to")
    return user.groups().filter(name=group_name).exists()


def is_payment_admin(user):
    print ("(ledger-api-client-is_payment_admin")
    return user.is_authenticated and (belongs_to(user, settings.PAYMENT_OFFICERS_GROUP) or user.is_superuser)

def is_payment_admin_cached(request, user):
    print ("(ledger-api-client-is_payment_admin")  
    session_key = request.session.session_key

    if session_key is not None:
        is_payment_admin_value = cache.get('is_payment_admin'+str(user.id)+'session_key:'+session_key)
        if is_payment_admin_value is None:            
            is_payment_admin_value = user.is_authenticated and (belongs_to(user, settings.PAYMENT_OFFICERS_GROUP) or user.is_superuser)
            cache.set('is_payment_admin'+str(user.id)+'session_key:'+session_key, is_payment_admin_value, 3600)                        
        return is_payment_admin_value
    else:
        return False

def oracle_interface_system(system_id):
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/remote/oracle-interface-system/'+api_key+'/'
    myobj = {'data': json.dumps({'system_id': system_id})}
    cookies = {}
    resp = requests.post(url, data = myobj, cookies=cookies)
    resp_json = {}
    try:
        resp_json = resp.json()
    except:
        resp_json = {}
    return resp_json

            
from django import http, VERSION
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.db.models import signals
from django.utils.deprecation import MiddlewareMixin
import urllib.request, json
import urllib.parse
from django.contrib import messages
# from confy import env
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from ledger_api_client import managed_models
from ledger_api_client import utils
import datetime

class SSOLoginMiddleware(MiddlewareMixin):

    def process_request(self, request):
       
        if request.path.startswith('/static') or request.path.startswith('/favicon') or request.path.startswith('/media'):
             pass
        else:
             pass
             User = get_user_model()
             ENABLE_DJANGO_LOGIN=settings.ENABLE_DJANGO_LOGIN
             
             SESSION_EXPIRY_SSO = 3600
             if settings.SESSION_EXPIRY_SSO:
                 SESSION_EXPIRY_SSO = settings.SESSION_EXPIRY_SSO
             if (request.path.startswith('/logout') or request.path.startswith('/ledger/logout')) \
                         and 'HTTP_X_LOGOUT_URL' in request.META and request.META['HTTP_X_LOGOUT_URL']:
                 print ("LOGGING OUT")
                 if 'is_authenticated' in request.session:
                      del request.session['is_authenticated']
                 if 'user_obj' in request.session:
                      del request.session['user_obj']
                 logout(request)
                 return http.HttpResponseRedirect(request.META['HTTP_X_LOGOUT_URL'])

             if VERSION < (2, 0):
                 user_auth = request.user.is_authenticated()
             else:
                 try:
                     user_obj = {'email': None, 'first_name': None, "last_name": None, "user_id" : None, 'is_staff': False}
                     is_authenticated = None
                     if 'is_authenticated' in request.session and 'user_obj' in request.session:
                          #request.session['is_authenticated'] = request.user.is_authenticated
                          is_authenticated = request.session['is_authenticated']
                          user_obj = request.session['user_obj']
                     
                     if is_authenticated is None:
                          is_authenticated = request.user.is_authenticated
                          request.session['is_authenticated'] = is_authenticated
                          if is_authenticated is True:
                              user_obj = {'user_id': request.user.id, 'email': request.user.email, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'is_staff': request.user.is_staff}
                              request.session['user_obj'] = user_obj
                     user_auth = is_authenticated
                     #user_auth = user_obj.is_authenticated
                     if user_auth is True:
                          pass
                          if ENABLE_DJANGO_LOGIN is True:
                              if 'HTTP_REMOTE_USER' in request.META:
                                   if len(request.META['HTTP_REMOTE_USER']) > 3:
                                         response = HttpResponse("<center><h1 style='font-family: Arial, Helvetica, sans-serif;'>Error: SSO detected as enabled.  ENABLE_DJANGO_LOGIN should be set to False when sso is enabled.</h1><br></center><script></script>")
                                         return response 
                          else:
                              pass
                              #if request.user.email.lower() != request.META['HTTP_REMOTE_USER'].lower():
                              if user_obj['email'].lower() != request.META['HTTP_REMOTE_USER'].lower():
                                  response = HttpResponse("<center><h1 style='font-family: Arial, Helvetica, sans-serif;'>Wait one moment please...</h1><br><img src='/static/ledger_api/images/ajax-loader-spinner.gif'></center><script> location.reload();</script>")
                                  response.delete_cookie('sessionid')
                                  return response
                 except:
                     print ("user_auth request user does not exist")
                     response = HttpResponse("<center><h1 style='font-family: Arial, Helvetica, sans-serif;'>Wait one moment please...</h1><br><img src='/static/ledger_api/images/ajax-loader-spinner.gif'></center><script> location.reload();</script>")
                     response.delete_cookie('sessionid')
                     return response
            
             if user_auth:                        
                 if request.META:
                      if 'HTTP_REMOTE_USER' in request.META:
                           if 'HTTP_X_FIRST_NAME' in request.META:
                               if user_obj['first_name'] !=  request.META['HTTP_X_FIRST_NAME']:
                                    user_auth = False
                           if 'HTTP_X_LAST_NAME' in request.META:
                               if user_obj['last_name'] != request.META['HTTP_X_LAST_NAME']:
                                    user_auth = False


             if not user_auth and 'HTTP_REMOTE_USER' in request.META and request.META['HTTP_REMOTE_USER']:
                 attributemap = {
                     'username': 'HTTP_REMOTE_USER',
                     'last_name': 'HTTP_X_LAST_NAME',
                     'first_name': 'HTTP_X_FIRST_NAME',
                     'email': 'HTTP_X_EMAIL',
                 }

                 for key, value in attributemap.items():
                     if value in request.META:
                         attributemap[key] = utils.remove_html_tags(request.META[value])

                 if hasattr(settings, 'ALLOWED_EMAIL_SUFFIXES') and settings.ALLOWED_EMAIL_SUFFIXES:
                     allowed = settings.ALLOWED_EMAIL_SUFFIXES
                     if isinstance(settings.ALLOWED_EMAIL_SUFFIXES, basestring):
                         allowed = [settings.ALLOWED_EMAIL_SUFFIXES]
                     if not any([attributemap['email'].lower().endswith(x) for x in allowed]):
                         return http.HttpResponseForbidden()

                 exists_in_ledger = False
                 if attributemap['email'] and User.objects.filter(email__iexact=attributemap['email']).exists():
                     user = User.objects.filter(email__iexact=attributemap['email'])[0]
                     exists_in_ledger = True
                 else:
                     user = User()

                 # connect to ledger and align local cache account

                 json_response = {}
                 try:
                     data = urllib.parse.urlencode(attributemap)
                     data = data.encode('utf-8')
                     with urllib.request.urlopen(settings.LEDGER_API_URL+"/ledgergw/remote/user/"+attributemap['email']+"/"+settings.LEDGER_API_KEY+"/", data) as url:
                           json_response = json.loads(url.read().decode())
                 except Exception as e:
                     print ("Error Connecting to Ledger GW")
                     print (e)
                     response = HttpResponse("<h1>Error Connecting to Ledger GW</h1>")
                     return response

                 if 'user' in json_response:
                     attributemap['ledger_id'] = json_response['user']['ledgerid']
                     attributemap['ledger_data'] = json_response['user']
                     attributemap['is_superuser'] = json_response['user']['is_superuser']
                     attributemap['is_staff'] = json_response['user']['is_staff']
                     attributemap['ledger_groups'] = json_response['user']['groups']
                 else:
                     messages.error(request, 'Unable to Update User Information from Ledger')
                 user.__dict__.update(attributemap)
                 user.save()

                 if exists_in_ledger is False:
                     response = HttpResponse("<center><h1 style='font-family: Arial, Helvetica, sans-serif;'>Wait one moment please</h1><br><img src='/static/ledger_api/images/ajax-loader-spinner.gif'></center><script> location.reload();</script>")
                     response.delete_cookie('sessionid')
                     return response

                 user.backend = 'django.contrib.auth.backends.ModelBackend'
                 request.session.set_expiry(SESSION_EXPIRY_SSO)
                 login(request, user)
                 del request.session['is_authenticated']
                 try:
                    is_authenticated = request.user.is_authenticated
                    request.session['is_authenticated'] = is_authenticated
                    user_obj = {'user_id': request.user.id, 'email': request.user.email, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'is_staff': request.user.is_staff}
                    request.session['user_obj'] = user_obj
                    su = managed_models.SystemUser.objects.filter(email=request.user.email)
                    if su.count() > 0:                        
                        #su_obj = managed_models.SystemUser
                        #su_obj.change_by_user_id = su.id
                        suo = managed_models.SystemUser.objects.get(id=su[0].id)
                        suo.first_name = request.user.first_name
                        suo.last_name = request.user.last_name
                        suo.email = request.user.email
                        suo.last_login = datetime.datetime.now()           
                        suo.ledger_id_id = request.user.id  # Must use _id_id to prevent OneToOne Lookup Issue
                        suo.change_by_user_id = su[0].id           
                        suo.save()                        
                    else:
                        su = managed_models.SystemUser.objects.create(ledger_id=request.user, email=request.user.email ,first_name=request.user.first_name, last_name=request.user.last_name, is_active=True, last_login=datetime.datetime.now())

                 except Exception as e:
                     print ("ERROR in sso middleware logging in")
                     print (e)
                        

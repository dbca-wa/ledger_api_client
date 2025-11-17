import logging
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
#from django.core.urlresolvers import reverse
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from ledger_api_client import ledger_models
from ledger_api_client import managed_models
from ledger_api_client import utils as ledger_api_client_utils
from ledger_api_client import helpers as ledger_api_client_helpers
from ledger_api_client.mixins import InvoiceOwnerMixin, SystemUserPermissionMixin, SystemUserAddressPermissionMixin, AccountManagementPermissionMixin
from ledger_api_client import forms as ledger_api_client_form
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django import forms
# from rest_framework import serializers, status, views as rest_views
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
import traceback

import django
from datetime import datetime, timedelta
#from django.template import Template, Context,RequestContext
#from django.template import loader
from django.template.loader import render_to_string
from decimal import *
import requests
import json
from django.views import generic
#from ledger.payments.pdf import create_invoice_pdf_bytes
#from ledger.payments.models import Invoice
#from ledger.payments.mixins import InvoiceOwnerMixin



class PaymentDetailCheckout(TemplateView):
    template_name = 'payments/payment-details.html'

    def get(self, request, *args, **kwargs):
        # if page is called with ratis_id, inject the ground_id
        context = {'settings': settings}
        cookies = {}
        api_key = settings.LEDGER_API_KEY
        url = None
        payment_total = Decimal('0.00')
        payment_session = None
        basket_hash = ""

        if 'payment_session' in request.session:
              payment_session = request.session.get('payment_session')
              no_payment_hash = request.session.get('no_payment_hash')
              basket_hash = request.session.get('basket_hash')
              basket_hash_split = basket_hash.split("|")
              basket_totals = ledger_api_client_utils.get_basket_total(basket_hash_split[0])
              if 'data' in basket_totals:
                  if 'basket_total' in basket_totals['data']:
                        payment_total = Decimal(basket_totals['data']['basket_total'])

              cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true','LEDGER_API_KEY': api_key}

        myobj = {'payment_method':'card',}
        # send request to server to get file
        # allow_redirects=False
        try:
             if "True|"+payment_session == no_payment_hash:
                   url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/payment-no/'
             else:
                   if payment_total > 0:
                         url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/payment-details/'
                   elif payment_total < 0:
                         url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/payment-refund/'
                   elif payment_total == 0:
                         url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/payment-zero/'

             resp = requests.get(url, data = myobj, cookies=cookies)
             context['data'] = resp.text
        except Exception as e:
            context['data'] = render_to_string('payments/gateway-error.html', {'error': 'There was an error connecting to the Payment Gateway please try again later','settings': settings},)             
             #context['data'] = "There was error connecting to the Payment Gateway please try again later"
        return render(request, self.template_name, context)


class PayInvoice(TemplateView):
    template_name = 'payments/pay-invoice.html'

    def get(self, request, *args, **kwargs):
        # if page is called with ratis_id, inject the ground_id

        if request.user.is_staff is True:
           # created as an exampe for testing purposes to generating a payment session for future invoices.
           context = {'settings': settings}
           invoice_reference = self.kwargs['reference']
           return_url = settings.PARKSTAY_EXTERNAL_URL+'/success/'
           fallback_url = settings.PARKSTAY_EXTERNAL_URL+'/fallback_url/'
           payment_session = ledger_api_client_utils.generate_payment_session(request,invoice_reference, return_url, fallback_url)
           context['data'] = payment_session

        return render(request, self.template_name, context)


class AccountsView(TemplateView):

    template_name = 'ledgerui/accounts.html'
    def get(self, request, *args, **kwargs):
        context = {'settings': settings}
        return render(request, self.template_name, context)
    
class AccountsFirstTimeView(TemplateView):

    template_name = 'ledgerui/accounts_firsttime.html'
    def get(self, request, *args, **kwargs):
        context = {'settings': settings, 'firsttime': True}
        return render(request, self.template_name, context)



class OrganisationView(TemplateView):

    template_name = 'ledgerui/organisation.html'
    def get(self, request, *args, **kwargs):
        org_id = kwargs['pk']
        context = {'settings': settings, 'org_id': org_id}        
        return render(request, self.template_name, context)

class SystemAccountsView(LoginRequiredMixin, TemplateView):

    template_name = 'ledgerui/system_accounts.html'
    
    def get(self, request, *args, **kwargs):
        context = {'settings': settings,'system_user_id' : None, 'ledger_user_id': None}
        system_user_id = None

        if request.user.is_authenticated is True:
            su = managed_models.SystemUser.objects.filter(ledger_id=request.user.id)
            if su.count() > 0:
                system_user_id = su[0].id 
            else:
                su = managed_models.SystemUser.objects.create(ledger_id=request.user, email=request.user.email, first_name=request.user.first_name, last_name=request.user.last_name)
                system_user_id = su.id
            context['system_user_id'] = system_user_id
            context['ledger_user_id'] = request.user.id
        return render(request, self.template_name, context)
    
    def get_permissions(self):
        return False

class SystemAccountsFirstTimeView(LoginRequiredMixin, TemplateView):

    template_name = 'ledgerui/system_accounts_firsttime.html'
    def get(self, request, *args, **kwargs):
        context = {'settings': settings, 'firsttime': True}
        if request.user.is_authenticated is True:
            su = managed_models.SystemUser.objects.filter(ledger_id=request.user.id)
            if su.count() > 0:
                system_user_id = su[0].id 
            else:
                su = managed_models.SystemUser.objects.filter(email=request.user.email)
                if su.count() > 0:
                   system_user_id = su[0].id                    
                else: 
                    su = managed_models.SystemUser.objects.create(ledger_id=request.user, email=request.user.email, first_name=request.user.first_name, last_name=request.user.last_name)
                    system_user_id = su.id
            context['system_user_id'] = system_user_id
            context['ledger_user_id'] = request.user.id    
        return render(request, self.template_name, context)

# System Accounts Page 
class AccountInformationView(SystemUserPermissionMixin,generic.TemplateView):
    model = managed_models.SystemUser
    # form_class = ledger_api_client_form.PersonalInformationUpdateForm
    template_name = 'ledgerui/crispy_forms/account_information.html'

    def get(self, request, *args, **kwargs):        
        return super(AccountInformationView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AccountInformationView, self).get_context_data(**kwargs)        
        context['request'] = self.request
        context['pk'] = kwargs['pk']
        su =  managed_models.SystemUser.objects.get(id=kwargs['pk'])
        context['system_user'] = su
        return context

# System Accounts Page 
class PersonalInformationUpdate(SystemUserPermissionMixin, generic.UpdateView):
    model = managed_models.SystemUser
    form_class = ledger_api_client_form.PersonalInformationUpdateForm
    template_name = 'ledgerui/crispy_forms/personal_information.html'
    save_success = False
    personal_details_completed = False

    def get(self, request, *args, **kwargs):        
        return super(PersonalInformationUpdate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PersonalInformationUpdate, self).get_context_data(**kwargs)        
        context['pk'] = self.object.id
        context['save_success'] = self.save_success
        context['request'] = self.request            
      
        su =  managed_models.SystemUser.objects.get(id=self.object.id)
        if su.legal_first_name:
            if len(su.legal_first_name) > 0:
                if su.legal_last_name:
                    if len(su.legal_last_name) > 0:
                        if su.legal_dob:
                            self.personal_details_completed = True
        context['personal_details_completed'] = self.personal_details_completed      
        return context

    def get_initial(self):
        initial = super(PersonalInformationUpdate, self).get_initial()                
        initial['account_change_locked'] = self.object.account_change_locked    
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = self.get_object().application_set.first()
            return HttpResponseRedirect(app.get_absolute_url())
        return super(PersonalInformationUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        forms_data = form.cleaned_data

        su = managed_models.SystemUser.objects.filter(ledger_id=self.request.user.id)                
        self.object.change_by_user_id = su[0].id
                                                        
        self.object.save()       
        self.save_success = True
        return render(self.request, self.template_name, self.get_context_data())        

class ContactInformationUpdate(SystemUserPermissionMixin,generic.UpdateView):
    model = managed_models.SystemUser
    form_class = ledger_api_client_form.ContactInformationUpdateForm
    template_name = 'ledgerui/crispy_forms/contact_information.html'
    save_success = False
    contact_details_completed = False

    def get(self, request, *args, **kwargs):
        
        # context = {"pk": kwargs['pk']}
        # context =  {}
        # return render(request, self.template_name, context)
        return super(ContactInformationUpdate, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(ContactInformationUpdate, self).get_context_data(**kwargs)        
        context['pk'] = self.object.id
        context['save_success'] = self.save_success
        context['request'] = self.request
        su =  managed_models.SystemUser.objects.get(id=self.object.id)
        if su.mobile_number:
            if len(su.mobile_number) > 0:            
                self.contact_details_completed = True
        context['contact_details_completed'] = self.contact_details_completed                  
        return context
    
    def get_initial(self):
        initial = super(ContactInformationUpdate, self).get_initial()                
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = self.get_object().application_set.first()
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ContactInformationUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):        
        self.object = form.save(commit=False)
        forms_data = form.cleaned_data
        
        su = managed_models.SystemUser.objects.filter(ledger_id=self.request.user.id)                
        self.object.change_by_user_id = su[0].id

        self.object.save()       
        self.save_success = True
        return render(self.request, self.template_name, self.get_context_data())        

class AddressInformationView(SystemUserPermissionMixin,generic.TemplateView):
    model = managed_models.SystemUserAddress
    template_name = 'ledgerui/crispy_forms/address_information.html'
    address_details_completed = False

    def get(self, request, *args, **kwargs):        
        return super(AddressInformationView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AddressInformationView, self).get_context_data(**kwargs)        
        context['request'] = self.request
        context['pk'] = kwargs['pk']
        su =  managed_models.SystemUser.objects.get(id=kwargs['pk'])
        sua =  managed_models.SystemUserAddress.objects.filter(system_user=kwargs['pk']).order_by('id')
        sua_residential_count =  managed_models.SystemUserAddress.objects.filter(system_user=kwargs['pk'],address_type='residential_address').count()
        sua_postal_count =  managed_models.SystemUserAddress.objects.filter(system_user=kwargs['pk'],address_type='postal_address').count()
        sua_billing_count =  managed_models.SystemUserAddress.objects.filter(system_user=kwargs['pk'],address_type='billing_address').count()

        if sua_residential_count > 0 and sua_postal_count > 0:
            self.address_details_completed = True
        context['system_user'] = su
        context['system_user_address'] = sua
        context['address_details_completed'] = self.address_details_completed
        context['sua_residential_count'] = sua_residential_count
        context['sua_postal_count'] = sua_postal_count
        context['sua_billing_count'] = sua_billing_count
        context['settings'] = settings
        return context

class AddressInformationCreate(SystemUserPermissionMixin,generic.CreateView):
    model = managed_models.SystemUserAddress
    form_class = ledger_api_client_form.AddressInformationUpdateForm
    template_name = 'ledgerui/crispy_forms/address_information_create.html'
    save_success = False
    
    def get(self, request, *args, **kwargs):
        return super(AddressInformationCreate, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(AddressInformationCreate, self).get_context_data(**kwargs)   
        context['pk'] = self.kwargs.get('pk')
        context['save_success'] = self.save_success
        context['request'] = self.request
        context['settings'] = settings
        # su =  managed_models.SystemUser.objects.get(id=self.object.id)
        # if su.mobile_number:
        #     if len(su.mobile_number) > 0:            
        #         self.contact_details_completed = True
        # context['contact_details_completed'] = self.contact_details_completed                  
        return context
    
    def get_initial(self):
        initial = super(AddressInformationCreate, self).get_initial() 
        initial['system_user_id']  = self.kwargs.get('pk')
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = self.get_object().application_set.first()
            return HttpResponseRedirect(app.get_absolute_url())
        return super(AddressInformationCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):        
        self.object = form.save(commit=False)
        forms_data = form.cleaned_data        
        pk = self.kwargs.get('pk')
        
        su = managed_models.SystemUser.objects.filter(id=int(pk))
        if su.count() > 0:
            self.object.system_user = su[0]

        sul = managed_models.SystemUser.objects.filter(ledger_id=self.request.user.id)                                
        self.kwargs.get('pk')
        self.object.change_by_user_id = sul[0].id
        self.object.save()   

        if self.object.use_for_postal is True:
            sua = managed_models.SystemUserAddress()
            sua.change_by_user_id=sul[0].id
            sua.system_user=su[0]
            sua.address_type='postal_address'                                                         
            sua.line1=self.object.line1
            sua.line2=self.object.line2
            sua.line3=self.object.line3
            sua.locality=self.object.locality
            sua.postcode=self.object.postcode
            sua.state=self.object.state
            sua.country=self.object.country
            sua.system_address_link=self.object.id
            sua.save()


        if self.object.use_for_billing is True:                                                                              
            sua = managed_models.SystemUserAddress()
            sua.change_by_user_id=sul[0].id
            sua.system_user=su[0]
            sua.address_type='billing_address'                                                         
            sua.line1=self.object.line1
            sua.line2=self.object.line2
            sua.line3=self.object.line3
            sua.locality=self.object.locality
            sua.postcode=self.object.postcode
            sua.state=self.object.state
            sua.country=self.object.country
            sua.system_address_link=self.object.id
            sua.save()
        self.save_success = True
        return render(self.request, self.template_name, self.get_context_data())  

class AddressInformationEdit(SystemUserAddressPermissionMixin,generic.UpdateView):
    model = managed_models.SystemUserAddress
    form_class = ledger_api_client_form.AddressInformationUpdateForm
    template_name = 'ledgerui/crispy_forms/address_information_edit.html'
    save_success = False
    
    def get(self, request, *args, **kwargs):
        return super(AddressInformationEdit, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(AddressInformationEdit, self).get_context_data(**kwargs)   

        context['pk'] = self.kwargs.get('pk')
        context['system_user_id'] = self.kwargs.get('system_user_id')
        context['save_success'] = self.save_success
        context['request'] = self.request
        context['settings'] = settings
        # su =  managed_models.SystemUser.objects.get(id=self.object.id)
        # if su.mobile_number:
        #     if len(su.mobile_number) > 0:            
        #         self.contact_details_completed = True
        # context['contact_details_completed'] = self.contact_details_completed                  
        return context
    
    def get_initial(self):
        initial = super(AddressInformationEdit, self).get_initial()  
        initial['address_id'] = self.kwargs.get('pk')     
        initial['system_user_id']  = self.kwargs.get('system_user_id')         

        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = self.get_object().application_set.first()
            return HttpResponseRedirect(app.get_absolute_url())
        return super(AddressInformationEdit, self).post(request, *args, **kwargs)

    def form_valid(self, form):        
        self.object = form.save(commit=False)
        forms_data = form.cleaned_data
        pk = self.kwargs.get('pk')
        system_user_id = self.kwargs.get('system_user_id')
        su = managed_models.SystemUser.objects.filter(id=int(system_user_id))           
        sul = managed_models.SystemUser.objects.filter(ledger_id=self.request.user.id) 

        if su.count() > 0:
            self.object.system_user = su[0]

        if self.object.use_for_postal is True:
            if managed_models.SystemUserAddress.objects.filter(system_address_link=self.object.id,address_type='postal_address').count() > 0: 
                sua = managed_models.SystemUserAddress.objects.get(system_address_link=self.object.id,address_type='postal_address')
                sua.change_by_user_id = sul[0].id
                sua.system_user = self.object.system_user
                sua.line1 = self.object.line1
                sua.line2 = self.object.line2
                sua.line3 = self.object.line3
                sua.locality = self.object.locality
                sua.postcode = self.object.postcode
                sua.state = self.object.state
                sua.country = self.object.country
                sua.save()
            else:
                sua = managed_models.SystemUserAddress()
                sua.change_by_user_id=sul[0].id
                sua.system_user=su[0]
                sua.address_type='postal_address'                                                         
                sua.line1=self.object.line1
                sua.line2=self.object.line2
                sua.line3=self.object.line3
                sua.locality=self.object.locality
                sua.postcode=self.object.postcode
                sua.state=self.object.state
                sua.country=self.object.country
                sua.system_address_link=self.object.id
                sua.save()
    
        else:
            
            sua = managed_models.SystemUserAddress.objects.filter(system_address_link=self.object.id,address_type='postal_address')
            for sua_item in sua:
                sua_item.change_by_user_id=sul[0].id
                sua_item.delete()
    

        if self.object.use_for_billing is True:

            if managed_models.SystemUserAddress.objects.filter(system_address_link=self.object.id,address_type='billing_address').count() > 0: 
                sua = managed_models.SystemUserAddress.objects.get(system_address_link=self.object.id,address_type='billing_address')
                sua.change_by_user_id = sul[0].id
                sua.system_user = self.object.system_user
                sua.line1 = self.object.line1
                sua.line2 = self.object.line2
                sua.line3 = self.object.line3
                sua.locality = self.object.locality
                sua.postcode = self.object.postcode
                sua.state = self.object.state
                sua.country = self.object.country
                sua.save()     
            else:            

                sua = managed_models.SystemUserAddress()
                sua.change_by_user_id=sul[0].id
                sua.system_user=su[0]
                sua.address_type='billing_address'                                                         
                sua.line1=self.object.line1
                sua.line2=self.object.line2
                sua.line3=self.object.line3
                sua.locality=self.object.locality
                sua.postcode=self.object.postcode
                sua.state=self.object.state
                sua.country=self.object.country
                sua.system_address_link=self.object.id
                sua.save()                
        else:
            sua = managed_models.SystemUserAddress.objects.filter(system_address_link=self.object.id,address_type='billing_address')                       
            for sua_item in sua:
                sua_item.change_by_user_id=sul[0].id
                sua_item.delete()

        self.kwargs.get('pk')
        self.object.change_by_user_id=sul[0].id
        self.object.save()       
        self.save_success = True
        return render(self.request, self.template_name, self.get_context_data())  


class AddressInformationDelete(SystemUserAddressPermissionMixin,generic.UpdateView):
    model = managed_models.SystemUserAddress
    form_class = ledger_api_client_form.AddressInformationDeleteForm
    template_name = 'ledgerui/crispy_forms/address_information_delete.html'
    save_success = False
    
    def get(self, request, *args, **kwargs):
        return super(AddressInformationDelete, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(AddressInformationDelete, self).get_context_data(**kwargs)   

        context['pk'] = self.kwargs.get('pk')
        context['system_user_id'] = self.kwargs.get('system_user_id')
        context['save_success'] = self.save_success
        context['request'] = self.request
        # su =  managed_models.SystemUser.objects.get(id=self.object.id)
        # if su.mobile_number:
        #     if len(su.mobile_number) > 0:            
        #         self.contact_details_completed = True
        # context['contact_details_completed'] = self.contact_details_completed                  
        return context
    
    def get_initial(self):
        initial = super(AddressInformationDelete, self).get_initial()                
        return initial

    def post(self, request, *args, **kwargs):

        # if request.POST.get('Cancel'):
        #     print ("CANCELLING")
        #     return HttpResponse("<script>$('#id_create_edit_address_information_modal').modal('hide');</script>")
        #     app = self.get_object().application_set.first()
        #     return HttpResponseRedirect(app.get_absolute_url())
        return super(AddressInformationDelete, self).post(request, *args, **kwargs)

    def form_valid(self, form):        
        self.object = form.save(commit=False)
        forms_data = form.cleaned_data
        sul = managed_models.SystemUser.objects.filter(ledger_id=self.request.user.id) 

        sua = managed_models.SystemUserAddress.objects.filter(system_address_link=self.object.id,address_type='postal_address')
        for sua_item in sua:
            sua_item.change_by_user_id=sul[0].id
            sua_item.delete()
        
        
        sua = managed_models.SystemUserAddress.objects.filter(system_address_link=self.object.id,address_type='billing_address')
        for sua_item in sua:
            sua_item.change_by_user_id=sul[0].id
            sua_item.delete()

        self.object.change_by_user_id=sul[0].id
        self.object.delete()
        # managed_models.SystemUserAddress.objects.filter(id=self.object.id).delete()                
        self.save_success = True
        return render(self.request, self.template_name, self.get_context_data())  
    
class AccountsManagementView(AccountManagementPermissionMixin, TemplateView):

    template_name = 'ledgerui/accounts-management.html'
    def get(self, request, *args, **kwargs):
        context = {'settings': settings, }
        return render(request, self.template_name, context)

class RobotView(TemplateView):

    template_name = 'ledgerui/robot.txt'

    def get(self, request, *args, **kwargs):
        context = {'settings': settings}
        return render(request, self.template_name, context,content_type="text/plain")



class InvoicePDFView(InvoiceOwnerMixin, generic.View):
    def get(self, request, *args, **kwargs):
        api_key = settings.LEDGER_API_KEY
        url = settings.LEDGER_API_URL+'/ledgergw/invoice-pdf/'+api_key+'/'+self.kwargs['reference']
        invoice_pdf = requests.get(url=url)
        response = HttpResponse(invoice_pdf.content, content_type='application/pdf')
        return response

    def get_object(self):
        invoice = get_object_or_404(ledger_models.Invoice, reference=self.kwargs['reference'])
        return invoice

class SystemAccountAdd(AccountManagementPermissionMixin, generic.CreateView):
    template_name = 'ledgerui/crispy_forms/system_account_add_admin.html'
    model = managed_models.SystemUser
    form_class = ledger_api_client_form.SystemUserCreateForm
    save_success = False 

    def get(self, request, *args, **kwargs):
        return super(SystemAccountAdd, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(SystemAccountAdd, self).get_context_data(**kwargs)   
        context['pk'] = self.kwargs.get('pk')
        context['save_success'] = self.save_success
        context['request'] = self.request                 
        return context
    
    def get_initial(self):
        initial = super(SystemAccountAdd, self).get_initial()                
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = self.get_object().application_set.first()
            return HttpResponseRedirect(app.get_absolute_url())
        return super(SystemAccountAdd, self).post(request, *args, **kwargs)

    def get_absolute_account_url(self):        
        id = self.object.id
        return "/ledger-ui/accounts-management/{}/change/".format(id)

    def form_valid(self, form):        
        self.object = form.save(commit=False)
        forms_data = form.cleaned_data                              
        self.save_success = True

        su = managed_models.SystemUser.objects.get(ledger_id=self.request.user.id)
        self.object.change_by_user_id = su.id            
        self.object.save()

        return HttpResponseRedirect(self.get_absolute_account_url())
        # return render(self.request, self.template_name, self.get_context_data())  



class SystemAccountChange(AccountManagementPermissionMixin, generic.UpdateView):
   
    template_name = 'ledgerui/crispy_forms/system_account_change_admin.html'
    model = managed_models.SystemUser
    form_class = ledger_api_client_form.SystemUserForm


    def get_initial(self):
        initial = super(SystemAccountChange, self).get_initial()
        person = self.get_object()
        initial['id'] = person.id
        
        # initial['identification2'] = person.identification2

        return initial
    def get_context_data(self, **kwargs):
        ctx = super(SystemAccountChange,self).get_context_data(**kwargs)
        ctx['account_id'] = self.kwargs['pk']
        is_auth = True
        if is_auth is True:
        # if helpers.is_account_admin(self.request.user) is True:
            pass

        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return ctx
    
    def get_absolute_url(self):       
        
        return "/ledger-ui/accounts-management/"

    def get_absolute_account_url(self):        
        id = self.get_object().id
        return "/ledger-ui/accounts-management/{}/change/".format(id)

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):            
            return HttpResponseRedirect(self.get_absolute_url())

        # first_name  = request.POST.get('first_name', '')
        # last_name = request.POST.get('last_name', '')
        
        # if len(first_name) < 1 and len(last_name) < 1:             
        #     messages.error(self.request, "No Given name or last name data")

        return super(SystemAccountChange, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        is_auth = True
        if is_auth is True:
        # if helpers.is_account_admin(self.request.user) is True:
            self.object = form.save(commit=False)
            forms_data = form.cleaned_data
            uservalue_map = {}
            eu = managed_models.SystemUser.objects.filter(id=self.object.id).values()
            
            for e in eu[0].keys():
                uservalue_map[e] = eu[0][e]            
 
            # if 'identification2_id' in uservalue_map:
            #     if uservalue_map['identification_id'] is not None:
            #         self.object.identification2 = PrivateDocument.objects.get(id=uservalue_map['identification2_id'])

            # identification2_filechanged = False
            # if 'identification2_json' in self.request.POST:
            
            #     try:
            #         json_data = json.loads(self.request.POST['identification2_json'])
            #         if self.object.identification2:
            #             if self.object.identification2.id != int(json_data['doc_id']):
            #                 doc = PrivateDocument.objects.get(id=int(json_data['doc_id']))
            #                 self.object.identification2 = doc
            #                 identification2_filechanged = True
            #         else:
            #             doc = PrivateDocument.objects.get(id=int(json_data['doc_id']))
            #             self.object.identification2 = doc
            #             identification2_filechanged = True                        
                        
            #     except Exception as e:
            #         print (e)

            
            su = managed_models.SystemUser.objects.get(ledger_id=self.request.user.id)
            self.object.change_by_user_id = su.id            
            self.object.save()
            # if identification2_filechanged is True:
            #     EmailUserChangeLog.objects.create(emailuser=self.object, change_key="identification2", change_value=str(self.object.identification2.id) + ":" +self.object.identification2.name,change_by=self.request.user)

            # for fd in forms_data:
            
            #     if fd == 'identification2':
            #         pass        
            #     else:
                    
            #         if uservalue_map[fd] != forms_data[fd]:
            #             EmailUserChangeLog.objects.create(emailuser=self.object, change_key=fd, change_value=forms_data[fd],change_by=self.request.user)
            # 

            messages.success(self.request, "Succesfully updated account for {} {} ({})".format(self.object.legal_first_name,self.object.legal_last_name, self.object.email))
            # return HttpResponseRedirect(self.get_absolute_url())
            return HttpResponseRedirect(self.get_absolute_account_url())
        else:            
            return HttpResponseRedirect(self.get_absolute_account_url())


#class ProcessPaymentCheckout(TemplateView):
#    template_name = 'payments/payment-details.html'
#
#    def get(self, request, *args, **kwargs):
#        # if page is called with ratis_id, inject the ground_id
#        # /ledger/checkout/checkout/payment-details/
#
#        context = {}
#        cookies = {}
#        api_key = settings.LEDGER_API_KEY
#        url = settings.LEDGER_API_URL+'/ledger/checkout/checkout/payment-details/'
#        payment_session = None
#        basket_hash = ""
#
#        if 'payment_session' in request.session:
#              payment_session = request.session.get('payment_session')
#              basket_hash = request.session.get('basket_hash')
#              print ("BASKET HASH")
#              print (basket_hash)
#              cookies = {'sessionid': payment_session, 'ledgergw_basket': basket_hash, 'no_header': 'true', 'payment_api_wrapper': 'true', 'LEDGER_API_KEY': api_key}
#
#        print ("PAYMENT SESSION")
#        print (payment_session)
#        myobj = {}
#
#        # send request to server to get file
#        # allow_redirects=False
#        resp = requests.get(url, data = myobj, cookies=cookies)
#        context['data'] = resp.text
#        print (resp.headers)
#
#        #print (resp.text)
#
#
#        return render(request, self.template_name, context)
#

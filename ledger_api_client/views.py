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
from ledger_api_client import utils as ledger_api_client_utils
from ledger_api_client.mixins import InvoiceOwnerMixin
from django import forms
import django
from datetime import datetime, timedelta
#from django.template import Template, Context,RequestContext
#from django.template import loader
from django.template.loader import render_to_string
from decimal import *
import requests

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
              print ("B HHH")
              print (basket_hash)
              print (payment_session)
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

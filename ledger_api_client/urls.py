import django

if django.VERSION[0] >= 4:
    from django.urls import re_path as url
else:
    from django.conf.urls import url

from ledger_api_client import views
from ledger_api_client import api
from django.contrib.auth.views import LogoutView, LoginView
from django.conf import settings

urlpatterns = [
        url(r'^ledger-api/payment-details$', views.PaymentDetailCheckout.as_view(), name='ledgergw-payment-details'),
        url(r'^ledger-api/pay-invoice/(?P<reference>\d+)/$', views.PayInvoice.as_view(), name='ledgergw-payment-invoice'),
        #url(r'^ledger-api/process-payment$', views.ProcessPaymentCheckout.as_view(), name='ledgergw-process-payment'),
        # api
        url(r'^ledger-api/get-card-tokens', api.get_card_tokens),
        url(r'^ledger-api/delete-card-token/(?P<card_token_id>[0-9]+)/', api.delete_card_token),
        url(r'^ledger-api/process-payment', api.process_payment),
        url(r'^ledger-api/process-refund', api.process_refund),
        url(r'^ledger-api/process-zero', api.process_zero),
        url(r'^ledger-api/process-no', api.process_no),
        url(r'^ledger-ui/accounts-firsttime',  views.AccountsFirstTimeView.as_view(), name='account-firstime'),
        url(r'^ledger-ui/accounts',  views.AccountsView.as_view(), name='account'),
        url(r'^ledger-ui/api/get-settings/', api.get_settings, name='get-settings'),
        url(r'^ledger-ui/api/get-countries/', api.get_countries, name='get-settings'),

        url(r'^ledger-ui/api/get-account-details/(?P<user_id>[0-9]+)/', api.get_account_details, name='get-account-details'),
        url(r'^ledger-ui/api/update-account-details/(?P<user_id>[0-9]+)/', api.update_account_details, name='update-account-details'),
        url(r'^ledger-toolkit-api/invoice-pdf/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='ledger-api-invoice-pdf'),
        url(r'^ledger-toolkit-api/get-card-tokens', api.get_card_tokens),
        url(r'^ledger-toolkit-api/delete-card-token/(?P<card_token_id>[0-9]+)/', api.delete_card_token),
        url(r'^ledger-toolkit-api/store-card/', api.store_card),
        url(r'^ledger-toolkit-api/set-primary-card/', api.set_primary_card),
        
]
if settings.ENABLE_DJANGO_LOGIN is True:
    urlpatterns.append(url(r'^login/', LoginView.as_view(),name='login'))
    # this is entirely for the purpose to help with development and should not be enabled in production
    urlpatterns.append(url(r'^ssologin/', LoginView.as_view(),name='ssologin'))

urlpatterns.append(url(r'^logout/$', LogoutView.as_view(), {'next_page': '/'}, name='logout'))

if settings.EMAIL_INSTANCE == 'DEV' or settings.EMAIL_INSTANCE == 'UAT'  or settings.EMAIL_INSTANCE == 'TEST':
    # purpose of this is to not let search bot crawl dev/test/uat sites and prevent them from being index.
    urlpatterns.append(url(r'^robots.txt',  views.RobotView.as_view(), name='robot_txt'))   


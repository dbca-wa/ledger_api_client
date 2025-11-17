# from django.conf.urls import url, include
from django.urls import include, re_path
from django.contrib import admin
from django.views.generic import TemplateView
from ledger_api_client import views
from ledger_api_client import api
from django.contrib.auth import logout, login
from django.contrib.auth.views import LogoutView, LoginView
from django.conf import settings
from django.urls import path

urlpatterns = [
        re_path(r'^ledger-api/payment-details$', views.PaymentDetailCheckout.as_view(), name='ledgergw-payment-details'),
        re_path(r'^ledger-api/pay-invoice/(?P<reference>\d+)/$', views.PayInvoice.as_view(), name='ledgergw-payment-invoice'),
        
        #url(r'^ledger-api/process-payment$', views.ProcessPaymentCheckout.as_view(), name='ledgergw-process-payment'),
        # api
        re_path(r'^ledger-api/get-card-tokens', api.get_card_tokens),
        re_path(r'^ledger-api/delete-card-token/(?P<card_token_id>[0-9]+)/', api.delete_card_token),
        re_path(r'^ledger-api/process-payment', api.process_payment),
        re_path(r'^ledger-api/process-refund', api.process_refund),
        re_path(r'^ledger-api/process-zero', api.process_zero),
        re_path(r'^ledger-api/process-no', api.process_no),

        # System Admin Account Management
        re_path(r'^ledger-admin-api/accounts-management/list',  api.SystemUserAccountsList.as_view(), name='accounts-management-list'),
        re_path(r'^ledger-admin-api/system-account/logs/(?P<pk>\d+)$', api.SystemUserAccountsLogsList.as_view(),name='ledger-system-user-account-logs'),

        re_path(r'^ledger-ui/accounts-management/(?P<pk>\d+)/change',  views.SystemAccountChange.as_view(), name='accounts-management-change'),
        re_path(r'^ledger-ui/accounts-management/add',  views.SystemAccountAdd.as_view(), name='accounts-management-add'),     
        re_path(r'^ledger-ui/accounts-management',  views.AccountsManagementView.as_view(), name='accounts-management'),        

        # Ledger Account Management Intefac
        re_path(r'^ledger-ui/accounts-firsttime',  views.AccountsFirstTimeView.as_view(), name='account-firstime'),
        re_path(r'^ledger-ui/accounts',  views.AccountsView.as_view(), name='account'),
        re_path(r'^ledger-ui/organisation/(?P<pk>[0-9]+)/',  views.OrganisationView.as_view(), name='view-organisation'),

        # System Account Management - Store Personal Information in local system database but maintain link to ledger account id
        re_path(r'^ledger-ui/system-accounts-firsttime',  views.SystemAccountsFirstTimeView.as_view(), name='system-account-firstime'),
        re_path(r'^ledger-ui/system-accounts',  views.SystemAccountsView.as_view(), name='system-account'),
        

        # Crispy Forms
        re_path(r'^ledger-ui/crispy-form/account-information/(?P<pk>[0-9]+)/',  views.AccountInformationView.as_view(), name='system-account-information'), 
        re_path(r'^ledger-ui/crispy-form/personal-information/(?P<pk>[0-9]+)/',  views.PersonalInformationUpdate.as_view(), name='system-personal-information'),        
        re_path(r'^ledger-ui/crispy-form/contact-information/(?P<pk>[0-9]+)/',  views.ContactInformationUpdate.as_view(), name='system-account-contact-information'),  
        re_path(r'^ledger-ui/crispy-form/address-information/(?P<pk>[0-9]+)/create',  views.AddressInformationCreate.as_view(), name='system-create-address-information'),  
        re_path(r'^ledger-ui/crispy-form/address-information/(?P<system_user_id>[0-9]+)/edit/(?P<pk>[0-9]+)',  views.AddressInformationEdit.as_view(), name='system-edit-address-information'),  
        re_path(r'^ledger-ui/crispy-form/address-information/(?P<system_user_id>[0-9]+)/delete/(?P<pk>[0-9]+)',  views.AddressInformationDelete.as_view(), name='system-delete-address-information'),  
        re_path(r'^ledger-ui/crispy-form/address-information/(?P<pk>[0-9]+)/',  views.AddressInformationView.as_view(), name='system-address-information'),  
        

        re_path(r'^ledger-ui/api/get-settings/', api.get_settings, name='get-settings'),
        re_path(r'^ledger-ui/api/get-organisation-settings/', api.get_organisation_settings, name='get-organisation-settings'),

        re_path(r'^ledger-ui/api/get-countries/', api.get_countries, name='get-settings'),

        re_path(r'^ledger-ui/api/get-account-details/(?P<user_id>[0-9]+)/', api.get_account_details, name='get-account-details'),
        re_path(r'^ledger-ui/api/update-account-details/(?P<user_id>[0-9]+)/', api.update_account_details, name='update-account-details'),
        re_path(r'^ledger-toolkit-api/invoice-pdf/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='ledger-api-invoice-pdf'),
        re_path(r'^ledger-toolkit-api/get-card-tokens', api.get_card_tokens),
        re_path(r'^ledger-toolkit-api/delete-card-token/(?P<card_token_id>[0-9]+)/', api.delete_card_token),
        re_path(r'^ledger-toolkit-api/store-card/', api.store_card),
        re_path(r'^ledger-toolkit-api/set-primary-card/', api.set_primary_card),
        re_path(r'^ledger-ui/api/get-organisation-details/(?P<org_id>[0-9]+)/', api.get_organisation_details, name='get-organisation-details'),
        re_path(r'^ledger-ui/api/update-organisation-details/(?P<org_id>[0-9]+)/', api.update_organisation_details, name='update-organisation-details'),
        
]
if settings.ENABLE_DJANGO_LOGIN is True:
    urlpatterns.append(re_path(r'^login/', LoginView.as_view(),name='login'))
    # this is entirely for the purpose to help with development and should not be enabled in production
    urlpatterns.append(re_path(r'^ssologin/', LoginView.as_view(),name='ssologin'))

urlpatterns.append(re_path(r'^logout/$', LogoutView.as_view(), {'next_page': '/'}, name='logout'))

if settings.EMAIL_INSTANCE == 'DEV' or settings.EMAIL_INSTANCE == 'UAT'  or settings.EMAIL_INSTANCE == 'TEST':
    # purpose of this is to not let search bot crawl dev/test/uat sites and prevent them from being index.
    urlpatterns.append(re_path(r'^robots.txt',  views.RobotView.as_view(), name='robot_txt'))   


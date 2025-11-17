from __future__ import unicode_literals
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Fieldset, MultiField, Div, Button
from crispy_forms.bootstrap import FormActions, InlineRadios
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import Form, ModelForm, ChoiceField, FileField, CharField, Textarea, ClearableFileInput, HiddenInput, Field, RadioSelect, ModelChoiceField, Select
from django_countries.fields import CountryField
from django_countries.data import COUNTRIES
from django import forms
from ledger_api_client import managed_models
from ledger_api_client import utils as ledger_api_client_utils

class BaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
    field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'

class FullBaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
    field_class = 'col-xs-12 col-sm-8 col-md-9 col-lg-10'

class ButtonBaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-xs-0 col-sm-0 col-md-0 col-lg-0'
    field_class = 'col-xs-12 col-sm-12 col-md-12 col-lg-12'


class PopupFormHelper(FormHelper):
    form_class = 'form-horizontal popup-form'
    label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-3'
    field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-6'


class PersonalInformationUpdateForm(ModelForm):
    
    class Meta:
        model = managed_models.SystemUser
        fields = ['legal_first_name','legal_last_name','legal_dob']

    def __init__(self, *args, **kwargs):
        super(PersonalInformationUpdateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-6'
        # self.helper.form_tag = False
        self.fields['legal_first_name'].required = True
        self.fields['legal_last_name'].required = True
        self.fields['legal_dob'].widget = forms.DateInput(format='%d/%m/%Y')
        self.fields['legal_dob'].input_formats=['%d/%m/%Y']
        self.fields['legal_dob'].required = True
        self.fields['legal_dob'].widget.attrs['class'] = 'bs-datepicker'        

        crispy_boxes = Layout()
        if self.initial['account_change_locked'] is True:
            self.fields['legal_first_name'].widget = HiddenInput()
            self.fields['legal_last_name'].widget = HiddenInput()
            self.fields['legal_dob'].widget = HiddenInput()

            crispy_boxes.append('legal_first_name')
            crispy_boxes.append('legal_last_name')
            crispy_boxes.append('legal_dob')        
           
            legal_dob_string = ''
            if self.initial['legal_dob']:
                legal_dob_string = self.initial['legal_dob'].strftime("%d/%m/%Y")
            crispy_boxes.append(HTML('<div id="div_id_legal_dob_display" class="mb-3 row"> <label for="id_legal_dob" class="col-form-label col-xs-12 col-sm-4 col-md-3 col-lg-2 requiredField">Legal Given name(s) </label> <div class="col-xs-12 col-sm-8 col-md-6 col-lg-6"> <span id="input-ledger-ui-given-name" class="form-control" style="background-color:#efefef; height: 37px;">'+self.initial['legal_first_name']+'<span></div> </div>'))
            crispy_boxes.append(HTML('<div id="div_id_legal_dob_display" class="mb-3 row"> <label for="id_legal_dob" class="col-form-label col-xs-12 col-sm-4 col-md-3 col-lg-2 requiredField">Legal Last name </label> <div class="col-xs-12 col-sm-8 col-md-6 col-lg-6"> <span id="input-ledger-ui-given-name" class="form-control" style="background-color:#efefef; height: 37px;">'+self.initial['legal_last_name']+'<span></div> </div>'))
            crispy_boxes.append(HTML('<div id="div_id_legal_dob_display" class="mb-3 row"> <label for="id_legal_dob" class="col-form-label col-xs-12 col-sm-4 col-md-3 col-lg-2 requiredField">Legal date of birth</label> <div class="col-xs-12 col-sm-8 col-md-6 col-lg-6"> <span id="input-ledger-ui-given-name" class="form-control" style="background-color:#efefef; height: 37px;">'+legal_dob_string+'<span></div> </div>'))
            # crispy_boxes.append(HTML("<label>Legal Given Name(s)</label><div class='p-1'>{}</div>".format(self.initial['legal_first_name'])))
            # crispy_boxes.append(HTML("<label>Legal Last Name</label><div class='p-1'>{}</div>".format(self.initial['legal_last_name'])))            
            # crispy_boxes.append(HTML("<label>Legal DOB</label><div class='p-1'>{}</div>".format(self.initial['legal_dob'])))            
            
        else:        
            crispy_boxes.append('legal_first_name')
            crispy_boxes.append('legal_last_name')       
            crispy_boxes.append('legal_dob')
     
            self.helper.add_input(Submit('Update', 'Update', css_class='btn-lg', css_id="id_personal_information_btn"))
        self.helper.layout = Layout(crispy_boxes)

    def clean_legal_last_name(self):
        cleaned_data = self.clean()
        legal_last_name = cleaned_data.get('legal_last_name')
        if legal_last_name is None:
            raise forms.ValidationError('Please provide a valid last name.')
        elif len(legal_last_name) < 2:
            raise forms.ValidationError('Please provide a valid last name.')
        legal_last_name = ledger_api_client_utils.remove_html_tags(legal_last_name)
        return legal_last_name

    def clean_legal_first_name(self):
        cleaned_data = self.clean()
        legal_first_name = cleaned_data.get('legal_first_name')
        if legal_first_name is None:
            raise forms.ValidationError('Please provide a valid first name.')
        elif len(legal_first_name) < 2:
            raise forms.ValidationError('Please provide a valid first name.')
        legal_first_name = ledger_api_client_utils.remove_html_tags(legal_first_name)
        return legal_first_name

class ContactInformationUpdateForm(ModelForm):

    class Meta:
        model = managed_models.SystemUser
        fields = ['phone_number','mobile_number',]

    def __init__(self, *args, **kwargs):
        super(ContactInformationUpdateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-6'  
        self.fields['mobile_number'].required = True      
        self.helper.add_input(Submit('Update', 'Update', css_class='btn-lg', css_id="id_contact_information_btn"))

    def clean_mobile_number(self):
        cleaned_data = self.clean()
        mobile_number = cleaned_data.get('mobile_number')
        if mobile_number:
            if len(mobile_number) < 10:
                raise forms.ValidationError('Please provide a valid mobile phone number')        
        else:
            raise forms.ValidationError('Please provide a valid mobile phone number')
        mobile_number = ledger_api_client_utils.remove_html_tags(mobile_number)
        return mobile_number
    
    def clean_phone_number(self):
        cleaned_data = self.clean()
        phone_number = cleaned_data.get('phone_number')
        if phone_number:
            if len(phone_number) < 10:
                raise forms.ValidationError('Please provide a valid landline number (minimum 10 digits including area code), or mobile number')        
        phone_number = ledger_api_client_utils.remove_html_tags(phone_number)
        return phone_number    
    

class AddressInformationUpdateForm(ModelForm):

    class Meta:
        model = managed_models.SystemUserAddress
        fields = [ 'address_type','country','line1','line2','line3','locality','postcode','state','use_for_postal','use_for_billing']

    def __init__(self, *args, **kwargs):
        super(AddressInformationUpdateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-6'  
        self.fields['address_type'].required = True      
        self.fields['country'].required = True  
        self.fields['line1'].required = True  
        self.fields['locality'].required = True  
        self.fields['postcode'].required = True  
        self.fields['state'].required = True  

        address_choices = []
        for at in self.fields['address_type'].choices:    
            if at[0] == 'residential_address':
                if settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['residential_address']['show'] is True:
                    address_choices.append(at)
            if at[0] == 'postal_address':
                if settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['postal_address']['show'] is True:
                    address_choices.append(at)                

            if at[0] == 'billing_address':
                if settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['billing_address']['show'] is True:
                    address_choices.append(at)            
        self.fields['address_type'].choices = address_choices

        self.helper.add_input(Submit('Save', 'Save', css_class='btn-lg', css_id="id_contact_information_btn"))

    def clean_line1(self):    
        cleaned_data = self.clean()
        line1 = cleaned_data.get('line1')        
        line1 = ledger_api_client_utils.remove_html_tags(line1)
        return line1

    def clean_line2(self):    
        cleaned_data = self.clean()
        line2 = cleaned_data.get('line2')        
        line2 = ledger_api_client_utils.remove_html_tags(line2)
        return line2
    
    def clean_line3(self):    
        cleaned_data = self.clean()
        line3 = cleaned_data.get('line3')        
        line3 = ledger_api_client_utils.remove_html_tags(line3)
        return line3

    def clean_locality(self):    
        cleaned_data = self.clean()
        locality = cleaned_data.get('locality')        
        locality = ledger_api_client_utils.remove_html_tags(locality)
        return locality

    def clean_postcode(self):
        
        cleaned_data = self.clean()
        postcode = cleaned_data.get('postcode')
        country = cleaned_data.get('country')
        if country == 'AU':            
            if postcode:
                if len(postcode) != 4:
                    raise forms.ValidationError('Invalid postcode for australia')        
        postcode = ledger_api_client_utils.remove_html_tags(postcode)
        return postcode
                
    def clean_state(self):
        cleaned_data = self.clean()
        state = cleaned_data.get('state')
        country = cleaned_data.get('country')
        if country == 'AU':
            state = state.upper()
            if state:
                if  state == "ACT" or state == "NSW" or state == "NT" or state == "QLD" or state == "SA" or state == "TAS" or state == "VIC" or state == "WA":                    
                    pass
                else:
                    raise forms.ValidationError('Invalid state for australia,  inputs accepted (ACT,NSW,NT,QLD,SA,TAS,VIC,WA) ')                   
        state = ledger_api_client_utils.remove_html_tags(state)
        return state 
    

    def clean_address_type(self):
        cleaned_data = self.clean()
        address_type = cleaned_data.get('address_type')
        use_for_postal = cleaned_data.get('use_for_postal')

        system_user_id = self.initial['system_user_id']
        address_id = None
        if 'address_id' in self.initial:
            address_id = self.initial['address_id']
        use_for_postal = self.data['use_for_postal']
        use_for_billing = self.data['use_for_billing']
        system_user_obj = managed_models.SystemUser.objects.get(id=system_user_id)
        if address_id:
            residential_address_count = managed_models.SystemUserAddress.objects.filter(system_user=system_user_obj,address_type='residential_address').exclude(system_address_link=address_id).exclude(id=address_id).count()
            postal_address_count = managed_models.SystemUserAddress.objects.filter(system_user=system_user_obj,address_type='postal_address').exclude(system_address_link=address_id).count()
            billing_address_count = managed_models.SystemUserAddress.objects.filter(system_user=system_user_obj,address_type='billing_address').exclude(system_address_link=address_id).count()   
        else:
            
            residential_address_count = managed_models.SystemUserAddress.objects.filter(system_user=system_user_obj,address_type='residential_address').count()
            postal_address_count = managed_models.SystemUserAddress.objects.filter(system_user=system_user_obj,address_type='postal_address').count()
            billing_address_count = managed_models.SystemUserAddress.objects.filter(system_user=system_user_obj,address_type='billing_address').count()        

        if residential_address_count >= settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['residential_address']['total_allowed'] and address_type == 'residential_address':
            raise forms.ValidationError('You have reached your address limit of {} for residential address. '.format(str(settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['residential_address']['total_allowed'])))  
        if use_for_postal == 'true' or use_for_postal is True or address_type == 'postal_address':
            if postal_address_count >= settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['postal_address']['total_allowed']:
                raise forms.ValidationError('You have reached your address limit of {} for postal address.'.format(str(settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['postal_address']['total_allowed'])))  
        if use_for_billing == 'true' or use_for_billing is True or address_type == 'billing_address':            
            if billing_address_count >= settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['billing_address']['total_allowed']:
                raise forms.ValidationError('You have reached your address limit of {} for billing address.'.format(str(settings.LEDGER_UI_SYSTEM_ACCOUNTS_MANAGEMENT['address_details']['options']['billing_address']['total_allowed'])))  

        address_type = ledger_api_client_utils.remove_html_tags(address_type)
        return address_type     


       


class AddressInformationDeleteForm(ModelForm):

    class Meta:
        model = managed_models.SystemUserAddress
        fields = []

    def __init__(self, *args, **kwargs):
        super(AddressInformationDeleteForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-6'  
        
        self.helper.add_input(Submit('Delete', 'Delete', css_class='btn-lg btn-danger', css_id="id_delete_information_btn"))
        self.helper.add_input(Button('Cancel', 'cancel', css_class='btn-lg btn-primary cancel-address', css_id="id_cancel_information_btn"))

class SystemUserCreateForm(forms.ModelForm):

    class Meta:
        model = managed_models.SystemUser
        # fields = ['email', 'first_name', 'last_name','legal_first_name','legal_last_name', 'title','position_title','manager_name','manager_email', 'dob', 'legal_dob', 'phone_number', 'mobile_number', 'fax_number','identification2','is_staff','is_active']
        fields = ['email',]

    def __init__(self, *args, **kwargs):
        super(SystemUserCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.add_input(Submit('Create', 'Create', css_class='btn-lg btn-primary', css_id="id_create_user_btn"))
        self.helper.field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-6'  
            
            

class SystemUserForm(forms.ModelForm):
    
    # identification2 = FileField(label='Upload Identification', required=False, max_length=128, widget=AjaxFileUploader(attrs={'single':'single'})) 

    class Meta:
        model = managed_models.SystemUser
        # fields = ['email', 'first_name', 'last_name','legal_first_name','legal_last_name', 'title','position_title','manager_name','manager_email', 'dob', 'legal_dob', 'phone_number', 'mobile_number', 'fax_number','identification2','is_staff','is_active']
        fields = ['email', 'first_name', 'last_name','legal_first_name','legal_last_name', 'title', 'legal_dob', 'phone_number', 'mobile_number', 'fax_number','account_change_locked','prevent_auto_lock','is_staff','is_active']

    def __init__(self, *args, **kwargs):
        
        email_required = kwargs.pop('email_required', True)

        super(SystemUserForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        crispy_boxes = Div()


        for f in self.fields:            
            self.fields[f].widget.attrs['class'] = 'form-control'
            self.fields[f].widget.attrs['label_class'] = 'form-control'
            if f == 'first_name':                
                self.fields[f].widget = HiddenInput()
            if f == 'last_name':
                self.fields[f].widget = HiddenInput()
            if f == 'email':                
                self.fields[f].widget = HiddenInput()
            if f == 'position_title':
                self.fields[f].widget = HiddenInput()
            if f == 'manager_name':
                self.fields[f].widget = HiddenInput()    
            if f == 'manager_email':
                self.fields[f].widget = HiddenInput()
            if f == 'is_active':
                self.fields[f].widget.attrs['class'] = 'form-check-input'
                self.fields[f].help_text = ''
            if f == 'is_staff':
                self.fields[f].widget.attrs['class'] = 'form-check-input'
                self.fields[f].help_text = ''
            if f == 'account_change_locked':
                self.fields[f].widget.attrs['class'] = 'form-check-input'
                self.fields[f].help_text = ''                
            if f == 'prevent_auto_lock':
                self.fields[f].widget.attrs['class'] = 'form-check-input'
                self.fields[f].help_text = ''                





        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['legal_dob'].widget = forms.DateInput(format='%d/%m/%Y')
        self.fields['legal_dob'].input_formats=['%d/%m/%Y']        
        self.fields['legal_dob'].widget.attrs['class'] = 'bs-datepicker'                 
        self.fields['legal_dob'].widget.attrs['autocomplete'] = 'off'

        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class='btn-lg btn-danger'))

        person_id = self.initial['id']
        self.fields['email'].required = email_required

        # some form renderers use widget's is_required field to set required attribute for input element
        self.fields['email'].widget.is_required = email_required

        crispy_boxes.append(HTML("<label>Email</label><div class='p-1'>{}</div>".format(self.initial['email'])))
        crispy_boxes.append(HTML("<label>Given Name(s)</label><div class='p-1'>{}</div>".format(self.initial['first_name'])))
        crispy_boxes.append(HTML("<label>Last Name</label><div class='p-1'>{}</div>".format(self.initial['last_name'])))
        # crispy_boxes.append(HTML("<input type='hidden' value='{}' name='file_group' id='file_group'>".format('1')))
        # crispy_boxes.append(HTML("<input type='hidden' value='{}' name='file_group_ref_id' id='file_group_ref_id'>".format(str(person_id))))

        crispy_boxes.append('first_name')
        crispy_boxes.append('last_name')

        crispy_boxes.append('email')
        crispy_boxes.append('legal_first_name')
        crispy_boxes.append('legal_last_name')
        crispy_boxes.append('title')
        # crispy_boxes.append('dob')
        crispy_boxes.append('legal_dob')
        crispy_boxes.append('phone_number')
        crispy_boxes.append('mobile_number')
        crispy_boxes.append('fax_number')
        # crispy_boxes.append('identification2')
        crispy_boxes.append(HTML("<BR>"))
        crispy_boxes.append('account_change_locked')
        crispy_boxes.append('prevent_auto_lock')
        
        crispy_boxes.append('is_staff')
        crispy_boxes.append('is_active')
        
        crispy_boxes.append(HTML("<BR>"))

        self.helper.layout = Layout(crispy_boxes)


    def clean_email(self):    
        cleaned_data = self.clean()
        email = cleaned_data.get('email')        
        email = ledger_api_client_utils.remove_html_tags(email)
        return email
    
    def clean_first_name(self):    
        cleaned_data = self.clean()
        first_name = cleaned_data.get('first_name')        
        if first_name is not None:    
            first_name = ledger_api_client_utils.remove_html_tags(first_name)
            return first_name    


    def clean_last_name(self):    
        cleaned_data = self.clean()
        last_name = cleaned_data.get('last_name')        
        if last_name is not None:    
            last_name = ledger_api_client_utils.remove_html_tags(last_name)
            return last_name   

    def clean_legal_first_name(self):    
        cleaned_data = self.clean()
        legal_first_name = cleaned_data.get('legal_first_name')        
        legal_first_name = ledger_api_client_utils.remove_html_tags(legal_first_name)
        return legal_first_name   
    
    def clean_legal_last_name(self):    
        cleaned_data = self.clean()
        legal_last_name = cleaned_data.get('legal_last_name')        
        legal_last_name = ledger_api_client_utils.remove_html_tags(legal_last_name)
        return legal_last_name   

    def clean_title(self):    
        cleaned_data = self.clean()
        title = cleaned_data.get('title')        
        title = ledger_api_client_utils.remove_html_tags(title)
        return title  

    # def clean_legal_dob(self):    
    #     cleaned_data = self.clean()
    #     legal_dob = cleaned_data.get('legal_dob')        
    #     legal_dob = ledger_api_client_utils.remove_html_tags(legal_dob)
    #     return legal_dob    

    def clean_phone_number(self):    
        cleaned_data = self.clean()
        phone_number = cleaned_data.get('phone_number')        
        phone_number = ledger_api_client_utils.remove_html_tags(phone_number)
        return phone_number  

    def clean_mobile_number(self):    
        cleaned_data = self.clean()
        mobile_number = cleaned_data.get('mobile_number')        
        mobile_number = ledger_api_client_utils.remove_html_tags(mobile_number)
        return mobile_number    

    def clean_fax_number(self):    
        cleaned_data = self.clean()
        fax_number = cleaned_data.get('fax_number')        
        fax_number = ledger_api_client_utils.remove_html_tags(fax_number)
        return fax_number    


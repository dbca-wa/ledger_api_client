from __future__ import unicode_literals

import os
import zlib

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField
from django.db import models, IntegrityError, transaction
#from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.dispatch import receiver
from django.db.models import Q
from django.db.models.signals import post_delete, pre_save, post_save
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django_countries.fields import CountryField
#from ledger_api_client import ledger_models
from datetime import datetime, date
from django.contrib.auth.models import Permission
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from django.core.cache import cache
import json

class SystemGroup(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description= models.TextField(blank=True, null=True, default='')
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='ledger_api_permissions',
        blank=True,
    )

    class Meta:
        verbose_name = 'System Group'
        verbose_name_plural = 'System Groups'

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def save(self, *args, **kwargs):
        cache.delete("managed_models.SystemGroup.objects.filter(id="+str(self.id)+")") 
        cache.delete("managed_models.SystemGroup.get_system_group_member_ids:"+str(self.id))
        cache.delete("managed_models.SystemGroup.objects.filter(name="+str(self.name)+")")
        cache.delete("managed_models.SystemGroup.get_system_group_member_ids_active_users:"+str(self.id))
        super(SystemGroup, self).save(*args, **kwargs)

    def get_system_group_member_ids(self):
        spg_array = []
        spg_array_cache = cache.get("managed_models.SystemGroup.get_system_group_member_ids:"+str(self.id))
        
        if spg_array_cache is None:
            spg = SystemGroupPermission.objects.filter(system_group=self)
            for p in spg:
                spg_array.append(p.emailuser.id)
            cache.set("managed_models.SystemGroup.get_system_group_member_ids:"+str(self.id), json.dumps(spg_array), 86400)
        else:
            spg_array = json.loads(spg_array_cache)
        return spg_array
    
    def get_system_group_member_ids_active_users(self):
        spg_array = []
        spg_array_cache = cache.get("managed_models.SystemGroup.get_system_group_member_ids_active_users:"+str(self.id))
        # ,emailuser__active=True
        if spg_array_cache is None:
            spg = SystemGroupPermission.objects.filter(system_group=self)
            for p in spg:
                if p.emailuser.is_active is True:
                    spg_array.append(p.emailuser.id)
                cache.set("managed_models.SystemGroup.get_system_group_member_ids_active_users:"+str(self.id), json.dumps(spg_array), 86400)
        else:
            spg_array = json.loads(spg_array_cache)
        return spg_array    


#customer = models.ForeignKey(EmailUser, on_delete=models.PROTECT, blank=True, null=True)

class SystemGroupPermission(models.Model):
      system_group = models.ForeignKey(SystemGroup, on_delete=models.PROTECT)
      emailuser = models.ForeignKey(EmailUser, on_delete=models.PROTECT, blank=True, null=True, db_constraint=False)
      active = models.BooleanField(default=True)

      def __str__(self):
            return str(self.system_group)




class SystemUser(models.Model):
    """Custom authentication model for the ledger project.
    Password and email are required. Other fields are optional.
    """
    change_by_user_id = None

    ledger_id = models.OneToOneField(EmailUser, on_delete=models.DO_NOTHING, db_constraint=False, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, default=None)
    first_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='Last name')

    legal_first_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Legal Given name(s)')
    legal_last_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Legal Last name')

    account_change_locked = models.BooleanField(
        default=False,
        help_text='Will lock the account details preventing changes to the account information.',
    )
    prevent_auto_lock = models.BooleanField(
        default=False,
        help_text='Will prevent to auto locking script from locking the account.',
    )
    
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active.'
                  'Unselect this instead of deleting ledger.accounts.',
    )
    created = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    
    title = models.CharField(max_length=100, choices=TITLE_CHOICES, null=True, blank=True, verbose_name='title', help_text='')
    # dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, verbose_name="date of birth", help_text='')
    legal_dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, verbose_name="Legal date of birth", help_text='')
    phone_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="phone number", help_text='')  
    mobile_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="mobile number", help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="fax number", help_text='')   

    def __str__(self):
        if self.legal_first_name:                        
            return '{} {}'.format(self.legal_first_name, self.legal_last_name)
        else:
            if self.first_name:
                return '{} {}'.format(self.first_name, self.last_name)
            return '{}'.format(self.ledger_id_id)      

    def save(self, *args, **kwargs):
 

        if self.id is None:

            super(SystemUser, self).save(*args, **kwargs)
            system_user_old = SystemUser.objects.get(email=self.email)
            if not self.change_by_user_id:
                self.change_by_user_id = system_user_old.id

            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='email',
                                            change_value=str(self.email),
                                            change_by_id=self.change_by_user_id
                                            )

            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='first_name',
                                            change_value=str(self.first_name),
                                            change_by_id=self.change_by_user_id
                                            )            

            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='last_name',
                                            change_value=str(self.last_name),
                                            change_by_id=self.change_by_user_id
                                            )            


            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='legal_first_name',
                                            change_value=str(self.legal_first_name),
                                            change_by_id=self.change_by_user_id
                                            )            


            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='legal_last_name',
                                            change_value=str(self.legal_last_name),
                                            change_by_id=self.change_by_user_id
                                            )            


            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='account_change_locked',
                                            change_value=str(self.account_change_locked),
                                            change_by_id=self.change_by_user_id
                                            )            

            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='prevent_auto_lock',
                                            change_value=str(self.prevent_auto_lock),
                                            change_by_id=self.change_by_user_id
                                            )     

            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='is_staff',
                                            change_value=str(self.is_staff),
                                            change_by_id=self.change_by_user_id
                                            )            



            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='is_active',
                                            change_value=str(self.is_active),
                                            change_by_id=self.change_by_user_id
                                            )            



            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='title',
                                            change_value=str(self.title),
                                            change_by_id=self.change_by_user_id
                                            )            



            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='legal_dob',
                                            change_value=str(self.legal_dob),
                                            change_by_id=self.change_by_user_id
                                            )            



            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='phone_number',
                                            change_value=str(self.phone_number),
                                            change_by_id=self.change_by_user_id
                                            )            



            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='mobile_number',
                                            change_value=str(self.mobile_number),
                                            change_by_id=self.change_by_user_id
                                            )            



            SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='fax_number',
                                            change_value=str(self.fax_number),
                                            change_by_id=self.change_by_user_id
                                            )         

        else:
 
            if self.change_by_user_id is None:
                """
                su = SystemUser()
                su.change_by_user_id = 9   # this should be set to the user id of the person making the change and is needed for change log records
                su.objects.get(id=8)
                su.first_name = "Bob"
                su.save()
                """
                raise ValidationError("Change User ID not provided, Please provide before changing any user data")    

            system_user_old = SystemUser.objects.get(id=self.id)
            super(SystemUser, self).save(*args, **kwargs)
            if system_user_old.email != self.email:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='email',
                                            change_value=str(self.email),
                                            change_by_id=self.change_by_user_id
                                            )
            if system_user_old.first_name != self.first_name:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='first_name',
                                            change_value=str(self.first_name),
                                            change_by_id=self.change_by_user_id
                                            )            
            if system_user_old.last_name != self.last_name:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='last_name',
                                            change_value=str(self.last_name),
                                            change_by_id=self.change_by_user_id
                                            )            

            if system_user_old.legal_first_name != self.legal_first_name:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='legal_first_name',
                                            change_value=str(self.legal_first_name),
                                            change_by_id=self.change_by_user_id
                                            )            

            if system_user_old.legal_last_name != self.legal_last_name:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='legal_last_name',
                                            change_value=str(self.legal_last_name),
                                            change_by_id=self.change_by_user_id
                                            )            

            if system_user_old.account_change_locked != self.account_change_locked:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='account_change_locked',
                                            change_value=str(self.account_change_locked),
                                            change_by_id=self.change_by_user_id
                                            )            

            if system_user_old.prevent_auto_lock != self.prevent_auto_lock:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='prevent_auto_lock',
                                            change_value=str(self.prevent_auto_lock),
                                            change_by_id=self.change_by_user_id
                                            )                                                   

            if system_user_old.is_staff != self.is_staff:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='is_staff',
                                            change_value=str(self.is_staff),
                                            change_by_id=self.change_by_user_id
                                            )            


            if system_user_old.is_active != self.is_active:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='is_active',
                                            change_value=str(self.is_active),
                                            change_by_id=self.change_by_user_id
                                            )            


            if system_user_old.title != self.title:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='title',
                                            change_value=str(self.title),
                                            change_by_id=self.change_by_user_id
                                            )            


            if system_user_old.legal_dob != self.legal_dob:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='legal_dob',
                                            change_value=str(self.legal_dob),
                                            change_by_id=self.change_by_user_id
                                            )            


            if system_user_old.phone_number != self.phone_number:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='phone_number',
                                            change_value=str(self.phone_number),
                                            change_by_id=self.change_by_user_id
                                            )            


            if system_user_old.mobile_number != self.mobile_number:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='mobile_number',
                                            change_value=str(self.mobile_number),
                                            change_by_id=self.change_by_user_id
                                            )            


            if system_user_old.fax_number != self.fax_number:
                SystemUserChangeLog.objects.create(systemuser=self,
                                            change_key='fax_number',
                                            change_value=str(self.fax_number),
                                            change_by_id=self.change_by_user_id
                                            )            

class SystemUserAddress(models.Model):

    STATE_CHOICES = (
        ('ACT', 'ACT'),
        ('NSW', 'NSW'),
        ('NT', 'NT'),
        ('QLD', 'QLD'),
        ('SA', 'SA'),
        ('TAS', 'TAS'),
        ('VIC', 'VIC'),
        ('WA', 'WA')
    )    
    ADDRESS_TYPE = (
            ('residential_address', 'Residential Address'),
            ('postal_address', 'Postal Address'),
            ('billing_address', 'Billing Address'),
    )

    change_by_user_id = None

    system_user = models.ForeignKey(SystemUser, on_delete=models.CASCADE)
    address_type = models.CharField(choices=ADDRESS_TYPE, max_length=50, blank=True, null=True )
    line1 = models.CharField('Line 1', max_length=255, blank=True, null=True)
    line2 = models.CharField('Line 2', max_length=255, blank=True, null=True)
    line3 = models.CharField('Line 3', max_length=255, blank=True, null=True)
    locality = models.CharField('Suburb / Town', max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=255, default='WA', blank=True, null=True)
    country = CountryField(default='AU', blank=True, null=True)
    use_for_postal = models.BooleanField(default=False)   
    use_for_billing = models.BooleanField(default=False)
    system_address_link = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return '{} {} {} {} {}'.format(self.line1, self.locality, self.state, self.country,self.postcode)

    def save(self, *args, **kwargs):
        
        if self.change_by_user_id is None:
            """
            su = SystemAddress()
            su.change_by_user_id = 9   # this should be set to the user id of the person making the change and is needed for change log records
            su.objects.get(id=8)
            su.line1 = "3 John St"
            su.save()
            """
            raise ValidationError("Change User ID not provided, Please provide before changing any user data")
        
        if self.pk is None:
            super(SystemUserAddress, self).save(*args, **kwargs)    
            
            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:address_type',
                            change_value=str(self.address_type),
                            change_by_id=self.change_by_user_id
                            )     

            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':line1',
                            change_value=str(self.line1),
                            change_by_id=self.change_by_user_id
                            )     
            
            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':line2',
                            change_value=str(self.line2),
                            change_by_id=self.change_by_user_id
                            )     
            
            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':line3',
                            change_value=str(self.line3),
                            change_by_id=self.change_by_user_id
                            )      

            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':locality',
                            change_value=str(self.locality),
                            change_by_id=self.change_by_user_id
                            )               

            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':postcode',
                            change_value=str(self.postcode),
                            change_by_id=self.change_by_user_id
                            )     
            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':state',
                            change_value=str(self.state),
                            change_by_id=self.change_by_user_id
                            )     
            
            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':country',
                            change_value=str(self.country),
                            change_by_id=self.change_by_user_id
                            )     

            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':use_for_postal',
                            change_value=str(self.use_for_postal),
                            change_by_id=self.change_by_user_id
                            ) 
                                        
            SystemUserChangeLog.objects.create(systemuser=self.system_user,
                            change_key='create:'+str(self.address_type)+':use_for_billing',
                            change_value=str(self.use_for_billing),
                            change_by_id=self.change_by_user_id
                            )     

        else:
            system_user_address_old = SystemUserAddress.objects.get(id=self.id)
            super(SystemUserAddress, self).save(*args, **kwargs) 

            if system_user_address_old.address_type != self.address_type:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':address_type',
                                            change_value=str(self.address_type),
                                            change_by_id=self.change_by_user_id
                                            )    
            if system_user_address_old.line1 != self.line1:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':line1',
                                            change_value=str(self.line1),
                                            change_by_id=self.change_by_user_id
                                            )   

            if system_user_address_old.line2 != self.line2:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':line2',
                                            change_value=str(self.line2),
                                            change_by_id=self.change_by_user_id
                                            )   


            if system_user_address_old.line3 != self.line3:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':line3',
                                            change_value=str(self.line3),
                                            change_by_id=self.change_by_user_id
                                            )   


            if system_user_address_old.locality != self.locality:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':locality',
                                            change_value=str(self.locality),
                                            change_by_id=self.change_by_user_id
                                            )  
                

            if system_user_address_old.postcode != self.postcode:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':postcode',
                                            change_value=str(self.postcode),
                                            change_by_id=self.change_by_user_id
                                            )  


            if system_user_address_old.state != self.state:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':state',
                                            change_value=str(self.state),
                                            change_by_id=self.change_by_user_id
                                            )  


            if system_user_address_old.country != self.country:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':country',
                                            change_value=str(self.country),
                                            change_by_id=self.change_by_user_id
                                            )                                                  

            if system_user_address_old.use_for_postal != self.use_for_postal:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':use_for_postal',
                                            change_value=str(self.use_for_postal),
                                            change_by_id=self.change_by_user_id
                                            )           
                
            if system_user_address_old.use_for_billing != self.use_for_billing:
                SystemUserChangeLog.objects.create(systemuser=self.system_user,
                                            change_key=str(self.id)+':'+str(self.address_type)+':use_for_billing',
                                            change_value=str(self.use_for_billing),
                                            change_by_id=self.change_by_user_id
                                            )                           

@receiver(post_delete, sender=SystemUserAddress)
def delete_preo(sender, instance, **kwargs):
  
    if instance.change_by_user_id is None:
        """
            # many items to delete
            sua = SystemUserAddress.objects.filter(address_type='postal_address')
            for sua_item in sua:
                sua_item.change_by_user_id=request.user.id
                sua_item.delete()
            
            # one item to delete
            sua_item = SystemUserAddress.objects.get(id=199)
            sua_item.change_by_user_id=request.user.id
            sua_item.delete()

        """
        raise ValidationError("Change User ID not provided, Please provide before changing any user data")
    # system_user_address_old = SystemUserAddress.objects.get(id=self.id)

    SystemUserChangeLog.objects.create(systemuser=instance.system_user,
                                change_key=str(instance.id)+':'+instance.address_type,
                                change_value="Deleted",
                                change_by_id=instance.change_by_user_id
                                )  



class SystemUserChangeLog(models.Model):
    systemuser = models.ForeignKey(SystemUser, related_name='change_log_system_user', on_delete=models.DO_NOTHING)
    change_key = models.CharField(max_length=1024, blank=True, null=True)
    change_value = models.CharField(max_length=1024, blank=True, null=True)
    change_by = models.ForeignKey(SystemUser, related_name='change_log_request_user', blank=True, null=True, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:        
        ordering = ['-created']
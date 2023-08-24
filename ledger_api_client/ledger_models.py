from __future__ import unicode_literals
import traceback
from django.db import models, transaction
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db.models import JSONField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser #PermissionsMixin
from django.utils import timezone
from django.db import models
from ledger_api_client.abstract_address_models import AbstractUserAddress
from ledger_api_client.address_models import UserAddress
from ledger_api_client.country_models import Country
#from ledger_api_client.perms_models import PermissionsMixinRO
from django_countries.fields import CountryField
from django.core.files.storage import FileSystemStorage
#from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from django.core.exceptions import PermissionDenied
from django.contrib import auth
from django.contrib.auth.models import Group, Permission
from ledger_api_client import utils
#from django.utils.encoding import python_2_unicode_compatible

import zlib
import decimal
import requests
import json
from django.db.models import Q
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class LedgerDBRouter(object):

    def db_for_read(self, model, **hints):
       if model._meta.db_table == 'accounts_emailuser' or model._meta.db_table == 'address_country' or  model._meta.db_table == 'payments_invoice' or model._meta.db_table == 'accounts_emailuser_documents' or model._meta.db_table ==  'accounts_document'  or model._meta.db_table ==  'accounts_emailidentity' or model._meta.db_table == 'basket_basket' or model._meta.db_table == 'accounts_emailuser_user_permissions':
           return 'ledger_db'
       if model._meta.db_table == 'auth_group': #or model._meta.db_table == 'auth_permission':
           return 'ledger_db'

       if model._meta.db_table == 'django_migrations':
            return 'default'
           

       #or model._meta.db_table == 'django_admin_log'
       return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.db_table == 'accounts_emailuser': # or model._meta.db_table == 'auth_group' or model._meta.db_table == 'auth_permission':
           return 'ledger_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the events app is involved.
        """
        if 'accounts_emailuser' == obj1._meta.db_table and  'parkstay_campgroundgroup_members' == obj2._meta.db_table:
             return True
        if 'accounts_emailuser' == obj1._meta.db_table:
            return True
        if 'auth_group' == obj1._meta.db_table:
            return True
        if 'auth_permission' == obj1._meta.db_table:
            return True
        if 'django_content_type' == obj1._meta.db_table:
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'other_db'  
        database.
        """
        #if app_label == '':
        #    return db == 'other_db'  
        return 'default'

class Document(models.Model):
    name = models.CharField(max_length=100, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    file = models.FileField(upload_to='%Y/%m/%d')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    @property
    def path(self):
        return self.file.path

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename

    class Meta:
        managed = False
        db_table = 'accounts_document'

# Private Documents
class PrivateDocument(models.Model):

    FILE_GROUP = (
        (1,'Identification'),
        (2,'Senior Card'),
    )

    #upload = models.FileField(max_length=512, upload_to='uploads/%Y/%m/%d', storage=upload_storage)
    name = models.CharField(max_length=256)
    metadata = JSONField(null=True, blank=True)
    text_content = models.TextField(null=True, blank=True, editable=False)  # Text for indexing
    file_group = models.IntegerField(choices=FILE_GROUP, null=True, blank=True)
    file_group_ref_id = models.IntegerField(null=True, blank=True)
    extension = models.CharField(max_length=5, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        if self.file_group:
            return '{} ({})'.format(self.name, self.get_file_group_display())
        return self.name

    class Meta:
        managed = False
        db_table = 'accounts_privatedocument'

class BaseAddress(models.Model):
    """Generic address model, intended to provide billing and shipping
    addresses.
    Taken from django-oscar address AbstrastAddress class.
    """
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

    # Addresses consist of 1+ lines, only the first of which is
    # required.
    line1 = models.CharField('Line 1', max_length=255)
    line2 = models.CharField('Line 2', max_length=255, blank=True)
    line3 = models.CharField('Line 3', max_length=255, blank=True)
    locality = models.CharField('Suburb / Town', max_length=255)
    state = models.CharField(max_length=255, default='WA', blank=True)
    country = CountryField(default='AU')
    postcode = models.CharField(max_length=10)
    # A field only used for searching addresses.
    search_text = models.TextField(editable=False)
    hash = models.CharField(max_length=255, db_index=True, editable=False)

    def __str__(self):
        return self.summary

#    def __unicode__(self):
#        return ''

    class Meta:
        abstract = True

    def clean(self):
        # Strip all whitespace
        for field in ['line1', 'line2', 'line3', 'locality', 'state']:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].strip()

    def save(self, *args, **kwargs):
        print ("NO SAVING ADDRESS")
        #self._update_search_text()
        #self.hash = self.generate_hash()
        #super(BaseAddress, self).save(*args, **kwargs)

    #def _update_search_text(self):
    #    search_fields = filter(
    #        bool, [self.line1, self.line2, self.line3, self.locality,
    #               self.state, str(self.country.name), self.postcode])
    #    self.search_text = ' '.join(search_fields)

    #@property
    #def summary(self):
    #    """Returns a single string summary of the address, separating fields
    #    using commas.
    #    """
    #    return u', '.join(self.active_address_fields())


    ## Helper methods
    #def active_address_fields(self):
    #    """Return the non-empty components of the address.
    #    """
    #    fields = [self.line1, self.line2, self.line3,
    #              self.locality, self.state, self.country, self.postcode]
    #    #for f in fields:
    #    #    print unicode(f).encode('utf-8').decode('unicode-escape').strip()
    #    #fields = [str(f).strip() for f in fields if f]
    #    print ("ENCODIUNG")
    #    for f in fields:
    #        print (f)
    #        if f:
    #            print (str(f))
    #    print ("END ")
    #    #print ([f.encode('utf-8').decode('unicode-escape').strip() for f in fields if f])
    #    fields = [str(f) for f in fields if f]
    #    #fields = [f.encode('utf-8').decode('unicode-escape').strip() for f in fields if f]
    #    #fields = [unicode_compatible(f).encode('utf-8').decode('unicode-escape').strip() for f in fields if f]

    #    return fields

    #def join_fields(self, fields, separator=u', '):
    #    """Join a sequence of fields using the specified separator.
    #    """
    #    field_values = []
    #    for field in fields:
    #        value = getattr(self, field)
    #        field_values.append(value)
    #    return separator.join(filter(bool, field_values))

    #def generate_hash(self):
    #    """
    #        Returns a hash of the address summary
    #    """
    #    return zlib.crc32(self.summary.strip().upper().encode('UTF8'))


#class AddressManager(): 
#
#     def create(self):
#         print ("Address Creation")
#
#     def save(self):
#         print ("SAVE ADDRESS")
#

class Address(BaseAddress):
    user = models.ForeignKey('EmailUserRO', related_name='profile_addresses', on_delete=models.DO_NOTHING)
    oscar_address = models.ForeignKey(UserAddress, related_name='profile_addresses', on_delete=models.DO_NOTHING)

    #objects = AddressManager()

    class Meta:
        managed = False
        db_table = 'accounts_address'
        verbose_name_plural = 'addresses'
        unique_together = ('user','hash')


class EmailIdentity(models.Model):
    """Table used for matching access email address with EmailUser.
    """
    user = models.ForeignKey('EmailUserRO', null=True, on_delete=models.DO_NOTHING)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

    class Meta:
        managed = False
        db_table = 'accounts_emailidentity'

def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():

        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False

def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False

####
class PermissionsMixinRO(models.Model):
    """
    A mixin class that adds the fields and methods necessary to support
    Django's Group and Permission model using the ModelBackend.
    """
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set_ro",
        related_query_name="user",
        db_table="accounts_emailuser_groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set_ro",
        related_query_name="user",
        db_table='accounts_emailuser_user_permissions'
    )

    class Meta:
        abstract = True
        managed = False
         
    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through their
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def get_system_group_permission(self,user_id):
        from ledger_api_client import managed_models
        cache_name_sgp = 'managed_models.SystemGroupPermission.objects.filter(emailuser_id='+str(user_id)+')'
        sgp_groups = []
        sgp_cache = cache.get(cache_name_sgp)
        if sgp_cache is None:
            sgp = managed_models.SystemGroupPermission.objects.filter(emailuser_id=self.id)
            for s in sgp:
                sgp_groups.append(s.system_group.id)
            cache.set(cache_name_sgp, json.dumps(sgp_groups), 10)
        else:
            sgp_groups = json.loads(sgp_cache)
        return sgp_groups
    def system_group_permision_list(self,system_group_id):
        from ledger_api_client import managed_models
        permission_list = []
        cache_name_pl = "managed_models.SystemGroup.objects.filter(id="+str(system_group_id)+")"
        pl_cache = cache.get(cache_name_pl)
        if pl_cache is None:
            system_groups = managed_models.SystemGroup.objects.filter(id=system_group_id)
            for sg in system_groups:
                for p in sg.permissions.all():
                    perm_name = p.content_type.app_label+"."+p.codename
                    app_label = p.content_type.app_label
                    permission_list.append({"id":p.id, "perm_name" : perm_name, 'app_label': app_label})
                    cache.set(cache_name_pl,json.dumps(permission_list), 86400)
        else:
            permission_list = json.loads(pl_cache)

        return permission_list

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        
        
        from ledger_api_client import managed_models       
        sgp_groups = self.get_system_group_permission(self.id)

        for sgp in sgp_groups:
              perm_list = self.system_group_permision_list(sgp)
              for p in perm_list:
                  if perm == p['perm_name']:
                       return True
        return False 
        # Otherwise we need to check the backends.
        #return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        #print ("YES BACKEND has_module_perms")
        #print (app_label)

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        sgp_groups = self.get_system_group_permission(self.id)

        for sgp in sgp_groups:
              perm_list = self.system_group_permision_list(sgp)
              for p in perm_list:
                  if app_label == p['app_label']:
                       return True

        return False 
        #return Permission.objects.filter(group__user=self.id)
        #return _user_has_module_perms(self, app_label)
            

####

















class EmailUserROManager(BaseUserManager):
    """A custom Manager for the EmailUser model.
    """
    use_in_migrations = False 

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves an EmailUser with the given email and password.
        """
        print ("Can not create users here")
        #if not email:
        #    raise ValueError('Email must be set')
        #email = self.normalize_email(email).lower()
        #if EmailUser.objects.filter(email__iexact=email):
        #    raise ValueError('This email is already in use')
        #user = self.model(
        #    email=email, is_staff=is_staff, is_superuser=is_superuser)
        #user.extra_data = extra_fields
        #user.set_password(password)
        #user.save(using=self._db)
        #return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class objects:
    def filter(**kwargs):
        return ("YES")

class GroupObj:
  def  __init__(self,group_id, group_name):
       self.id = group_id
       self.name = group_name
  
class GroupQuerySet(object):
    query_set = []
    def  __init__(self):
        pass

    def add(self):
        self.query_set.append({'test': 'test'})

    def exists(self):
        return True

    def __call__(self):
        return self.query_set
    def __repr__(self):
        return self.query_set

    def __str(self):
        return "OBJECT"


class GroupsManger:

    def __init__(self,emailuser, **kwargs):
        self.emailuser_id = emailuser.id
        self.filtered = self.filtered(self,**kwargs)
        self.filter = self.filtered.filter
        self.exists = self.filtered.exists
        self.all = self.filtered.all
        
    #def __call__(self, **kwargs):
    #    return self

    def all(self):
        return

    class filtered:
         action = None
         exists_checked = False
         groups_obj = []

         def __iter__(self, **kwargs):
              return iter(self.groups_obj)

         def __call__(self, **kwargs):
             return self

         def __init__(self,innerself,**kwargs):
             self.emailuser_id = innerself.emailuser_id

         def exists(self, **kwargs):
             return self.exists_checked

         def all(self, **kwargs):
             try:
                 url = settings.LEDGER_API_URL+"/ledgergw/remote/user-groups/"+str(self.emailuser_id)+"/"+settings.LEDGER_API_KEY+"/"

                 filter_obj = {}
                 myobj = {'filter': json.dumps(filter_obj)}
                 resp = requests.post(url, data = myobj, cookies={})
                 self.groups_obj = []
                 for g in resp.json()['groups']['groups']:
                     g_obj = GroupObj(g['group_id'],g['group_name'])
                     self.groups_obj.append(g_obj)
                 self.exists_checked = resp.json()['query_exists']
             except Exception as e:
                 raise ValidationError('Error: Unable to create user - Issue connecting to ledger gateway')
             return self

         def filter(self, **kwargs):
             try:
                 url = settings.LEDGER_API_URL+"/ledgergw/remote/user-groups/"+str(self.emailuser_id)+"/"+settings.LEDGER_API_KEY+"/"

                 filter_obj = {} 
                 for m in kwargs:
                     filter_obj[m] = kwargs[m]

                 myobj = {'filter': json.dumps(filter_obj)}
                 resp = requests.post(url, data = myobj, cookies={})
                 self.groups_obj = []
                 for g in resp.json()['groups']['groups']:
                     g_obj = GroupObj(g['group_id'],g['group_name'])
                     self.groups_obj.append(g_obj)
                 self.exists_checked = resp.json()['query_exists']
             except Exception as e:
                 print (e)
                 raise ValidationError('Error: Unable to create user - Issue connecting to ledger gateway')
             return self 

class EmailUserRO(AbstractBaseUser, PermissionsMixinRO):
#class EmailUserRO(AbstractBaseUser):

    """Custom authentication model for the ledger project.
    Password and email are required. Other fields are optional.
    """
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active.'
                  'Unselect this instead of deleting ledger.accounts.',
    )
    date_joined = models.DateTimeField(default=timezone.now)

    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    title = models.CharField(max_length=100, choices=TITLE_CHOICES, null=True, blank=True,
                             verbose_name='title', help_text='')
    dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False,
                           verbose_name="date of birth", help_text='')
    phone_number = models.CharField(max_length=50, null=True, blank=True,
                                    verbose_name="phone number", help_text='')
    position_title = models.CharField(max_length=100, null=True, blank=True,
                                    verbose_name="position title", help_text='')
    mobile_number = models.CharField(max_length=50, null=True, blank=True,
                                     verbose_name="mobile number", help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True,
                                  verbose_name="fax number", help_text='')
    organisation = models.CharField(max_length=300, null=True, blank=True,
                                    verbose_name="organisation", help_text='organisation, institution or company')

    residential_address = models.ForeignKey(Address, null=True, blank=False, related_name='+', on_delete=models.DO_NOTHING)
    postal_address = models.ForeignKey(Address, null=True, blank=True, related_name='+', on_delete=models.DO_NOTHING)
    postal_same_as_residential = models.BooleanField(default=False) 
    billing_address = models.ForeignKey(Address, null=True, blank=True, related_name='+', on_delete=models.DO_NOTHING)
    billing_same_as_residential = models.BooleanField(default=False)

    identification = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='identification_document')
    identification2 = models.ForeignKey(PrivateDocument, null=True, blank=True, on_delete=models.SET_NULL, related_name='identification_document_2')

    senior_card = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='senior_card')
    senior_card2 = models.ForeignKey(PrivateDocument, null=True, blank=True, on_delete=models.SET_NULL, related_name='senior_card')

    character_flagged = models.BooleanField(default=False)

    character_comments = models.TextField(blank=True)

    documents = models.ManyToManyField(Document)

    extra_data = JSONField(default=dict)

    objects = EmailUserROManager()
    #groups = GroupsManger() 
    USERNAME_FIELD = 'email'

    class Meta:
        managed = False
        db_table = 'accounts_emailuser'
        #app_label = 'EmailUser'


    def __str__(self):
        if self.is_dummy_user:
            if self.organisation:
                return '{} {} ({})'.format(self.first_name, self.last_name, self.organisation)
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            if self.organisation:
                return '{} ({})'.format(self.email, self.organisation)
            return '{}'.format(self.email)

    def clean(self):
        super(EmailUserRO, self).clean()
        self.email = self.email.lower() if self.email else self.email
        post_clean.send(sender=self.__class__, instance=self)

    def save(self, *args, **kwargs):
        print ("Preparing Api call to ledger") 
        try:
            url = settings.LEDGER_API_URL+"/ledgergw/remote/user/"+self.email+"/"+settings.LEDGER_API_KEY+"/"
            saveobj = {
                    'username': '',
                    'last_name': self.last_name,
                    'first_name': self.first_name,
                    'email': self.email,
            }
            resp = requests.post(url, data = saveobj, cookies={})
            print (resp)
        except Exception as e:
            raise ValidationError('Error: Unable to create user - Issue connecting to ledger gateway')
 

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        #.encode('utf-8').strip()
        return full_name

    def get_full_name_dob(self):
        full_name_dob = '{} {} ({})'.format(self.first_name, self.last_name, self.dob.strftime('%d/%m/%Y'))
        return full_name_dob.strip()

    def get_short_name(self):
        if self.first_name:
            return self.first_name.split(' ')[0]
        return self.email

    dummy_email_suffix = ".s058@ledger.dpaw.wa.gov.au"
    dummy_email_suffix_len = len(dummy_email_suffix)

    @property
    def is_dummy_user(self):
        return not self.email or self.email[-1 * self.dummy_email_suffix_len:] == self.dummy_email_suffix

    @property
    def dummy_email(self):
        if self.is_dummy_user:
            return self.email
        else:
            return None

    def get_dummy_email(self):
        # use timestamp plus first name, last name to generate a unique id.
        uid = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return "{}.{}.{}{}".format(self.first_name, self.last_name, uid, self.dummy_email_suffix)

    @property
    def username(self):
        return self.email

    @property
    def is_senior(self):
        """
        Test if the the user is a senior according to the rules of WA senior
        dob is before 1 July 1955; or
        dob is between 1 July 1955 and 30 June 1956 and age is 61 or older; or
        dob is between 1 July 1956 and 30 June 1957 and age is 62 or older; or
        dob is between 1 July 1957 and 30 June 1958 and age is 63 or older; or
        dob is between 1 July 1958 and 30 June 1959 and age is 64 or older; or
        dob is after 30 June 1959 and age is 65 or older
        :return:
        """
        return \
            self.dob < date(1955, 7, 1) or \
            ((date(1955, 7, 1) <= self.dob <= date(1956, 6, 30)) and self.age() >= 61) or \
            ((date(1956, 7, 1) <= self.dob <= date(1957, 6, 30)) and self.age() >= 62) or \
            ((date(1957, 7, 1) <= self.dob <= date(1958, 6, 30)) and self.age() >= 63) or \
            ((date(1958, 7, 1) <= self.dob <= date(1959, 6, 30)) and self.age() >= 64) or \
            (self.dob > date(1959, 6, 1) and self.age() >= 65)

    def age(self):
        if self.dob:
            today = date.today()
            # calculate age with the help of trick int(True) = 1 and int(False) = 0
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        else:
            return -1

    def groups(self):
        return GroupsManger(self)  
EmailUserRO.documents.through._meta.get_field('emailuserro_id').column='emailuser_id'

#EmailUserRO.groups.through._meta.get_field('emailuserro').column='emailuser_id'



class Invoice(models.Model):

    PAYMENT_METHOD_CC = 0
    PAYMENT_METHOD_BPAY = 1
    PAYMENT_METHOD_MONTHLY_INVOICING = 2
    PAYMENT_METHOD_OTHER = 3
    PAYMENT_METHOD_CHOICES = (
        (PAYMENT_METHOD_CC, 'Credit Card'),
        (PAYMENT_METHOD_BPAY, 'BPAY'),
        (PAYMENT_METHOD_MONTHLY_INVOICING, 'Monthly Invoicing'),
        (PAYMENT_METHOD_OTHER, 'Other'),
    )

    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True,blank=True)
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    order_number = models.CharField(max_length=50,unique=True)
    reference = models.CharField(max_length=50, unique=True)
    system = models.CharField(max_length=4,blank=True,null=True)
    token = models.CharField(max_length=80,null=True,blank=True)
    voided = models.BooleanField(default=False)
    previous_invoice = models.ForeignKey('self',null=True,blank=True, on_delete=models.DO_NOTHING)
    settlement_date = models.DateField(blank=True, null=True)
    payment_method = models.SmallIntegerField(choices=PAYMENT_METHOD_CHOICES, default=0)

    def __unicode__(self):
        return 'Invoice #{0}'.format(self.reference)

    class Meta:
        managed = False
        db_table = 'payments_invoice'

    @property
    def number(self):
        length = len(str(self.id))
        val = '0'
        return '{}{}'.format((val*(6-length)),self.id)

    @property
    def refundable_amount(self):
        return self.total_payment_amount - self.__calculate_total_refunds()

    @property
    def refundable(self):
        if self.refundable_amount > 0:
            return True
        return False

    @property
    def num_items(self):
        ''' Get the number of items in this invoice.
        '''
        return self.order.num_items

    @property
    def owner(self):
        user = None
        order = utils.Order.objects.get(number=self.order_number)
        if order:
            if order.user_id:
               user= EmailUserRO.objects.filter(id=order.user_id)
               if user.count() > 0:
                   return user[0]
        return None

    @property
    def balance(self):
        if self.voided:
            return decimal.Decimal(0)
        amount = decimal.Decimal(self.amount - self.payment_amount)
        if amount < 0:
            amount =  decimal.Decimal(0)
        return amount
 
    @property
    def payment_amount(self):
        invoice_remote = utils.get_invoice_properties(self.id)
        payment_amount = 0
        if 'status' in invoice_remote:
           if invoice_remote['status'] == 200:
               payment_amount = invoice_remote['data']['invoice']['payment_amount']
        return decimal.Decimal(payment_amount)

    # Functions
    # =============================================
    def save(self,*args,**kwargs):
        print ('Save forbidden')
        pass


class Basket(models.Model):
    """
    Basket object
    """

    system = models.CharField(max_length=4)
    custom_ledger = models.BooleanField(default=False)
    booking_reference = models.CharField(max_length=254, blank=True, null=True)

    # Baskets can be anonymously owned - hence this field is nullable.  When a
    # anon user signs in, their two baskets are merged.
    owner = models.ForeignKey('EmailUserRO', related_name='owner_basket_name', null=True, on_delete=models.CASCADE,)
    # Basket statuses
    # - Frozen is for when a basket is in the process of being submitted
    #   and we need to prevent any changes to it.
    OPEN, MERGED, SAVED, FROZEN, SUBMITTED = (
        "Open", "Merged", "Saved", "Frozen", "Submitted")
    STATUS_CHOICES = (
        (OPEN, _("Open - currently active")),
        (MERGED, _("Merged - superceded by another basket")),
        (SAVED, _("Saved - for items to be purchased later")),
        (FROZEN, _("Frozen - the basket cannot be modified")),
        (SUBMITTED, _("Submitted - has been ordered at the checkout")),
    )
    status = models.CharField(
        _("Status"), max_length=128, default=OPEN, choices=STATUS_CHOICES)

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_merged = models.DateTimeField(_("Date merged"), null=True, blank=True)
    date_submitted = models.DateTimeField(_("Date submitted"), null=True,
                                          blank=True)


    class Meta:
       managed = False
       db_table = 'basket_basket'



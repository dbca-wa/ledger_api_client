from django.core.exceptions import PermissionDenied

from ledger_api_client import helpers
from ledger_api_client import utils
from ledger_api_client import ledger_models
from ledger_api_client import managed_models

class InvoiceOwnerMixin(object):

    #def belongs_to(self, user, group_name):
    #    return helpers.belongs_to(user, group_name)

    def is_payment_admin(self,user):
        return helpers.is_payment_admin(user)

    def check_owner(self, user):
        user_id = user.id
        if user_id:
            order_number = self.get_object().order_number
            order = utils.Order.objects.get(number=order_number)
            user = ledger_models.EmailUserRO.objects.get(id=user_id)        
            return order.user_id == user_id or self.is_payment_admin(user)
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.check_owner(request.user):
            raise PermissionDenied
        return super(InvoiceOwnerMixin, self).dispatch(request, *args, **kwargs)
    

class SystemUserPermissionMixin(object):

    def system_user_access(self, user, system_user_id):
        has_access = False
        if user:
            if user.is_authenticated is True:
                su = managed_models.SystemUser.objects.filter(id=system_user_id)
                sg_account_management = managed_models.SystemGroupPermission.objects.filter(system_group__name='Account Management',emailuser=user.id, active=True).count()                            
                if su.count() > 0:
                    if user.is_superuser is True:
                        has_access = True
                    elif su[0].ledger_id_id == user.id:
                        has_access = True      
                    elif sg_account_management > 0:
                        has_access = True                            
        return has_access

    def dispatch(self, request, *args, **kwargs):
        if not self.system_user_access(request.user,kwargs.get('pk')):
            raise PermissionDenied
        return super(SystemUserPermissionMixin, self).dispatch(request, *args, **kwargs)    

class SystemUserAddressPermissionMixin(object):

    def system_user_access(self, user, address_id):
        has_access = False
        if user:
            if user.is_authenticated is True:
                sua = managed_models.SystemUserAddress.objects.filter(id=address_id)
                if sua.count() > 0:
                    su = managed_models.SystemUser.objects.filter(id=sua[0].system_user.id)
                    sg_account_management = managed_models.SystemGroupPermission.objects.filter(system_group__name='Account Management',emailuser=user.id, active=True).count()                            
                    if su.count() > 0:
                        if user.is_superuser is True:
                            has_access = True
                        elif su[0].ledger_id_id == user.id:
                            has_access = True  
                        elif sg_account_management > 0:
                            has_access = True                                      
        return has_access

    def dispatch(self, request, *args, **kwargs):
        
        if not self.system_user_access(request.user,kwargs.get('pk')):
            raise PermissionDenied
        return super(SystemUserAddressPermissionMixin, self).dispatch(request, *args, **kwargs)        

class AccountManagementPermissionMixin(object):

    def system_user_access(self, user):
        has_access = False
        if user:
            if user.is_authenticated is True:                
                sg_account_management = managed_models.SystemGroupPermission.objects.filter(system_group__name='Account Management',emailuser=user.id, active=True).count()                            
                if user.is_superuser is True:
                    has_access = True
                if sg_account_management > 0:
                    has_access = True       
        return has_access

    def dispatch(self, request, *args, **kwargs):
        
        if not self.system_user_access(request.user):
            raise PermissionDenied
        return super(AccountManagementPermissionMixin, self).dispatch(request, *args, **kwargs)    
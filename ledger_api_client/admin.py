from django.contrib import messages
from django.contrib.gis import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.admin import register, ModelAdmin
from ledger_api_client import models
from ledger_api_client import managed_models
from ledger_api_client import ledger_models

#@admin.register(managed_models.SystemGroupPermission)
class SystemGroupPermissionInline(admin.TabularInline):
    model = managed_models.SystemGroupPermission
    extra = 0
    raw_id_fields = ('emailuser',)

    # list_display = ('id','emailuser')

@admin.register(managed_models.SystemGroup)
class SystemGroupAdmin(ModelAdmin):
    list_display = ('id','name','description')
    search_fields = ('id','name','description',)
    inlines = [SystemGroupPermissionInline]

@admin.register(managed_models.SystemUser)
class SystemuserAdmin(ModelAdmin):
    list_display = ('id','legal_first_name','legal_last_name')    
    raw_id_fields = ('ledger_id',)
    search_fields = ('id','first_name','last_name','legal_first_name','legal_last_name','email',)

    def save_model(self, request, obj, form, change):

        # Need to create this way to ledger_id being in a different database.
        if obj.pk is None:
            eu= ledger_models.EmailUserRO.objects.get(id=obj.ledger_id.id)
            su = managed_models.SystemUser.objects.create(  ledger_id=eu,
                                                            first_name=obj.first_name,
                                                            last_name=obj.last_name,
                                                            legal_first_name=obj.legal_first_name,
                                                            legal_last_name=obj.legal_last_name,
                                                            is_staff=obj.is_staff,
                                                            is_active=obj.is_active,
                                                            title=obj.title,
                                                            dob=obj.dob,
                                                            legal_dob=obj.legal_dob,
                                                            phone_number=obj.phone_number,
                                                            mobile_number=obj.mobile_number,
                                                            fax_number=obj.fax_number,                                                          
                                                          )
        else:
            super().save_model(request, obj, form, change)

@admin.register(managed_models.SystemUserAddress)
class SystemUserAddressAdmin(ModelAdmin):
    list_display = ('id','system_user','address_type','line1','locality','postcode','state','country')    
    search_fields = ('id','system_user','line1','locality','postcode','state','country')
    raw_id_fields = ('system_user',)

    # def save_model(self, request, obj, form, change):

    #     # Need to create this way to ledger_id being in a different database.
    #     if obj.pk is None:
    #         eu= ledger_models.EmailUserRO.objects.get(id=obj.ledger_id.id)
    #         su = managed_models.SystemUser.objects.create(  ledger_id=eu,
    #                                                         first_name=obj.first_name,
    #                                                         last_name=obj.last_name,
    #                                                         legal_first_name=obj.legal_first_name,
    #                                                         legal_last_name=obj.legal_last_name,
    #                                                         is_staff=obj.is_staff,
    #                                                         is_active=obj.is_active,
    #                                                         title=obj.title,
    #                                                         dob=obj.dob,
    #                                                         legal_dob=obj.legal_dob,
    #                                                         phone_number=obj.phone_number,
    #                                                         mobile_number=obj.mobile_number,
    #                                                         fax_number=obj.fax_number,                                                          
    #                                                       )
    #     else:
    #         super().save_model(request, obj, form, change)




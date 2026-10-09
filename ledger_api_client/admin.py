from django.contrib import messages
from django.contrib.gis import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.admin import register, ModelAdmin
from django.contrib.admin.options import get_content_type_for_model
from ledger_api_client import models
from ledger_api_client import managed_models
from ledger_api_client import ledger_models

from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import unquote, quote
from django.contrib.contenttypes.models import ContentType
from django.template.response import TemplateResponse

from django.core.exceptions import PermissionDenied
from django.utils.text import capfirst
from django.utils.translation import gettext as _

from reversion.admin import VersionAdmin as ReversionVersionAdmin
from django.urls import reverse
from reversion.models import Version

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

    def history_view(self, request, object_id, extra_context=None):
            "The 'history' admin view for this model."
            from django.contrib.admin.models import LogEntry
            from django.contrib.admin.views.main import PAGE_VAR
    
            # First check if the user can see this history.
            model = self.model
            obj = self.get_object(request, unquote(object_id))
            if obj is None:
                return self._get_obj_does_not_exist_redirect(
                    request, model._meta, object_id
                )
    
            if not self.has_view_or_change_permission(request, obj):
                raise PermissionDenied
    
            # Then get the history for this object.
            app_label = self.opts.app_label
            action_list = (
                LogEntry.objects.filter(
                    object_id=unquote(object_id),
                    content_type=get_content_type_for_model(model),
                )
                .order_by("action_time")
            )
    
            paginator = self.get_paginator(request, action_list, 100)
            page_number = request.GET.get(PAGE_VAR, 1)
            page_obj = paginator.get_page(page_number)
            page_range = paginator.get_elided_page_range(page_obj.number)
    
            context = {
                **self.admin_site.each_context(request),
                "title": _("Change history: %s") % obj,
                "subtitle": None,
                "action_list": page_obj,
                "page_range": page_range,
                "page_var": PAGE_VAR,
                "pagination_required": paginator.count > 100,
                "module_name": str(capfirst(self.opts.verbose_name_plural)),
                "object": obj,
                "opts": self.opts,
                "preserved_filters": self.get_preserved_filters(request),
                **(extra_context or {}),
            }
    
            request.current_app = self.admin_site.name
    
            return TemplateResponse(
                request,
                self.object_history_template
                or [
                    "admin/%s/%s/object_history.html" % (app_label, self.opts.model_name),
                    "admin/%s/object_history.html" % app_label,
                    "admin/object_history.html",
                ],
                context,
            )

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

class VersionAdmin(ReversionVersionAdmin):

    def history_view(self, request, object_id, extra_context=None):

        if hasattr(self, 'has_view_or_change_permission'):
            if not self.has_view_or_change_permission(request):
                raise PermissionDenied
        else:
            if not self.has_change_permission(request):
                raise PermissionDenied

        opts = self.model._meta
        action_list = [
            {
                "revision": version.revision,
                "url": reverse(
                    f"{self.admin_site.name}:{opts.app_label}_{opts.model_name}_revision",
                    args=(quote(version.object_id), version.id)
                ),
            }
            for version
            in self._reversion_order_version_queryset(Version.objects.get_for_object_reference(
                self.model,
                unquote(object_id),
            ))
        ]
        # Compile the context.
        context = {"action_list": action_list}
        context.update(extra_context or {})
        return super(ReversionVersionAdmin, self).history_view(request, object_id, context)



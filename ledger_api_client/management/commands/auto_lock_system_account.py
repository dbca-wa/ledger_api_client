from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
from ledger_api_client import models
from ledger_api_client import managed_models
from datetime import datetime,timedelta

import urllib.request, json


class Command(BaseCommand):
    help = 'Automatically set system "account change lock" to true after a desire period after account is created.'

    def handle(self, *args, **options):
        
        nowtime = datetime.now().astimezone()        
        print ("Looking for unlocked accounts at "+str(nowtime))
        mm = managed_models.SystemUser.objects.get(email=settings.SYSTEM_ACCOUNT_AUTO)        

        su_obj = managed_models.SystemUser.objects.filter(account_change_locked=False, prevent_auto_lock=False)
        for su in su_obj:            
            timedelta_obj = nowtime - su.created.astimezone()
            diff_in_seconds = timedelta_obj.days * 24 * 3600 + timedelta_obj.seconds
            prevent_locking = False
            if su.legal_first_name is None or su.legal_first_name == '':
                prevent_locking= True
            
            if su.legal_last_name is None or su.legal_last_name == '':
                prevent_locking= True

            if prevent_locking is False:
                if diff_in_seconds > settings.SYSTEM_ACCOUNT_AUTO_LOCK_PERIOD:
                    print ("Locking Account: "+str(su.legal_first_name)+" "+str(su.legal_last_name)+" ("+str(su.id)+") as created seconds is "+str(diff_in_seconds)+" which longer than "+str(settings.SYSTEM_ACCOUNT_AUTO_LOCK_PERIOD))                
                    su.account_change_locked = True
                    su.change_by_user_id = mm.id
                    su.save()

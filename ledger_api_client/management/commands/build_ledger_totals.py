from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
from ledger_api_client import utils
from datetime import datetime
from django.conf import settings
import requests
import json
import os

from datetime import timedelta

class Command(BaseCommand):
    help = 'Collect totals data from ledger.'

    def handle(self, *args, **options):

        try:
            ledger_totals = {'refund_total': 0}
            system_id = settings.PAYMENT_SYSTEM_ID.replace('S','0');
            refund_total = utils.get_refund_totals(system_id)
            try:
                ledger_totals['refund_total'] = refund_total['data']['total_failed']
            except:
                print ("error updating failed refund totals")

            data_dir = settings.BASE_DIR+"/datasets/"
            data_file = data_dir+"ledger-totals.json"
            if os.path.isdir(data_dir):
                pass
            else:
                os.mkdir(data_dir)
                
            f = open(data_file, "w")
            f.write(json.dumps(ledger_totals, indent=4))
            f.close()

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)

"""Ledger API Client Django Application Cron Jobs."""

# Standard
import logging

# Third-Party
from django import conf
from django.core import management
import django_cron

# Logging
log = logging.getLogger(__name__)

class CronJobLedgerTotals(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    RUN_EVERY_MINS = 5
    
    schedule = django_cron.Schedule(run_at_times=RUN_EVERY_MINS)
    code = "ledger_api_client.ledger_totals"

    def do(self) -> None:
        """Update Ledger Totals"""

        # Run Management Command
        management.call_command("build_ledger_totals")
        return "Job Completed Successfully"
    

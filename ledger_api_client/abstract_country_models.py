import re
import zlib

from django.conf import settings
from django.core import exceptions
from django.db import models
#from django.utils.encoding import python_2_unicode_compatible
# from django.utils.six.moves import filter
# from django5_six.utils.six.moves import filter
# from django5_six.utils import six
#from django.utils.translation import ugettext_lazy as _
#from django.utils.translation import pgettext_lazy
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from ledger_api_client.decorators import deprecated
from ledger_api_client.oscar_fields import UppercaseCharField
#from ledger_api_client.country_models import Country

#@python_2_unicode_compatible
class AbstractCountry(models.Model):
    """
    International Organization for Standardization (ISO) 3166-1 Country list.

    The field names are a bit awkward, but kept for backwards compatibility.
    pycountry's syntax of alpha2, alpha3, name and official_name seems sane.
    """
    iso_3166_1_a2 = models.CharField(
        _('ISO 3166-1 alpha-2'), max_length=2, primary_key=True)
    iso_3166_1_a3 = models.CharField(
        _('ISO 3166-1 alpha-3'), max_length=3, blank=True)
    iso_3166_1_numeric = models.CharField(
        _('ISO 3166-1 numeric'), blank=True, max_length=3)

    #: The commonly used name; e.g. 'United Kingdom'
    printable_name = models.CharField(_('Country name'), max_length=128)
    #: The full official name of a country
    #: e.g. 'United Kingdom of Great Britain and Northern Ireland'
    name = models.CharField(_('Official name'), max_length=128)

    display_order = models.PositiveSmallIntegerField(
        _("Display order"), default=0, db_index=True,
        help_text=_('Higher the number, higher the country in the list.'))

    is_shipping_country = models.BooleanField(
        _("Is shipping country"), default=False, db_index=True)

    class Meta:
        abstract = True
        app_label = 'address'
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        ordering = ('-display_order', 'printable_name',)

    def __str__(self):
        return self.printable_name or self.name

    @property
    def code(self):
        """
        Shorthand for the ISO 3166 Alpha-2 code
        """
        return self.iso_3166_1_a2

    @property
    def numeric_code(self):
        """
        Shorthand for the ISO 3166 numeric code.

        iso_3166_1_numeric used to wrongly be a integer field, but has to be
        padded with leading zeroes. It's since been converted to a char field,
        but the database might still contain non-padded strings. That's why
        the padding is kept.
        """
        return u"%.03d" % int(self.iso_3166_1_numeric)


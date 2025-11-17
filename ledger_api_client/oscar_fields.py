from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import CharField, DecimalField
# from django.utils import six
from django5_six.utils import six
#from django.utils.translation import ugettext_lazy as _

class Creator(object):
    """
    A placeholder class that provides a way to set the attribute on the model.
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)


class UppercaseCharField(CharField):
    """
    A simple subclass of ``django.db.models.fields.CharField`` that
    restricts all text to be uppercase.

    Defined with the with_metaclass helper so that to_python is called
    https://docs.djangoproject.com/en/1.6/howto/custom-model-fields/#the-subfieldbase-metaclass  # NOQA
    """

    def contribute_to_class(self, cls, name, **kwargs):
        super(UppercaseCharField, self).contribute_to_class(
            cls, name, **kwargs)
        setattr(cls, self.name, Creator(self))

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        val = super(UppercaseCharField, self).to_python(value)
        if isinstance(val, six.string_types):
            return val.upper()
        else:
            return val

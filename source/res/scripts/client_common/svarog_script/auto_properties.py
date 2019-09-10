# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/svarog_script/auto_properties.py


class AutoProperty(object):

    def __init__(self, fieldName=None):
        self.fieldName = fieldName

    def __get__(self, instance, owner=None):
        return getattr(instance, self.fieldName, None) if instance is not None else getattr(owner, self.fieldName)

    def __set__(self, instance, value):
        setattr(instance, self.fieldName, value)


class TypedProperty(AutoProperty):

    def __init__(self, allowedType, fieldName=None):
        AutoProperty.__init__(self, fieldName)
        self.allowedType = allowedType

    def __set__(self, instance, value):
        setattr(instance, self.fieldName, value)


class LinkDescriptor(AutoProperty):

    def __init__(self, fieldName=None):
        AutoProperty.__init__(self, fieldName)

    def __set__(self, instance, value):
        setattr(instance, self.fieldName, value)

    def __call__(self, *args, **kwargs):
        return None


class AutoPropertyInitMetaclass(type):

    def __new__(mcs, name, bases, attributes):
        for attributeName, attribute in attributes.iteritems():
            if isinstance(attribute, AutoProperty) and attribute.fieldName is None:
                attribute.fieldName = '_%s__%s' % (name, attributeName)

        return super(AutoPropertyInitMetaclass, mcs).__new__(mcs, name, bases, attributes)

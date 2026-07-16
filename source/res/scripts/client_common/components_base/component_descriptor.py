# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/components_base/component_descriptor.py
from __future__ import absolute_import
from components_base.auto_properties import AutoProperty
from components_base.component_controller import ComponentController

class ComponentDescriptor(AutoProperty):

    def __init__(self, fieldName=None):
        AutoProperty.__init__(self, fieldName)

    def __set__(self, instance, value):
        prevValue = getattr(instance, self.fieldName, None)
        if prevValue is not None:
            if self.__isIterable(prevValue):
                for element in prevValue:
                    instance.removeComponent(element)

            else:
                instance.removeComponent(prevValue)
        if value is not None:
            if self.__isIterable(value):
                for element in value:
                    self.__setValue(instance, element)

            else:
                self.__setValue(instance, value)
        instance.touchDescriptor(self.fieldName)
        setattr(instance, self.fieldName, value)
        return

    def __setValue(self, instance, value):
        if getattr(value, 'isOwning', True):
            instance.addComponent(value, self.fieldName)
        else:
            instance.registerComponent(value)

    def __isIterable(self, value):
        return hasattr(value, '__iter__')


class ComponentDescriptorTyped(ComponentDescriptor):

    def __init__(self, allowedType, fieldName=None):
        ComponentDescriptor.__init__(self, fieldName)
        self.allowedType = allowedType

    def __set__(self, instance, value):
        ComponentDescriptor.__set__(self, instance, value)

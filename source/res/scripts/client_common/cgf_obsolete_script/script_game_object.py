# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/cgf_obsolete_script/script_game_object.py
import CGF
from cgf_obsolete_script.auto_properties import AutoProperty, AutoPropertyInitMetaclass

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


class ScriptGameObject(object):
    __metaclass__ = AutoPropertyInitMetaclass
    gameObject = property(lambda self: self._nativeSystem)

    def __init__(self, spaceID, name=''):
        self._components = []
        self.__touchedDescriptors = set()
        self._nativeSystem = CGF.GameObject(spaceID, name)

    def activate(self):
        self._nativeSystem.activate()

    def deactivate(self):
        self._nativeSystem.deactivate()

    def touchDescriptor(self, descriptorName):
        self.__touchedDescriptors.add(descriptorName)

    def addComponent(self, component, name=''):
        self._components.append(component)
        self._nativeSystem.addComponent(component, name)

    def removeComponent(self, component):
        if self._nativeSystem.isValid():
            self._nativeSystem.removeComponent(component)
        try:
            self._components.remove(component)
        except ValueError:
            pass

    def destroy(self):
        self.reset(False)

    def reset(self, recreate=True):
        for descriptorName in self.__touchedDescriptors:
            setattr(self, descriptorName, None)

        spaceID = self._nativeSystem.spaceID
        self._components = []
        self._nativeSystem.destroy()
        if recreate:
            self._nativeSystem = CGF.GameObject(spaceID)
        else:
            self._nativeSystem = None
        return

    def __getattr__(self, item):
        if item == '_nativeSystem':
            raise AttributeError('Missing nativeSystem.')
        return getattr(self._nativeSystem, item)

    def registerComponent(self, component):
        self._components.append(component)

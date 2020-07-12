# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/svarog_script/script_game_object.py
import Svarog
from svarog_script.auto_properties import AutoProperty, AutoPropertyInitMetaclass

class ComponentDescriptor(AutoProperty):

    def __init__(self, fieldName=None):
        AutoProperty.__init__(self, fieldName)

    def __set__(self, instance, value):
        prevValue = getattr(instance, self.fieldName, None)
        if prevValue is not None:
            instance.removeComponent(prevValue)
        if value is not None:
            if getattr(value, 'isOwning', True):
                instance.addComponent(value, self.fieldName)
            else:
                instance.registerComponent(value)
        setattr(instance, self.fieldName, value)
        return


class ComponentDescriptorTyped(ComponentDescriptor):

    def __init__(self, allowedType, fieldName=None):
        ComponentDescriptor.__init__(self, fieldName)
        self.allowedType = allowedType

    def __set__(self, instance, value):
        ComponentDescriptor.__set__(self, instance, value)


class ScriptGameObject(object):
    __metaclass__ = AutoPropertyInitMetaclass

    def __init__(self, spaceID):
        self._components = []
        self._nativeSystem = Svarog.GameObject(spaceID)

    def activate(self):
        self._nativeSystem.activate()

    def deactivate(self):
        self._nativeSystem.deactivate()

    def addComponent(self, component, name=''):
        self._components.append(component)
        self._nativeSystem.addComponent(component, name)

    def removeComponent(self, component):
        self._nativeSystem.removeComponent(component)
        if component in self._components:
            self._components.remove(component)

    def destroy(self):
        self._components = []
        self._nativeSystem.destroy()

    def __getattr__(self, item):
        return getattr(self._nativeSystem, item)

    def registerComponent(self, component):
        self._components.append(component)

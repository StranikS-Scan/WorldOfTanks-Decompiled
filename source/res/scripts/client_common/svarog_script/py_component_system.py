# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/svarog_script/py_component_system.py
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
            instance.addComponent(value, self.fieldName)
        setattr(instance, self.fieldName, value)
        return


class ComponentSystem(object):
    __metaclass__ = AutoPropertyInitMetaclass

    @staticmethod
    def groupCall(func):

        def wrapped(*args, **kwargs):
            self = args[0]
            processedArgs = args[1:]
            for component in self._components:
                attr = getattr(component, func.__name__, None)
                if attr is not None:
                    attr(*processedArgs, **kwargs)

            func(*args, **kwargs)
            return

        return wrapped

    def __init__(self):
        self._components = []
        self._nativeSystem = Svarog.ComponentSystem()

    def activate(self):
        self._nativeSystem.activate()

    def deactivate(self):
        self._nativeSystem.deactivate()

    def addComponent(self, component, name=''):
        self._nativeSystem.addComponent(component, name)
        self._components.append(component)

    def removeComponent(self, component):
        self._nativeSystem.removeComponent(component)
        self._components.remove(component)

    def destroy(self):
        self._components = []
        self._nativeSystem.destroy()

    def __getattr__(self, item):
        return getattr(self._nativeSystem, item)

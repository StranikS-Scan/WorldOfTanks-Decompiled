# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/components_base/component_controller.py
from __future__ import absolute_import
import typing
from future.utils import with_metaclass
from components_base.auto_properties import AutoPropertyInitMetaclass
if typing.TYPE_CHECKING:
    from components_base.component import Component

class ComponentController(with_metaclass(AutoPropertyInitMetaclass, object)):

    def __init__(self, name=''):
        self._components = []
        self.__touchedDescriptors = set()
        self.__name = name

    def activate(self):
        for component in self._components:
            component.activate()

    def deactivate(self):
        for component in self._components:
            component.deactivate()

    def touchDescriptor(self, descriptorName):
        self.__touchedDescriptors.add(descriptorName)

    def addComponent(self, component, name=''):
        self._components.append(component)

    def removeComponent(self, component):
        self._components.remove(component)

    def destroy(self):
        for component in self._components:
            component.destroy()

        self.reset()

    def reset(self):
        for descriptorName in self.__touchedDescriptors:
            setattr(self, descriptorName, None)

        self._components = []
        return

    def registerComponent(self, component):
        self._components.append(component)

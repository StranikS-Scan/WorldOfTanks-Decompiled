# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCGFObject.py
import CGF
from ClientSelectableObject import ClientSelectableObject
from Math import Vector3
from cgf_components.client_selectable_components import OnClickComponent, SwitchSelectableStateComponent

class ClientSelectableCGFObject(ClientSelectableObject):

    def __init__(self):
        super(ClientSelectableCGFObject, self).__init__()
        self.__gameObject = None
        self.__switchStateComponent = None
        return

    def onEnterWorld(self, prereqs):
        super(ClientSelectableCGFObject, self).onEnterWorld(prereqs)
        parent = self.entityGameObject
        if parent is not None and self.usedPrefab:
            CGF.loadGameObjectIntoHierarchy(self.usedPrefab, parent, Vector3(), self.__onGameObjectLoaded)
        return

    def onLeaveWorld(self):
        if self.__switchStateComponent is not None:
            self.__switchStateComponent.onStateChanged -= self.setEnable
        if self.__gameObject is not None:
            CGF.removeGameObject(self.__gameObject)
        self.__gameObject = None
        super(ClientSelectableCGFObject, self).onLeaveWorld()
        return

    def onMouseClick(self):
        if self.__gameObject:
            onMouseClickComponent = self.__gameObject.findComponentByType(OnClickComponent)
            if onMouseClickComponent:
                onMouseClickComponent.doAction()
        super(ClientSelectableCGFObject, self).onMouseClick()

    def __onGameObjectLoaded(self, gameObject):
        self.__gameObject = gameObject
        self.__switchStateComponent = self.__gameObject.findComponentByType(SwitchSelectableStateComponent)
        if self.__switchStateComponent is not None:
            self.setEnable(self.__switchStateComponent.selectableEnabled)
            self.__switchStateComponent.onStateChanged += self.setEnable
        return

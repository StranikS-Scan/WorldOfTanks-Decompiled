# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCGFObject.py
import CGF
from ClientSelectableObject import ClientSelectableObject
from Math import Vector3
from cgf_components.client_selectable_components import OnClickComponent

class ClientSelectableCGFObject(ClientSelectableObject):

    def __init__(self):
        super(ClientSelectableCGFObject, self).__init__()
        self.__gameObject = None
        return

    def onEnterWorld(self, prereqs):
        super(ClientSelectableCGFObject, self).onEnterWorld(prereqs)
        parent = self.entityGameObject
        if parent is not None and self.usedPrefab:
            CGF.loadGameObjectIntoHierarchy(self.usedPrefab, parent, Vector3(), self.__onGameObjectLoaded)
        return

    def onLeaveWorld(self):
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

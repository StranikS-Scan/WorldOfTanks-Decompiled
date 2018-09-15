# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DormantSelectableObject.py
from ClientSelectableObject import ClientSelectableObject
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager

class DormantSelectableObject(ClientSelectableObject):
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self, edgeMode=2):
        super(DormantSelectableObject, self).__init__(edgeMode)
        super(DormantSelectableObject, self).enable(False)

    def onEnterWorld(self, prereqs):
        super(DormantSelectableObject, self).onEnterWorld(prereqs)
        if self.isSelectable:
            self.customizableObjectsMgr.addSelectableEntity(self)
            self.enable(True)

    def onLeaveWorld(self):
        if self.isSelectable:
            self.customizableObjectsMgr.removeSelectableEntity(self)
        super(DormantSelectableObject, self).onLeaveWorld()

    def collideSegment(self, startPoint, endPoint, skipGun=False):
        return super(DormantSelectableObject, self).collideSegment(startPoint, endPoint, skipGun) if self.isSelectable else None

    def enable(self, enabled):
        if self.isSelectable:
            super(DormantSelectableObject, self).enable(enabled)

    def onClicked(self):
        if self.isSelectable:
            super(DormantSelectableObject, self).onClicked()
            self._doClick()

    def _doClick(self):
        pass

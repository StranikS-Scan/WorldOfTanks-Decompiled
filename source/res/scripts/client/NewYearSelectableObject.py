# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearSelectableObject.py
from ClientSelectableObject import ClientSelectableObject
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager

class NewYearSelectableObject(ClientSelectableObject):
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self):
        super(NewYearSelectableObject, self).__init__(0)
        if self.singleTargetCaps > 0:
            self.targetCaps = [self.singleTargetCaps]

    def onEnterWorld(self, prereqs):
        super(NewYearSelectableObject, self).onEnterWorld(prereqs)
        self.customizableObjectsMgr.addSelectableEntity(self)

    def onLeaveWorld(self):
        super(NewYearSelectableObject, self).onLeaveWorld()
        self.customizableObjectsMgr.removeSelectableEntity(self)

    def onClicked(self):
        super(NewYearSelectableObject, self).onClicked()
        self.customizableObjectsMgr.switchTo(self.anchorName)

    def _castsShadow(self):
        return False

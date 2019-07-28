# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomizableHB1SceneObject.py
from helpers import dependency
from ClientSelectableObject import ClientSelectableObject
from skeletons.hb1 import ICustomizableObjectsManager

class CustomizableHB1SceneObject(ClientSelectableObject):
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def onEnterWorld(self, prereqs):
        super(CustomizableHB1SceneObject, self).onEnterWorld(prereqs)
        self.customizableObjectsMgr.addCustomizableEntity(self)

    def onLeaveWorld(self):
        self.customizableObjectsMgr.removeCustomizableEntity(self)
        super(CustomizableHB1SceneObject, self).onLeaveWorld()

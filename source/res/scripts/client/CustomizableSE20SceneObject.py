# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomizableSE20SceneObject.py
from helpers import dependency
from ClientSelectableObject import ClientSelectableObject
from skeletons.se20 import ICustomizableObjectsManager

class CustomizableSE20SceneObject(ClientSelectableObject):
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def onEnterWorld(self, prereqs):
        super(CustomizableSE20SceneObject, self).onEnterWorld(prereqs)
        self.customizableObjectsMgr.addCustomizableEntity(self)

    def onLeaveWorld(self):
        self.customizableObjectsMgr.removeCustomizableEntity(self)
        super(CustomizableSE20SceneObject, self).onLeaveWorld()

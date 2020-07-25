# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/GFTutorialViewMeta.py
from gui.Scaleform.framework.entities.View import View

class GFTutorialViewMeta(View):

    def as_createHintAreaInComponentS(self, componentName, hintName, posX, posY, width, height):
        return self.flashObject.as_createHintAreaInComponent(componentName, hintName, posX, posY, width, height) if self._isDAAPIInited() else None

    def as_removeHintAreaS(self, hintName):
        return self.flashObject.as_removeHintArea(hintName) if self._isDAAPIInited() else None

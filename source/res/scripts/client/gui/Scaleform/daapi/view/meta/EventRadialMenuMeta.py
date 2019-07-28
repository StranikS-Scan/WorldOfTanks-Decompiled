# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventRadialMenuMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventRadialMenuMeta(BaseDAAPIComponent):

    def showHandCursor(self):
        self._printOverrideError('showHandCursor')

    def hideHandCursor(self):
        self._printOverrideError('hideHandCursor')

    def as_showWithNameS(self, radialState, offset, ratio, targetDisplayName):
        return self.flashObject.as_showWithName(radialState, offset, ratio, targetDisplayName) if self._isDAAPIInited() else None

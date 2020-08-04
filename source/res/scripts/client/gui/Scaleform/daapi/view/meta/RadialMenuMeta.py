# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RadialMenuMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RadialMenuMeta(BaseDAAPIComponent):

    def onSelect(self):
        self._printOverrideError('onSelect')

    def onAction(self, action):
        self._printOverrideError('onAction')

    def onHideCompleted(self):
        self._printOverrideError('onHideCompleted')

    def as_buildDataS(self, data):
        return self.flashObject.as_buildData(data) if self._isDAAPIInited() else None

    def as_showS(self, cursorX, cursorY, radialState, replyStateDiff, offset):
        return self.flashObject.as_show(cursorX, cursorY, radialState, replyStateDiff, offset) if self._isDAAPIInited() else None

    def as_hideS(self, allowAction):
        return self.flashObject.as_hide(allowAction) if self._isDAAPIInited() else None

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventAwardScreenMeta.py
from gui.Scaleform.framework.entities.View import View

class EventAwardScreenMeta(View):

    def onCloseWindow(self):
        self._printOverrideError('onCloseWindow')

    def onPlaySound(self, soundType):
        self._printOverrideError('onPlaySound')

    def onButton(self):
        self._printOverrideError('onButton')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setCloseBtnEnabledS(self, enabled):
        return self.flashObject.as_setCloseBtnEnabled(enabled) if self._isDAAPIInited() else None

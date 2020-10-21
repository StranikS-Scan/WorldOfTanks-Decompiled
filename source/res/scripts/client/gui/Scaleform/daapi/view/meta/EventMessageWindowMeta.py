# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventMessageWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class EventMessageWindowMeta(AbstractWindowView):

    def onResult(self, ok):
        self._printOverrideError('onResult')

    def as_setMessageDataS(self, value):
        return self.flashObject.as_setMessageData(value) if self._isDAAPIInited() else None

    def as_blurOtherWindowsS(self, container):
        return self.flashObject.as_blurOtherWindows(container) if self._isDAAPIInited() else None

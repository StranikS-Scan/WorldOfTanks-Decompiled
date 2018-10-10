# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCQueueWindowMeta.py
from gui.Scaleform.framework.entities.View import View

class BCQueueWindowMeta(View):

    def cancel(self):
        self._printOverrideError('cancel')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_showCancelButtonS(self, value, label, info):
        return self.flashObject.as_showCancelButton(value, label, info) if self._isDAAPIInited() else None

    def as_setStatusTextS(self, value):
        return self.flashObject.as_setStatusText(value) if self._isDAAPIInited() else None

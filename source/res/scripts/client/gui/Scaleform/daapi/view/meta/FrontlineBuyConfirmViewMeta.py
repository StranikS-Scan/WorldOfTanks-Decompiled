# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FrontlineBuyConfirmViewMeta.py
from gui.Scaleform.framework.entities.View import View

class FrontlineBuyConfirmViewMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onBuy(self):
        self._printOverrideError('onBuy')

    def onBack(self):
        self._printOverrideError('onBack')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

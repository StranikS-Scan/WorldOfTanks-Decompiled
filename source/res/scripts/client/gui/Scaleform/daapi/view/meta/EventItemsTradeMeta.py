# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventItemsTradeMeta.py
from gui.Scaleform.framework.entities.View import View

class EventItemsTradeMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def backView(self):
        self._printOverrideError('backView')

    def onButtonPaymentPanelClick(self, count):
        self._printOverrideError('onButtonPaymentPanelClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_updateTokensS(self, value):
        return self.flashObject.as_updateTokens(value) if self._isDAAPIInited() else None

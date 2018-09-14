# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PremiumWindowMeta.py
from gui.Scaleform.daapi.view.meta.SimpleWindowMeta import SimpleWindowMeta

class PremiumWindowMeta(SimpleWindowMeta):

    def onRateClick(self, rateId):
        self._printOverrideError('onRateClick')

    def as_setHeaderS(self, prc, bonus1, bonus2):
        return self.flashObject.as_setHeader(prc, bonus1, bonus2) if self._isDAAPIInited() else None

    def as_setRatesS(self, header, rates, selectedRateId):
        return self.flashObject.as_setRates(header, rates, selectedRateId) if self._isDAAPIInited() else None

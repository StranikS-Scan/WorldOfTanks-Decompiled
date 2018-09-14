# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PremiumWindowMeta.py
from gui.Scaleform.daapi.view.meta.SimpleWindowMeta import SimpleWindowMeta

class PremiumWindowMeta(SimpleWindowMeta):

    def onTariffClick(self, tariffId):
        self._printOverrideError('onTariffClick')

    def as_setHeaderS(self, prc, bonus1, bonus2):
        if self._isDAAPIInited():
            return self.flashObject.as_setHeader(prc, bonus1, bonus2)

    def as_setTariffsS(self, header, tarifs, selectedTariffId):
        if self._isDAAPIInited():
            return self.flashObject.as_setTariffs(header, tarifs, selectedTariffId)

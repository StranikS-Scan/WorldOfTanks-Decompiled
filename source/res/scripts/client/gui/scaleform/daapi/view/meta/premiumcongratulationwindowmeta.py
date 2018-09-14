# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PremiumCongratulationWindowMeta.py
from gui.Scaleform.daapi.view.meta.SimpleWindowMeta import SimpleWindowMeta

class PremiumCongratulationWindowMeta(SimpleWindowMeta):

    def onToBuyClick(self):
        self._printOverrideError('onToBuyClick')

    def as_setDataS(self, imagePath, percent, btnLabel):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(imagePath, percent, btnLabel)

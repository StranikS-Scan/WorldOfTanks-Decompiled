# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationBuyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class CustomizationBuyWindowMeta(AbstractWindowView):

    def buy(self):
        self._printOverrideError('buy')

    def selectItem(self, id):
        self._printOverrideError('selectItem')

    def deselectItem(self, id):
        self._printOverrideError('deselectItem')

    def changePriceItem(self, id, priceMode):
        self._printOverrideError('changePriceItem')

    def applyToTankChanged(self, selected):
        self._printOverrideError('applyToTankChanged')

    def as_getPurchaseDPS(self):
        return self.flashObject.as_getPurchaseDP() if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setTotalDataS(self, data):
        return self.flashObject.as_setTotalData(data) if self._isDAAPIInited() else None

    def as_setBuyBtnStateS(self, isEnabled, label):
        return self.flashObject.as_setBuyBtnState(isEnabled, label) if self._isDAAPIInited() else None

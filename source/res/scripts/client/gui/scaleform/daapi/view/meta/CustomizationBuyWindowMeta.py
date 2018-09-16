# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationBuyWindowMeta.py
from gui.Scaleform.framework.entities.View import View

class CustomizationBuyWindowMeta(View):

    def buy(self):
        self._printOverrideError('buy')

    def close(self):
        self._printOverrideError('close')

    def selectItem(self, id, fromStorage):
        self._printOverrideError('selectItem')

    def deselectItem(self, id, fromStorage):
        self._printOverrideError('deselectItem')

    def changePriceItem(self, id, priceMode):
        self._printOverrideError('changePriceItem')

    def applyToTankChanged(self, selected):
        self._printOverrideError('applyToTankChanged')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setTitlesS(self, data):
        return self.flashObject.as_setTitles(data) if self._isDAAPIInited() else None

    def as_setTotalDataS(self, data):
        return self.flashObject.as_setTotalData(data) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setBuyBtnStateS(self, isEnabled, label):
        return self.flashObject.as_setBuyBtnState(isEnabled, label) if self._isDAAPIInited() else None

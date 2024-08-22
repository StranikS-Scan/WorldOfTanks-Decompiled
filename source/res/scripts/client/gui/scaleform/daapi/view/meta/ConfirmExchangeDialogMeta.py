# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ConfirmExchangeDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ConfirmExchangeDialogMeta(AbstractWindowView):

    def exchange(self, goldValue):
        self._printOverrideError('exchange')

    def onSelectedAmountChanged(self, goldValue, needItemsValue):
        self._printOverrideError('onSelectedAmountChanged')

    def openDiscountInfoPage(self):
        self._printOverrideError('openDiscountInfoPage')

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None

    def as_setExchangeValuesS(self, goldValue, needItemsValue, discountsAmountApplied):
        return self.flashObject.as_setExchangeValues(goldValue, needItemsValue, discountsAmountApplied) if self._isDAAPIInited() else None

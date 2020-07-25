# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/deal_panel_model.py
from gui.impl.gen.view_models.common.price_model import PriceModel

class DealPanelModel(PriceModel):
    __slots__ = ('onDealConfirmed', 'onDealCancelled', 'onAutoRenewalChanged')
    GENERAL = 'general'
    REPAIR = 'repair'

    def __init__(self, properties=9, commands=3):
        super(DealPanelModel, self).__init__(properties=properties, commands=commands)

    def getDealType(self):
        return self._getString(3)

    def setDealType(self, value):
        self._setString(3, value)

    def getCanAccept(self):
        return self._getBool(4)

    def setCanAccept(self, value):
        self._setBool(4, value)

    def getCanCancel(self):
        return self._getBool(5)

    def setCanCancel(self, value):
        self._setBool(5, value)

    def getIsAutoRenewalEnabled(self):
        return self._getBool(6)

    def setIsAutoRenewalEnabled(self, value):
        self._setBool(6, value)

    def getIsDisabled(self):
        return self._getBool(7)

    def setIsDisabled(self, value):
        self._setBool(7, value)

    def getTotalItemsInStorage(self):
        return self._getNumber(8)

    def setTotalItemsInStorage(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(DealPanelModel, self)._initialize()
        self._addStringProperty('dealType', '')
        self._addBoolProperty('canAccept', False)
        self._addBoolProperty('canCancel', True)
        self._addBoolProperty('isAutoRenewalEnabled', False)
        self._addBoolProperty('isDisabled', False)
        self._addNumberProperty('totalItemsInStorage', 0)
        self.onDealConfirmed = self._addCommand('onDealConfirmed')
        self.onDealCancelled = self._addCommand('onDealCancelled')
        self.onAutoRenewalChanged = self._addCommand('onAutoRenewalChanged')

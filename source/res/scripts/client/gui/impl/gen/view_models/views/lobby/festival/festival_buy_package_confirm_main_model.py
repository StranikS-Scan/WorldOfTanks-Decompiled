# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_buy_package_confirm_main_model.py
from frameworks.wulf import ViewModel

class FestivalBuyPackageConfirmMainModel(ViewModel):
    __slots__ = ()

    def getItemName(self):
        return self._getString(0)

    def setItemName(self, value):
        self._setString(0, value)

    def getItemTypeName(self):
        return self._getString(1)

    def setItemTypeName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(FestivalBuyPackageConfirmMainModel, self)._initialize()
        self._addStringProperty('itemName', '')
        self._addStringProperty('itemTypeName', '')

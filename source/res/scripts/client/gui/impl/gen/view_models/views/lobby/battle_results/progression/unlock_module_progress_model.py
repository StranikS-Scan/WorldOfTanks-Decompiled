# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/unlock_module_progress_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel

class UnlockModuleProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(UnlockModuleProgressModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceItemModel

    def getModuleId(self):
        return self._getNumber(1)

    def setModuleId(self, value):
        self._setNumber(1, value)

    def getItemTypeName(self):
        return self._getString(2)

    def setItemTypeName(self, value):
        self._setString(2, value)

    def getUserName(self):
        return self._getString(3)

    def setUserName(self, value):
        self._setString(3, value)

    def getIconName(self):
        return self._getString(4)

    def setIconName(self, value):
        self._setString(4, value)

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(UnlockModuleProgressModel, self)._initialize()
        self._addViewModelProperty('price', PriceItemModel())
        self._addNumberProperty('moduleId', 0)
        self._addStringProperty('itemTypeName', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('iconName', '')
        self._addNumberProperty('level', 0)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/common/preset_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class PresetDisableReason(Enum):
    NONE = 'none'
    DEMOUNT_NOT_POSSIBLE = 'demountNotPossible'
    LOAD_CAPACITY_NOT_ENOUGH = 'loadCapacityNotEnough'
    NOT_ENOUGH_BUNKS = 'notEnoughBunks'


class PresetModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PresetModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getInstalled(self):
        return self._getBool(1)

    def setInstalled(self, value):
        self._setBool(1, value)

    def getDisableReason(self):
        return PresetDisableReason(self._getString(2))

    def setDisableReason(self, value):
        self._setString(2, value.value)

    def getStoredItemsCount(self):
        return self._getNumber(3)

    def setStoredItemsCount(self, value):
        self._setNumber(3, value)

    def getInstalledItemsCount(self):
        return self._getNumber(4)

    def setInstalledItemsCount(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(PresetModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addBoolProperty('installed', False)
        self._addStringProperty('disableReason')
        self._addNumberProperty('storedItemsCount', 0)
        self._addNumberProperty('installedItemsCount', 0)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/clan_supply/stage_info_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class ScreenStatus(IntEnum):
    PENDING = 0
    ERROR = 1
    LOADED = 2


class StageInfoStatus(IntEnum):
    AVAILABLE = 0
    PURCHASED = 1
    UNAVAILABLE = 2


class StageInfoModel(ViewModel):
    __slots__ = ('onRefresh',)

    def __init__(self, properties=9, commands=1):
        super(StageInfoModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIsPremium(self):
        return self._getBool(1)

    def setIsPremium(self, value):
        self._setBool(1, value)

    def getIsBuyLoading(self):
        return self._getBool(2)

    def setIsBuyLoading(self, value):
        self._setBool(2, value)

    def getStatus(self):
        return ScreenStatus(self._getNumber(3))

    def setStatus(self, value):
        self._setNumber(3, value.value)

    def getStageStatus(self):
        return StageInfoStatus(self._getNumber(4))

    def setStageStatus(self, value):
        self._setNumber(4, value.value)

    def getIsEnoughMoney(self):
        return self._getBool(5)

    def setIsEnoughMoney(self, value):
        self._setBool(5, value)

    def getPrice(self):
        return self._getNumber(6)

    def setPrice(self, value):
        self._setNumber(6, value)

    def getDeficiencyAmount(self):
        return self._getNumber(7)

    def setDeficiencyAmount(self, value):
        self._setNumber(7, value)

    def getRewards(self):
        return self._getArray(8)

    def setRewards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(StageInfoModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addBoolProperty('isPremium', False)
        self._addBoolProperty('isBuyLoading', False)
        self._addNumberProperty('status')
        self._addNumberProperty('stageStatus')
        self._addBoolProperty('isEnoughMoney', True)
        self._addNumberProperty('price', 0)
        self._addNumberProperty('deficiencyAmount', 0)
        self._addArrayProperty('rewards', Array())
        self.onRefresh = self._addCommand('onRefresh')

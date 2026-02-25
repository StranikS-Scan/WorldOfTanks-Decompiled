# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/reset_branch_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.reset_vehicle_info_model import ResetVehicleInfoModel

class ResetState(IntEnum):
    INITIAL = 0
    SUCCESS = 1
    FAILED = 2


class ResetBranchViewModel(ViewModel):
    __slots__ = ('onClose', 'onConfirm', 'onInstallVehicleConfiguration')
    VEHICLE_CONFIGURATION_KEY = 'configuration'
    CURRENT_VALUE_KEY = 'current'
    STOCK_VALUE_KEY = 'stock'

    def __init__(self, properties=9, commands=3):
        super(ResetBranchViewModel, self).__init__(properties=properties, commands=commands)

    def getResetState(self):
        return ResetState(self._getNumber(0))

    def setResetState(self, value):
        self._setNumber(0, value.value)

    def getIsFill(self):
        return self._getBool(1)

    def setIsFill(self, value):
        self._setBool(1, value)

    def getCanEquipStock(self):
        return self._getBool(2)

    def setCanEquipStock(self, value):
        self._setBool(2, value)

    def getResetBranchesCount(self):
        return self._getNumber(3)

    def setResetBranchesCount(self, value):
        self._setNumber(3, value)

    def getMaxResetBranchesCount(self):
        return self._getNumber(4)

    def setMaxResetBranchesCount(self, value):
        self._setNumber(4, value)

    def getResetVehicles(self):
        return self._getArray(5)

    def setResetVehicles(self, value):
        self._setArray(5, value)

    @staticmethod
    def getResetVehiclesType():
        return ResetVehicleInfoModel

    def getTotalCredits(self):
        return self._getNumber(6)

    def setTotalCredits(self, value):
        self._setNumber(6, value)

    def getCompleteBonusCoins(self):
        return self._getNumber(7)

    def setCompleteBonusCoins(self, value):
        self._setNumber(7, value)

    def getCoinsForBranchReset(self):
        return self._getNumber(8)

    def setCoinsForBranchReset(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(ResetBranchViewModel, self)._initialize()
        self._addNumberProperty('resetState', ResetState.INITIAL.value)
        self._addBoolProperty('isFill', False)
        self._addBoolProperty('canEquipStock', False)
        self._addNumberProperty('resetBranchesCount', 0)
        self._addNumberProperty('maxResetBranchesCount', 0)
        self._addArrayProperty('resetVehicles', Array())
        self._addNumberProperty('totalCredits', 0)
        self._addNumberProperty('completeBonusCoins', 0)
        self._addNumberProperty('coinsForBranchReset', 0)
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
        self.onInstallVehicleConfiguration = self._addCommand('onInstallVehicleConfiguration')

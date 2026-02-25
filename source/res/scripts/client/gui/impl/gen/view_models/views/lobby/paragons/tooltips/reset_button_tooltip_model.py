# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/reset_button_tooltip_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.paragons_tooltip_vehicles_model import ParagonsTooltipVehiclesModel

class FeatureState(IntEnum):
    IS_ACTIVE = 0
    IS_PAUSED = 1
    LIMIT_REACHED = 2
    PARAGONS_NOT_AVAILABLE = 3
    VEHICLES_REQUIRED = 4
    RULES_INCOMLETED = 5
    FIRST_BRANCH_RESET = 6
    DROPPED_BRANCH = 7


class ResetButtonTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(ResetButtonTooltipModel, self).__init__(properties=properties, commands=commands)

    def getResetBranchesCount(self):
        return self._getNumber(0)

    def setResetBranchesCount(self, value):
        self._setNumber(0, value)

    def getMaxResetBranchesCount(self):
        return self._getNumber(1)

    def setMaxResetBranchesCount(self, value):
        self._setNumber(1, value)

    def getCredits(self):
        return self._getNumber(2)

    def setCredits(self, value):
        self._setNumber(2, value)

    def getParagonsPoints(self):
        return self._getNumber(3)

    def setParagonsPoints(self, value):
        self._setNumber(3, value)

    def getBranchResetPoints(self):
        return self._getNumber(4)

    def setBranchResetPoints(self, value):
        self._setNumber(4, value)

    def getWinPoints(self):
        return self._getNumber(5)

    def setWinPoints(self, value):
        self._setNumber(5, value)

    def getBonusPoints(self):
        return self._getNumber(6)

    def setBonusPoints(self, value):
        self._setNumber(6, value)

    def getState(self):
        return FeatureState(self._getNumber(7))

    def setState(self, value):
        self._setNumber(7, value.value)

    def getVehicleCount(self):
        return self._getNumber(8)

    def setVehicleCount(self, value):
        self._setNumber(8, value)

    def getNecessaryVehicleCount(self):
        return self._getNumber(9)

    def setNecessaryVehicleCount(self, value):
        self._setNumber(9, value)

    def getBattleTypes(self):
        return self._getArray(10)

    def setBattleTypes(self, value):
        self._setArray(10, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def getVehicles(self):
        return self._getArray(11)

    def setVehicles(self, value):
        self._setArray(11, value)

    @staticmethod
    def getVehiclesType():
        return ParagonsTooltipVehiclesModel

    def _initialize(self):
        super(ResetButtonTooltipModel, self)._initialize()
        self._addNumberProperty('resetBranchesCount', 0)
        self._addNumberProperty('maxResetBranchesCount', 0)
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('paragonsPoints', 0)
        self._addNumberProperty('branchResetPoints', 0)
        self._addNumberProperty('winPoints', 0)
        self._addNumberProperty('bonusPoints', 0)
        self._addNumberProperty('state', FeatureState.IS_ACTIVE.value)
        self._addNumberProperty('vehicleCount', 0)
        self._addNumberProperty('necessaryVehicleCount', 0)
        self._addArrayProperty('battleTypes', Array())
        self._addArrayProperty('vehicles', Array())

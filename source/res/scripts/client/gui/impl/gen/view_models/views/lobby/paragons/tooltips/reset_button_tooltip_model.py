# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/reset_button_tooltip_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.paragons_tooltip_vehicles_model import ParagonsTooltipVehiclesModel

class FeatureState(IntEnum):
    IS_PAUSED = 1
    LIMIT_REACHED = 2
    VEHICLES_REQUERED = 3
    RULES_INCOMLETED = 4
    IS_ACTIVE = 0


class ResetButtonTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
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

    def getState(self):
        return self._getNumber(4)

    def setState(self, value):
        self._setNumber(4, value)

    def getVehicleCount(self):
        return self._getNumber(5)

    def setVehicleCount(self, value):
        self._setNumber(5, value)

    def getNecessaryVehicleCount(self):
        return self._getNumber(6)

    def setNecessaryVehicleCount(self, value):
        self._setNumber(6, value)

    def getVehicles(self):
        return self._getArray(7)

    def setVehicles(self, value):
        self._setArray(7, value)

    @staticmethod
    def getVehiclesType():
        return ParagonsTooltipVehiclesModel

    def _initialize(self):
        super(ResetButtonTooltipModel, self)._initialize()
        self._addNumberProperty('resetBranchesCount', 0)
        self._addNumberProperty('maxResetBranchesCount', 0)
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('paragonsPoints', 0)
        self._addNumberProperty('state', FeatureState.IS_PAUSED)
        self._addNumberProperty('vehicleCount', 0)
        self._addNumberProperty('necessaryVehicleCount', 0)
        self._addArrayProperty('vehicles', Array())

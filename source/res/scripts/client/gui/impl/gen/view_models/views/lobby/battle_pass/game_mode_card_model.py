# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/game_mode_card_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.vehicle_item_model import VehicleItemModel

class PointsCardType(IntEnum):
    TECH = 0
    LIMIT = 1
    DAILY = 2
    BATTLE = 3
    EPIC_BATTLE_POINTS = 4
    COMP7 = 5


class GameModeCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(GameModeCardModel, self).__init__(properties=properties, commands=commands)

    def getCardType(self):
        return PointsCardType(self._getNumber(0))

    def setCardType(self, value):
        self._setNumber(0, value.value)

    def getViewId(self):
        return self._getString(1)

    def setViewId(self, value):
        self._setString(1, value)

    def getVehiclesList(self):
        return self._getArray(2)

    def setVehiclesList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesListType():
        return VehicleItemModel

    def _initialize(self):
        super(GameModeCardModel, self)._initialize()
        self._addNumberProperty('cardType')
        self._addStringProperty('viewId', '')
        self._addArrayProperty('vehiclesList', Array())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/game_mode_card_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.vehicle_item_model import VehicleItemModel

class PointsCardType(IntEnum):
    TECH = 0
    LIMIT = 1
    DAILY = 2
    BATTLE = 3
    EPIC_BATTLE_POINTS = 4


class GameModeCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(GameModeCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehiclesList(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehiclesListType():
        return VehicleItemModel

    def getCardType(self):
        return PointsCardType(self._getNumber(1))

    def setCardType(self, value):
        self._setNumber(1, value.value)

    def getViewId(self):
        return self._getString(2)

    def setViewId(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(GameModeCardModel, self)._initialize()
        self._addViewModelProperty('vehiclesList', UserListModel())
        self._addNumberProperty('cardType')
        self._addStringProperty('viewId', '')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/yearly_rewards_card_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.comp7_bonus_model import Comp7BonusModel
from comp7.gui.impl.gen.view_models.views.lobby.season_point_model import SeasonPointModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class RewardsState(Enum):
    GUARANTEED = 'guaranteed'
    POSSIBLE = 'possible'
    NOTAVAILABLE = 'notAvailable'
    CLAIMED = 'claimed'


class YearlyRewardsCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(YearlyRewardsCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return Comp7BonusModel

    def getSeasonPoints(self):
        return self._getArray(2)

    def setSeasonPoints(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSeasonPointsType():
        return SeasonPointModel

    def getRewardsState(self):
        return RewardsState(self._getString(3))

    def setRewardsState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(YearlyRewardsCardModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('seasonPoints', Array())
        self._addStringProperty('rewardsState')

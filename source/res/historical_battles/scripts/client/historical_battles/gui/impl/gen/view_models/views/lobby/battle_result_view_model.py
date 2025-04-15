# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/battle_result_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import BaseTeamMemberModel
from historical_battles.gui.impl.gen.view_models.views.common.hb_coin_model import HbCoinModel
from historical_battles.gui.impl.gen.view_models.views.common.stat_column_settings_model import StatColumnSettingsModel
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_info_model import BattleInfoModel
from historical_battles.gui.impl.gen.view_models.views.lobby.player_info_model import PlayerInfoModel
from historical_battles.gui.impl.gen.view_models.views.lobby.reward_info_model import RewardInfoModel

class BattleResultType(Enum):
    WIN = 'win'
    LOSE = 'lose'
    TIE = 'draw'
    ENDED = 'ended'


class FairplayStatus(Enum):
    PLAYER = 'player'
    DESERTER = 'deserter'
    AFK = 'afk'


class BoosterType(Enum):
    EMPTY = 'empty'
    X1 = 'x1'
    X5 = 'x5'
    X10 = 'x10'
    X15 = 'x15'


class BattleResultViewModel(ViewModel):
    __slots__ = ('onClose', 'onApplyBooster')

    def __init__(self, properties=14, commands=2):
        super(BattleResultViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def earnings(self):
        return self._getViewModel(0)

    @staticmethod
    def getEarningsType():
        return HbCoinModel

    @property
    def rewardInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getRewardInfoType():
        return RewardInfoModel

    @property
    def battleInfo(self):
        return self._getViewModel(2)

    @staticmethod
    def getBattleInfoType():
        return BattleInfoModel

    @property
    def playerInfo(self):
        return self._getViewModel(3)

    @staticmethod
    def getPlayerInfoType():
        return PlayerInfoModel

    @property
    def columnSettings(self):
        return self._getViewModel(4)

    @staticmethod
    def getColumnSettingsType():
        return StatColumnSettingsModel

    def getTitle(self):
        return self._getResource(5)

    def setTitle(self, value):
        self._setResource(5, value)

    def getSubTitle(self):
        return self._getResource(6)

    def setSubTitle(self, value):
        self._setResource(6, value)

    def getFrontName(self):
        return self._getString(7)

    def setFrontName(self, value):
        self._setString(7, value)

    def getResultType(self):
        return BattleResultType(self._getString(8))

    def setResultType(self, value):
        self._setString(8, value.value)

    def getFairplayStatus(self):
        return FairplayStatus(self._getString(9))

    def setFairplayStatus(self, value):
        self._setString(9, value.value)

    def getBoosterType(self):
        return BoosterType(self._getString(10))

    def setBoosterType(self, value):
        self._setString(10, value.value)

    def getBoosterCount(self):
        return self._getNumber(11)

    def setBoosterCount(self, value):
        self._setNumber(11, value)

    def getIsBoosterUsed(self):
        return self._getBool(12)

    def setIsBoosterUsed(self, value):
        self._setBool(12, value)

    def getTeam(self):
        return self._getArray(13)

    def setTeam(self, value):
        self._setArray(13, value)

    @staticmethod
    def getTeamType():
        return BaseTeamMemberModel

    def _initialize(self):
        super(BattleResultViewModel, self)._initialize()
        self._addViewModelProperty('earnings', HbCoinModel())
        self._addViewModelProperty('rewardInfo', RewardInfoModel())
        self._addViewModelProperty('battleInfo', BattleInfoModel())
        self._addViewModelProperty('playerInfo', PlayerInfoModel())
        self._addViewModelProperty('columnSettings', StatColumnSettingsModel())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addStringProperty('frontName', '')
        self._addStringProperty('resultType')
        self._addStringProperty('fairplayStatus')
        self._addStringProperty('boosterType')
        self._addNumberProperty('boosterCount', 0)
        self._addBoolProperty('isBoosterUsed', False)
        self._addArrayProperty('team', Array())
        self.onClose = self._addCommand('onClose')
        self.onApplyBooster = self._addCommand('onApplyBooster')

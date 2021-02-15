# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_in_progress_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_royale_reward_points import BattleRoyaleRewardPoints
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel

class BattlePassInProgressTooltipViewModel(ViewModel):
    __slots__ = ()
    GAME_MODE_UNKNOWN = 'unknown'
    GAME_MODE_RANDOM_BATTLES = 'randomBattles'
    GAME_MODE_BATTLE_ROYALE = 'battleRoyale'
    GAME_MODE_RANKED_BATTLES = 'ranked'

    def __init__(self, properties=14, commands=0):
        super(BattlePassInProgressTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardPoints(self):
        return self._getViewModel(0)

    @property
    def battleRoyaleRewardPoints(self):
        return self._getViewModel(1)

    @property
    def rewardsCommon(self):
        return self._getViewModel(2)

    @property
    def rewardsElite(self):
        return self._getViewModel(3)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getCurrentPoints(self):
        return self._getNumber(5)

    def setCurrentPoints(self, value):
        self._setNumber(5, value)

    def getMaxPoints(self):
        return self._getNumber(6)

    def setMaxPoints(self, value):
        self._setNumber(6, value)

    def getIsBattlePassPurchased(self):
        return self._getBool(7)

    def setIsBattlePassPurchased(self, value):
        self._setBool(7, value)

    def getIsSpecialVehicle(self):
        return self._getBool(8)

    def setIsSpecialVehicle(self, value):
        self._setBool(8, value)

    def getVideoName(self):
        return self._getString(9)

    def setVideoName(self, value):
        self._setString(9, value)

    def getIsPostProgression(self):
        return self._getBool(10)

    def setIsPostProgression(self, value):
        self._setBool(10, value)

    def getTimeTillEnd(self):
        return self._getString(11)

    def setTimeTillEnd(self, value):
        self._setString(11, value)

    def getCanPlay(self):
        return self._getBool(12)

    def setCanPlay(self, value):
        self._setBool(12, value)

    def getGameMode(self):
        return self._getString(13)

    def setGameMode(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(BattlePassInProgressTooltipViewModel, self)._initialize()
        self._addViewModelProperty('rewardPoints', UserListModel())
        self._addViewModelProperty('battleRoyaleRewardPoints', BattleRoyaleRewardPoints())
        self._addViewModelProperty('rewardsCommon', UserListModel())
        self._addViewModelProperty('rewardsElite', UserListModel())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addBoolProperty('isBattlePassPurchased', False)
        self._addBoolProperty('isSpecialVehicle', False)
        self._addStringProperty('videoName', '')
        self._addBoolProperty('isPostProgression', False)
        self._addStringProperty('timeTillEnd', '')
        self._addBoolProperty('canPlay', False)
        self._addStringProperty('gameMode', '')

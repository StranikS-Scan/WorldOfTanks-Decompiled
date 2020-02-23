# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_in_progress_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel

class BattlePassInProgressTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(BattlePassInProgressTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardPoints(self):
        return self._getViewModel(0)

    @property
    def rewards(self):
        return self._getViewModel(1)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getCurrentPoints(self):
        return self._getNumber(3)

    def setCurrentPoints(self, value):
        self._setNumber(3, value)

    def getMaxPoints(self):
        return self._getNumber(4)

    def setMaxPoints(self, value):
        self._setNumber(4, value)

    def getIsBattlePassPurchased(self):
        return self._getBool(5)

    def setIsBattlePassPurchased(self, value):
        self._setBool(5, value)

    def getIsSpecialVehicle(self):
        return self._getBool(6)

    def setIsSpecialVehicle(self, value):
        self._setBool(6, value)

    def getVideoName(self):
        return self._getString(7)

    def setVideoName(self, value):
        self._setString(7, value)

    def getIsPostProgression(self):
        return self._getBool(8)

    def setIsPostProgression(self, value):
        self._setBool(8, value)

    def getTimeTillEnd(self):
        return self._getString(9)

    def setTimeTillEnd(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(BattlePassInProgressTooltipViewModel, self)._initialize()
        self._addViewModelProperty('rewardPoints', UserListModel())
        self._addViewModelProperty('rewards', UserListModel())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addBoolProperty('isBattlePassPurchased', False)
        self._addBoolProperty('isSpecialVehicle', False)
        self._addStringProperty('videoName', '')
        self._addBoolProperty('isPostProgression', False)
        self._addStringProperty('timeTillEnd', '')

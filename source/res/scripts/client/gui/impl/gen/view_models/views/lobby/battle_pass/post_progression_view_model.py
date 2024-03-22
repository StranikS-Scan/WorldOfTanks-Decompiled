# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/post_progression_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.awards_widget_model import AwardsWidgetModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_rewards_view_model import BattlePassBuyRewardsViewModel

class ChapterStates(IntEnum):
    ACTIVE = 0
    PAUSED = 1
    COMPLETED = 2
    NOTSTARTED = 3


class PostProgressionViewModel(ViewModel):
    __slots__ = ('showRewards', 'onTakeRewardsClick', 'showTankmen', 'onBackClick', 'onPreviewVehicle', 'showVehicle', 'showBuy', 'onClose')
    BUY_STATE = 'buyState'
    REWARDS_STATE = 'rewardsState'
    TANKMEN_STATE = 'tankmenState'
    SELECTABLE_REWARDS_STATE = 'selectableRewardsState'
    FINAL_STATE = 'finalState'

    def __init__(self, properties=10, commands=8):
        super(PostProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return BattlePassBuyRewardsViewModel

    @property
    def awardsWidget(self):
        return self._getViewModel(1)

    @staticmethod
    def getAwardsWidgetType():
        return AwardsWidgetModel

    def getState(self):
        return self._getString(2)

    def setState(self, value):
        self._setString(2, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(3)

    def setNotChosenRewardCount(self, value):
        self._setNumber(3, value)

    def getIsChooseRewardsEnabled(self):
        return self._getBool(4)

    def setIsChooseRewardsEnabled(self, value):
        self._setBool(4, value)

    def getIsSpecialVoiceTankmen(self):
        return self._getBool(5)

    def setIsSpecialVoiceTankmen(self, value):
        self._setBool(5, value)

    def getChapterID(self):
        return self._getNumber(6)

    def setChapterID(self, value):
        self._setNumber(6, value)

    def getCurrentLevel(self):
        return self._getNumber(7)

    def setCurrentLevel(self, value):
        self._setNumber(7, value)

    def getChapterState(self):
        return ChapterStates(self._getNumber(8))

    def setChapterState(self, value):
        self._setNumber(8, value.value)

    def getIsSeasonEndingSoon(self):
        return self._getBool(9)

    def setIsSeasonEndingSoon(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(PostProgressionViewModel, self)._initialize()
        self._addViewModelProperty('rewards', BattlePassBuyRewardsViewModel())
        self._addViewModelProperty('awardsWidget', AwardsWidgetModel())
        self._addStringProperty('state', 'buyState')
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addBoolProperty('isChooseRewardsEnabled', True)
        self._addBoolProperty('isSpecialVoiceTankmen', True)
        self._addNumberProperty('chapterID', 0)
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('chapterState')
        self._addBoolProperty('isSeasonEndingSoon', False)
        self.showRewards = self._addCommand('showRewards')
        self.onTakeRewardsClick = self._addCommand('onTakeRewardsClick')
        self.showTankmen = self._addCommand('showTankmen')
        self.onBackClick = self._addCommand('onBackClick')
        self.onPreviewVehicle = self._addCommand('onPreviewVehicle')
        self.showVehicle = self._addCommand('showVehicle')
        self.showBuy = self._addCommand('showBuy')
        self.onClose = self._addCommand('onClose')

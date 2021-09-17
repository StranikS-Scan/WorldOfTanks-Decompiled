# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/random_mode_selector_item.py
from battle_pass_common import BattlePassState
from gui.battle_pass.battle_pass_helpers import getNotChosen3DStylesCount
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_random_battle_model import ModeSelectorRandomBattleModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_random_battle_widget_model import ModeSelectorRandomBattleWidgetModel, ProgressionState
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared import g_eventBus
from gui.shared.events import ModeSelectorPopoverEvent
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class RandomModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorRandomBattleModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.RANDOM
    __battlePassController = dependency.instance(IBattlePassController)

    @property
    def viewModel(self):
        return super(RandomModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(RandomModeSelectorItem, self)._onInitializing()
        self.setPopoverState(False)
        self.__onBattlePassUpdate()
        if self._bootcamp.isInBootcamp():
            self.viewModel.setIsDisabled(False)
        g_eventBus.addListener(ModeSelectorPopoverEvent.NAME, self.randomBattlePopoverStatusChangeCallback)
        self.__battlePassController.onPointsUpdated += self.__onBattlePassUpdate
        self.__battlePassController.onSeasonStateChange += self.__onBattlePassUpdate
        self.__battlePassController.onBattlePassSettingsChange += self.__onBattlePassUpdate
        self._addReward(ModeSelectorRewardID.CREDITS)
        self._addReward(ModeSelectorRewardID.EXPERIENCE)
        setBattlePassState(self.viewModel)

    def randomBattlePopoverStatusChangeCallback(self, event):
        self.setPopoverState(event.ctx['active'])

    def setPopoverState(self, active):
        self.viewModel.setIsSettingsActive(active)

    def _onDisposing(self):
        g_eventBus.removeListener(ModeSelectorPopoverEvent.NAME, self.randomBattlePopoverStatusChangeCallback)
        self.__battlePassController.onPointsUpdated -= self.__onBattlePassUpdate
        self.__battlePassController.onSeasonStateChange -= self.__onBattlePassUpdate
        self.__battlePassController.onBattlePassSettingsChange -= self.__onBattlePassUpdate

    def __onBattlePassUpdate(self, *_):
        with self.viewModel.widget.transaction() as vm:
            self.viewModel.setEventName(self.__getBattlePassName())
            self.__fillRandomBattleWidget(vm)

    def __fillRandomBattleWidget(self, model):
        isEnabled = self.__battlePassController.isEnabled() or self.__battlePassController.isPaused()
        model.setIsEnabled(isEnabled)
        if not isEnabled:
            return
        currentLevel = min(self.__battlePassController.getCurrentLevel() + 1, self.__battlePassController.getMaxLevel())
        curPoints, limitPoints = self.__battlePassController.getLevelProgression()
        curChapter = self.__battlePassController.getCurrentChapter()
        notChosen3DStylesCount = getNotChosen3DStylesCount(battlePass=self.__battlePassController)
        notChosenRewardCount = self.__battlePassController.getNotChosenRewardCount() + notChosen3DStylesCount
        is3DStyleChosen = notChosen3DStylesCount == 0
        isOffSeasonEnable = not self.__battlePassController.isSeasonStarted() or self.__battlePassController.isSeasonFinished()
        isPaused = self.__battlePassController.isPaused()
        bpState = self.__battlePassController.getState()
        hasBattlePass = self.__battlePassController.isBought()
        progression = curPoints * 100 / limitPoints if limitPoints else 100
        pointsLeft = limitPoints - curPoints
        if isPaused:
            currentState = ProgressionState.PAUSED
            tooltip = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
        elif isOffSeasonEnable:
            currentState = ProgressionState.AWAIT_SEASON
            tooltip = R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView()
        elif bpState == BattlePassState.COMPLETED:
            currentState = ProgressionState.COMPLETED
            tooltip = R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView()
        else:
            if hasBattlePass:
                currentState = ProgressionState.BOUGHT_BASE
            else:
                currentState = ProgressionState.FREE_BASE
            if not is3DStyleChosen:
                tooltip = R.views.lobby.battle_pass.tooltips.BattlePass3dStyleNotChosenTooltip()
            else:
                tooltip = R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView()
        model.setLevel(currentLevel)
        model.setProgress(progression)
        model.setPoints(pointsLeft)
        model.setHasBattlePass(hasBattlePass)
        model.setIs3DStyleChosen(is3DStyleChosen)
        model.setProgressionState(currentState)
        model.setChapter(curChapter)
        model.setNotChosenRewardCount(notChosenRewardCount)
        model.setTooltipID(tooltip)

    def __getBattlePassName(self):
        seasonNum = self.__battlePassController.getSeasonNum()
        return backport.text(R.strings.mode_selector.event.battlePass.name(), seasonNum=seasonNum) if self.__battlePassController.isActive() or self.__battlePassController.isPaused() else ''

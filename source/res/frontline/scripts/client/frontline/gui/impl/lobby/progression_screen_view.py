# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/progression_screen_view.py
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings
from frontline.frontline_account_settings import getReceivedRewardTokens, setReceivedRewardTokens
from frontline.gui.frontline_bonus_packers import packBonusModelAndTooltipData
from frontline.gui.frontline_helpers import geFrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.progression_screen.progression_screen_model import ProgressionScreenModel
from frontline.gui.impl.gen.view_models.views.lobby.views.progression_screen.tiers_section_model import TiersSectionModel
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showEpicRewardsSelectionWindow, showFrontlineAwards, showHangar
from gui.sounds.epic_sound_constants import EPIC_SOUND
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from sound_gui_manager import CommonSoundSpaceSettings

class ProgressionScreenView(ViewImpl, LobbyHeaderVisibility, IGlobalListener):
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=EPIC_SOUND.HANGAR, entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=None, exitEvent=None)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__tooltipItems', '__rewardsSelectionWindow')

    def __init__(self, layoutID=R.views.frontline.mono.lobby.progression_screen()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ProgressionScreenModel()
        self.__tooltipItems = {}
        self.__rewardsSelectionWindow = None
        self.__hasNewRewards = False
        self.__gameModeStatus, _, _ = geFrontlineState()
        super(ProgressionScreenView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(ProgressionScreenView, self).getViewModel()

    @property
    def __frontlineLevel(self):
        return self.__epicController.getCurrentLevel()

    @property
    def __frontlineProgress(self):
        return self.__epicController.getCurrentProgress()

    @property
    def __levelUpXp(self):
        return self.__epicController.getNextLevelXP()

    @property
    def __isMaxLevel(self):
        return self.__epicController.isMaxLevel()

    @property
    def __newRewardsCount(self):
        return self.__epicController.getNotChosenRewardCount()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressionScreenView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltipItems.get(tooltipId) if tooltipId else None

    def _getEvents(self):
        return [(self.__epicController.onUpdated, self.__onEpicUpdated),
         (self.__epicController.onGameModeStatusTick, self.__onGameModeStatusChange),
         (self.viewModel.onClaimRewards, self.__onClaimRewards),
         (self.viewModel.onClose, self.__onClose)]

    def _onLoading(self, *args, **kwargs):
        super(ProgressionScreenView, self)._onLoading(*args, **kwargs)
        self.__checkHasNewRewards()
        self._fillModel()
        SoundGroups.g_instance.playSound2D(EPIC_SOUND.PROGRESS_PAGE_ENTER)

    def _fillModel(self):
        with self.getViewModel().transaction() as vm:
            self._updateFrontlineState(vm)
            self._fillTiersSection(vm)

    def _updateFrontlineState(self, vm):
        state, _, secondsToState = geFrontlineState()
        vm.setCountdownSeconds(secondsToState)
        vm.setFrontlineState(state.value)
        isNotAnnounce = state != EventBannerState.ANNOUNCE
        vm.setLevel(self.__frontlineLevel if isNotAnnounce else 0)
        vm.setCurrentPoints(self.__frontlineProgress if isNotAnnounce else 0)
        vm.setNeededPoints(self.__levelUpXp if isNotAnnounce else 0)
        vm.setIsMaxLevel(self.__isMaxLevel if isNotAnnounce else False)
        vm.setAmountRewardsToClaim(self.__newRewardsCount)
        vm.setAreRewardsJustEarned(self.__hasNewRewards)

    def _fillTiersSection(self, vm):
        mergedLvlData = self.__epicController.getMergedLevelRewards()
        tiersList = vm.getTiersSections()
        tiersList.clear()
        for startLvl, endLvl, bonuses in mergedLvlData:
            tierModel = TiersSectionModel()
            tierModel.setStart(startLvl)
            tierModel.setEnd(endLvl)
            rewardsList = tierModel.getRewards()
            packBonusModelAndTooltipData(bonuses, rewardsList, self.__tooltipItems)
            tiersList.addViewModel(tierModel)

        tiersList.invalidate()

    def _finalize(self):
        SoundGroups.g_instance.playSound2D(EPIC_SOUND.PROGRESS_PAGE_EXIT)
        super(ProgressionScreenView, self)._finalize()

    def __checkHasNewRewards(self):
        newTokens = self.__epicController.getNotChosenRewardTokens()
        prevReceivedTokens = getReceivedRewardTokens()
        if set(newTokens) - set(prevReceivedTokens):
            self.__hasNewRewards = True
        setReceivedRewardTokens(newTokens)

    def __onClaimRewards(self):
        rewards = []

        def _onAwardsAnimationEnded():
            if self.__rewardsSelectionWindow:
                self.__rewardsSelectionWindow.destroy()

        def _onRewardReceived(rs):
            rewards.extend(rs)
            self._fillModel()
            if rewards:
                showFrontlineAwards(rewards, None, _onAwardsAnimationEnded)
            return

        self.__rewardsSelectionWindow = showEpicRewardsSelectionWindow(level=self.__frontlineLevel, onRewardsReceivedCallback=_onRewardReceived, onCloseCallback=None, isAutoDestroyWindowsOnReceivedRewards=False)
        return

    def __onEpicUpdated(self, diff):
        if 'metaLevel' in diff:
            self._fillModel()

    def __onGameModeStatusChange(self):
        state, _, _ = geFrontlineState()
        if self.__gameModeStatus != state:
            self.__gameModeStatus = state
            with self.viewModel.transaction() as tx:
                self._updateFrontlineState(tx)

    def __onClose(self):
        showHangar()

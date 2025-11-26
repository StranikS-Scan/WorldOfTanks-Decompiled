# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/frontline_event_banner.py
from account_helpers.AccountSettings import AccountSettings, FRONTLINE_BANNER_FIRST_APPEARANCE_TIMESTAMP, FRONTLINE_BANNER_INTRO_CLICK_TIMESTAMP
from frontline.gui.frontline_helpers import isHangarAvailable, geFrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineState
from frontline.gui.impl.lobby.tooltips.banner_tooltip import BannerTooltipView
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.event_dispatcher import showEpicRewardsSelectionWindow
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from frontline.constants.common import STATES_MAP

class FrontlineEventBanner(BaseEventBanner):
    NAME = EPICBATTLES_ALIASES.EPIC_BATTLES_ENTRY_POINT
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(FrontlineEventBanner, self).__init__()
        self._state = ''
        self._eventStartDate = 0
        self._eventEndDate = 0
        self._timerValue = 0
        self._playAppearAnim = False

    @property
    def isMode(self):
        return True

    @property
    def hasRewards(self):
        return self.__epicController.getNotChosenRewardCount()

    @property
    def borderColor(self):
        pass

    @property
    def bannerState(self):
        return self._state

    @property
    def timerValue(self):
        return self._timerValue

    @property
    def eventStartDate(self):
        return self._eventStartDate

    @property
    def eventEndDate(self):
        return self._eventEndDate

    @property
    def playAppearAnim(self):
        return self._playAppearAnim

    def createToolTipContent(self, event):
        return BannerTooltipView()

    def onClick(self):
        from frontline.gui.impl.lobby.states import ProgressionScreenState
        if isHangarAvailable():
            self.__epicController.selectEpicBattle()
        elif self.hasRewards:
            showEpicRewardsSelectionWindow()
        else:
            ProgressionScreenState.goTo()
        if self._state == EventBannerState.INTRO:
            currentSeasonStartDate = self.__epicController.getCurrentSeason().getStartDate()
            AccountSettings.setSettings(FRONTLINE_BANNER_INTRO_CLICK_TIMESTAMP, currentSeasonStartDate)

    def onAppearAnimationPlayed(self):
        currentSeasonStartDate = self.__epicController.getCurrentSeason().getStartDate()
        AccountSettings.setSettings(FRONTLINE_BANNER_FIRST_APPEARANCE_TIMESTAMP, currentSeasonStartDate)

    def prepare(self):
        self._eventStartDate = 0
        self._eventEndDate = 0
        self._timerValue = 0
        frontlineState, _, stateEndTime = geFrontlineState(withPrimeTime=True)
        self._state = STATES_MAP[frontlineState]
        if frontlineState == FrontlineState.ANNOUNCE:
            self._eventStartDate, self._eventEndDate = self.__epicController.getSeasonTimeRange()
        currentSeasonStartDate = self.__epicController.getCurrentSeason().getStartDate()
        if frontlineState == FrontlineState.ACTIVE:
            savedClickTime = AccountSettings.getSettings(FRONTLINE_BANNER_INTRO_CLICK_TIMESTAMP)
            if savedClickTime < currentSeasonStartDate:
                self._state = EventBannerState.INTRO
        if frontlineState in (FrontlineState.FROZEN, FrontlineState.ACTIVE):
            self._timerValue = stateEndTime
        savedAppearTime = AccountSettings.getSettings(FRONTLINE_BANNER_FIRST_APPEARANCE_TIMESTAMP)
        self._playAppearAnim = savedAppearTime < currentSeasonStartDate

    def onAppear(self):
        if self._isVisible:
            return
        super(FrontlineEventBanner, self).onAppear()
        self.__epicController.onUpdated += self.__onUpdate
        self.__epicController.onGameModeStatusTick += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        super(FrontlineEventBanner, self).onDisappear()
        self.__epicController.onUpdated -= self.__onUpdate
        self.__epicController.onGameModeStatusTick -= self.__onUpdate

    def __onUpdate(self, *_):
        if isEpicBattlesEntryPointAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()


@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def isEpicBattlesEntryPointAvailable(epicController=None):
    state, _, _ = geFrontlineState()
    primeTimeStatus, _, _ = epicController.getPrimeTimeStatus()
    hasUnclaimedRewards = epicController.getNotChosenRewardCount()
    return not (not epicController.isEnabled() or not epicController.getCurrentSeasonID() or primeTimeStatus in [PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN] or state == FrontlineState.FINISHED and not hasUnclaimedRewards)

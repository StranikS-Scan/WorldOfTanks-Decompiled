# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/user_missions/hangar_widget/event_banners/comp7_tournament_banner.py
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from comp7.gui.impl.lobby.tooltips.entry_point_tooltip_tournament import Comp7TournamentEntryPointTooltip
from comp7.gui.shared import event_dispatcher as comp7_events
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.ingame_tournament_helper import IngameTournamentState
from helpers.time_utils import ONE_MINUTE, getCurrentLocalServerTimestamp
from skeletons.gui.game_control import IIngameTournamentController

class Comp7TournamentBanner(BaseEventBanner):
    NAME = COMP7_HANGAR_ALIASES.COMP7_TOURNAMENT_ENTRY_POINT
    __tournamentStateBannerStateMap = {IngameTournamentState.INTRO: EventBannerState.INTRO,
     IngameTournamentState.IN_PROGRESS: EventBannerState.IN_PROGRESS,
     IngameTournamentState.BETWEEN_SHOWMATCHES: EventBannerState.INTRO,
     IngameTournamentState.FINISHED: EventBannerState.INTRO}
    __tournamentStateDescriptionMap = {IngameTournamentState.INTRO: R.strings.hangar_event_banners.event.Comp7TournamentEntryPoint.intro.description,
     IngameTournamentState.IN_PROGRESS: R.strings.hangar_event_banners.event.Comp7TournamentEntryPoint.in_live.description,
     IngameTournamentState.FINISHED: R.strings.hangar_event_banners.event.Comp7TournamentEntryPoint.finished.description}
    __tournamentController = dependency.descriptor(IIngameTournamentController)

    def __init__(self):
        super(Comp7TournamentBanner, self).__init__()
        self.__state = None
        self.__stateEndDate = 0
        self.__tournamentStartDate = 0
        self.__tournamentEndDate = 0
        self.__callbackDelayer = None
        return

    @property
    def bannerState(self):
        return self.__tournamentStateBannerStateMap.get(self.__state, EventBannerState.INACTIVE)

    @property
    def borderColor(self):
        return '#FFCF5F' if self.__state == IngameTournamentState.INTRO else ''

    @property
    def timerText(self):
        return str(backport.text(R.strings.hangar_event_banners.event.Comp7TournamentEntryPoint.timer.text())) if self.__state == IngameTournamentState.BETWEEN_SHOWMATCHES else ''

    @property
    def timerValue(self):
        return max(self.__stateEndDate - getCurrentLocalServerTimestamp(), ONE_MINUTE) if self.__state == IngameTournamentState.BETWEEN_SHOWMATCHES else 0

    @property
    def showTimerBeforeEventEnd(self):
        return self.timerValue + 1000 if self.__state == IngameTournamentState.BETWEEN_SHOWMATCHES else -1

    @property
    def eventStartDate(self):
        return self.__tournamentStartDate

    @property
    def eventEndDate(self):
        return self.__tournamentEndDate

    @property
    def introDescription(self):
        descriptionKey = self.__tournamentStateDescriptionMap.get(self.__state)
        return backport.text(descriptionKey()) if descriptionKey else ''

    @property
    def inProgressDescription(self):
        descriptionKey = self.__tournamentStateDescriptionMap.get(self.__state)
        return backport.text(descriptionKey()) if descriptionKey else ''

    @classmethod
    def isTournamentEntryPointAvailable(cls):
        return cls.__tournamentController.isTournamentBannerAvailable()

    def onAppear(self):
        super(Comp7TournamentBanner, self).onAppear()
        self.__tournamentController.onTournamentBannerUpdated += self.__onTournamentBannerUpdated

    def onDisappear(self):
        super(Comp7TournamentBanner, self).onDisappear()
        self.__state = None
        if self.__callbackDelayer is not None:
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
        self.__tournamentController.onTournamentBannerUpdated -= self.__onTournamentBannerUpdated
        return

    def prepare(self):
        super(Comp7TournamentBanner, self).prepare()
        self.__updateBannerData()

    def onClick(self):
        comp7_events.showComp7WCIScreen()

    def createToolTipContent(self, event):
        return Comp7TournamentEntryPointTooltip()

    def __onTournamentBannerUpdated(self):
        self.__updateBannerData()
        EventBannersContainer().onBannerUpdate(self)

    def __updateBannerData(self):
        bannerData = self.__tournamentController.getActiveBannerData()
        if bannerData is not None:
            self.__state = bannerData.state
            self.__stateEndDate = bannerData.endTime
            self.__tournamentStartDate, self.__tournamentEndDate = self.__tournamentController.getTournamentDates()
        else:
            self.__state = None
        if self.__state == IngameTournamentState.BETWEEN_SHOWMATCHES:
            if self.__callbackDelayer is None:
                self.__callbackDelayer = CallbackDelayer()
            self.__callbackDelayer.delayCallback(ONE_MINUTE, self.__updateTimerValue)
        elif self.__callbackDelayer is not None:
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
        return

    def __updateTimerValue(self):
        EventBannersContainer().onBannerUpdate(self)
        if self.__state == IngameTournamentState.BETWEEN_SHOWMATCHES:
            self.__callbackDelayer.delayCallback(ONE_MINUTE, self.__updateTimerValue)

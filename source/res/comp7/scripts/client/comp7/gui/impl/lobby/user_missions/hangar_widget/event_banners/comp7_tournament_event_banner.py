# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/user_missions/hangar_widget/event_banners/comp7_tournament_event_banner.py
from comp7.gui.impl.lobby.tooltips.entry_point_tooltip_tournament import Comp7TournamentEntryPointTooltip
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.prb_control import prbEntityProperty
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.ingame_tournament_helper import IngameTournamentState, IngameTournamentType
from helpers.time_utils import ONE_MINUTE, getCurrentLocalServerTimestamp
from skeletons.gui.game_control import IIngameTournamentController

class Comp7TournamentEventBanner(BaseEventBanner):
    _TOURNAMENT_TYPE = None
    _BORDER_COLOR = '#FFCF5F'
    __tournamentStateBannerStateMap = {IngameTournamentState.INTRO: EventBannerState.INTRO,
     IngameTournamentState.IN_PROGRESS: EventBannerState.IN_PROGRESS,
     IngameTournamentState.BETWEEN_SHOWMATCHES: EventBannerState.INTRO,
     IngameTournamentState.FINISHED: EventBannerState.INTRO}
    __tournamentStateDescriptionMap = {IngameTournamentState.INTRO: R.strings.hangar_event_banners.event.Comp7TournamentEntryPoint.intro.description,
     IngameTournamentState.IN_PROGRESS: R.strings.hangar_event_banners.event.Comp7TournamentEntryPoint.in_live.description,
     IngameTournamentState.FINISHED: R.strings.hangar_event_banners.event.Comp7TournamentEntryPoint.finished.description}
    __tournamentController = dependency.descriptor(IIngameTournamentController)

    def __init__(self):
        super(Comp7TournamentEventBanner, self).__init__()
        self.__state = None
        self.__nextMatchDate = 0
        self.__tournamentStartDate = 0
        self.__tournamentEndDate = 0
        self.__callbackDelayer = None
        return

    @property
    def isMode(self):
        return False

    @property
    def bannerState(self):
        return self.__tournamentStateBannerStateMap.get(self.__state, EventBannerState.INACTIVE)

    @property
    def borderColor(self):
        return self._BORDER_COLOR if self.__state == IngameTournamentState.INTRO else ''

    @property
    def timerText(self):
        return str(backport.text(R.strings.hangar_event_banners.event.Comp7TournamentEntryPoint.timer.text())) if self.__state == IngameTournamentState.BETWEEN_SHOWMATCHES else ''

    @property
    def timerValue(self):
        return max(self.__nextMatchDate - getCurrentLocalServerTimestamp(), ONE_MINUTE) if self.__state == IngameTournamentState.BETWEEN_SHOWMATCHES else 0

    @property
    def showTimerBeforeEventEnd(self):
        return self.timerValue + 1000 if self.__state == IngameTournamentState.BETWEEN_SHOWMATCHES else 0

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

    @prbEntityProperty
    @classmethod
    def prbEntity(cls):
        return None

    @classmethod
    def isTournamentEntryPointAvailable(cls):
        return cls.__tournamentController.isTournamentAvailable(cls._TOURNAMENT_TYPE) and cls.__tournamentController.getTournamentState(cls._TOURNAMENT_TYPE) is not None

    def onAppear(self):
        super(Comp7TournamentEventBanner, self).onAppear()
        self.__tournamentController.onTournamentEntryPointUpdated += self.__onTournamentEntryPointUpdated

    def onDisappear(self):
        super(Comp7TournamentEventBanner, self).onDisappear()
        self.__state = None
        self.__tournamentController.onTournamentEntryPointUpdated -= self.__onTournamentEntryPointUpdated
        if self.__callbackDelayer is not None:
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
        return

    def prepare(self):
        super(Comp7TournamentEventBanner, self).prepare()
        self.__updateEntryPointData()

    def onClick(self):
        raise NotImplementedError

    def createToolTipContent(self, event):
        return Comp7TournamentEntryPointTooltip(self._TOURNAMENT_TYPE)

    def __onTournamentEntryPointUpdated(self):
        self.__updateEntryPointData()
        EventBannersContainer().onBannerUpdate(self)

    def __updateEntryPointData(self):
        entryPointState = self.__tournamentController.getTournamentState(self._TOURNAMENT_TYPE)
        if entryPointState is not None:
            self.__state = entryPointState
            nextMatch = self.__tournamentController.getNextShowmatch(self._TOURNAMENT_TYPE)
            if nextMatch:
                self.__nextMatchDate = nextMatch.startTime
            else:
                self.__nextMatchDate = 0
            tournamentDates = self.__tournamentController.getTournamentShowmatchPeriod(self._TOURNAMENT_TYPE)
            self.__tournamentStartDate, self.__tournamentEndDate = tournamentDates
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

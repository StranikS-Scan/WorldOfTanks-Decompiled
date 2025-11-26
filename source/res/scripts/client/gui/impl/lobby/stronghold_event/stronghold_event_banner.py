# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/stronghold_event/stronghold_event_banner.py
from typing import Tuple
from account_helpers.AccountSettings import StrongholdEvent
from constants import ClansConfig
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getStrongholdEventEnabled, getStrongholdEventUrl
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.clans.clan_cache import g_clanCache
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.stronghold_event.stronghold_event_helpers import getSettings, setSettings
from gui.impl.lobby.stronghold_event.tooltips.stronghold_event_banner_tooltip import StrongholdEventBannerTooltip
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.shared.event_dispatcher import showStrongholds
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from helpers.server_settings import serverSettingsChangeListener
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext

class StrongholdEventBanner(Notifiable, BaseEventBanner):
    NAME = HANGAR_ALIASES.STRONGHOLD_EVENT_BANNER
    __eventsService = dependency.descriptor(IEventsService)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(StrongholdEventBanner, self).__init__()
        self.__eventSettings = None
        self._state = EventBannerState.IN_PROGRESS
        self._timerValue = 0
        self._playAppearAnim = False
        self.addNotificator(SimpleNotifier(self.__getTimeToNextAction, self.__onUpdate))
        return

    @property
    def bannerState(self):
        return self._state

    @property
    def isMode(self):
        return False

    @property
    def borderColor(self):
        pass

    @property
    def introDescription(self):
        res = R.strings.hangar_event_banners.event.StrongholdEventBanner
        return backport.text(res.inProgress.description())

    @property
    def inProgressDescription(self):
        res = R.strings.hangar_event_banners.event.StrongholdEventBanner
        return backport.text(res.inProgress.description())

    @property
    def timerValue(self):
        return self._timerValue

    @property
    def eventStartDate(self):
        return self.__eventSettings.getEventConfig().getStartDate() if self.__eventSettings is not None else 0

    @property
    def eventEndDate(self):
        return self.__eventSettings.getEventConfig().getEndDate() if self.__eventSettings is not None else 0

    @property
    def playAppearAnim(self):
        return self._playAppearAnim

    @property
    def showTimerBeforeEventEnd(self):
        return self._timerValue

    def createToolTipContent(self, event):
        if self.__eventSettings is None:
            return StrongholdEventBannerTooltip(EventBannerState.INACTIVE, 0, 0)
        timeNow = time_utils.getServerUTCTime()
        primeTimeStart, primeTimeEnd, nextPrimeTimeStart = self.__getCurrentPrimeTime()
        eventStartDate = self.__eventSettings.getEventConfig().getStartDate()
        eventEndDate = self.__eventSettings.getEventConfig().getEndDate()
        if timeNow < eventStartDate:
            return StrongholdEventBannerTooltip(EventBannerState.ANNOUNCE, eventStartDate, eventEndDate)
        elif timeNow >= eventEndDate:
            return StrongholdEventBannerTooltip(EventBannerState.INACTIVE, 0, 0)
        elif timeNow < primeTimeStart:
            return StrongholdEventBannerTooltip(EventBannerState.INACTIVE, primeTimeStart, 0)
        elif primeTimeStart < timeNow < primeTimeEnd:
            return StrongholdEventBannerTooltip(EventBannerState.IN_PROGRESS, 0, primeTimeEnd)
        else:
            return StrongholdEventBannerTooltip(EventBannerState.INACTIVE, nextPrimeTimeStart, 0) if primeTimeEnd < timeNow < nextPrimeTimeStart < eventEndDate else StrongholdEventBannerTooltip(EventBannerState.INACTIVE, 0, 0)

    def onClick(self):
        showStrongholds(getStrongholdEventUrl())
        isFirstEnterMade = getSettings(StrongholdEvent.FIRST_BANNER_ENTERING_MADE, False)
        if self._state == EventBannerState.INTRO and isFirstEnterMade is not None and not isFirstEnterMade:
            setSettings(StrongholdEvent.FIRST_BANNER_ENTERING_MADE, True)
        return

    def prepare(self):
        self.__eventSettings = g_clanCache.strongholdEventProvider.getSettings()
        self._playAppearAnim = False
        isFirstAppearance = getSettings(StrongholdEvent.IS_BANNER_FIRST_APPEARANCE_SEEN, False)
        if isFirstAppearance is not None and not isFirstAppearance:
            self._playAppearAnim = True
        self._state, _ = self.__getState()
        self.startNotification()
        return

    def onAppear(self):
        if self._isVisible:
            return
        super(StrongholdEventBanner, self).onAppear()
        if self._playAppearAnim:
            setSettings(StrongholdEvent.IS_BANNER_FIRST_APPEARANCE_SEEN, True)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_clanCache.strongholdEventProvider.onDataReceived += self.__onUpdate
        g_clanCache.strongholdEventProvider.onDataFailed += self.__onDataFailed

    def onDisappear(self):
        if not self._isVisible:
            return
        super(StrongholdEventBanner, self).onDisappear()
        self.stopNotification()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_clanCache.strongholdEventProvider.onDataReceived -= self.__onUpdate
        g_clanCache.strongholdEventProvider.onDataFailed -= self.__onDataFailed

    def __getState(self):
        if self.__eventSettings is None:
            return (EventBannerState.INACTIVE, -1)
        elif not getStrongholdEventEnabled():
            return (EventBannerState.INACTIVE, -1)
        timeNow = time_utils.getServerUTCTime()
        eventConfig = self.__eventSettings.getEventConfig()
        eventStartTime = eventConfig.getStartDate()
        eventEndTime = eventConfig.getEndDate()
        primeTimeStart, primeTimeEnd, nextPrimeTimeStart = self.__getCurrentPrimeTime()
        if timeNow < eventStartTime:
            return (EventBannerState.ANNOUNCE, eventStartTime - timeNow)
        elif timeNow >= eventEndTime:
            return (EventBannerState.FINISHED, -1)
        elif timeNow < primeTimeStart:
            self._timerValue = primeTimeStart - timeNow
            return (EventBannerState.INACTIVE, primeTimeStart - timeNow)
        elif primeTimeStart <= timeNow <= primeTimeEnd:
            self._timerValue = 0
            isFirstEnterMade = getSettings(StrongholdEvent.FIRST_BANNER_ENTERING_MADE, False)
            if isFirstEnterMade is not None and not isFirstEnterMade:
                state = EventBannerState.INTRO
            else:
                state = EventBannerState.IN_PROGRESS
            return (state, primeTimeEnd - timeNow)
        elif primeTimeEnd < timeNow < nextPrimeTimeStart < eventEndTime:
            self._timerValue = nextPrimeTimeStart - timeNow
            return (EventBannerState.INACTIVE, nextPrimeTimeStart - timeNow)
        else:
            return (EventBannerState.FINISHED, eventEndTime - timeNow)

    def __onUpdate(self, *_):
        self.__eventSettings = g_clanCache.strongholdEventProvider.getSettings()
        if getStrongholdEventEnabled():
            EventBannersContainer().onBannerUpdate(self)

    @serverSettingsChangeListener(ClansConfig.SECTION_NAME)
    def __onServerSettingsChanged(self, _):
        self.__eventsService.updateEntries()

    def __onDataFailed(self, _):
        self.__eventsService.updateEntries()

    def __isEventActive(self):
        if self.__eventSettings is None:
            return False
        else:
            timeNow = time_utils.getServerUTCTime()
            eventConfig = self.__eventSettings.getEventConfig()
            return eventConfig.getStartDate() < timeNow < eventConfig.getEndDate()

    def __getCurrentPrimeTime(self):
        primeTimes = self.__eventSettings.getEventConfig().primetimes
        if not primeTimes:
            return (-1, -1, -1)
        firstPrimeStartTime = min((primeTime['start_time'] for primeTime in primeTimes))
        lastPrimeEndTime = max((primeTime['end_time'] for primeTime in primeTimes))
        nextPrimeStartDate = firstPrimeStartTime + time_utils.ONE_DAY
        return (firstPrimeStartTime, lastPrimeEndTime, nextPrimeStartDate)

    def __getTimeToNextAction(self):
        _, timeUntilUpdate = self.__getState()
        return max(timeUntilUpdate, 0)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/game_control/grinch_controller.py
import logging
import typing
import Event
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CURRENT_VEHICLE
from adisp import adisp_process
from frameworks.wulf import WindowLayer
from grinch.account_helpers.account_settings import isStartChapterNotifationShown, isEndedChapterNotifationShown, isFinishedNotifationShown, setStartChapterNotificationShown, setEndedChapterNotificationShown, setFinishedNotificationShown
from grinch.gui.grinch_gui_constants import PREBATTLE_ACTION_NAME, SCH_CLIENT_MSG_TYPE, FUNCTIONAL_FLAG
from grinch.gui.prebattle_hints.random_prb_hints import PrbRandomHintManager
from grinch.helpers.server_settings import GrinchConfig
from grinch.overrides.hangar_override import showHangar
from grinch.skeletons.battle_controller import IGrinchController
from grinch_common.grinch_constants import EventStates, PREBATTLE_TYPE, QUEUE_TYPE, Configs
from gui.game_control.season_provider import SeasonProvider
from gui.shared.event_dispatcher import showHangar as showDefaultHangar
from gui.periodic_battles.models import PeriodType
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from shared_utils import makeTupleByDict
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.system_messages import ISystemMessages
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Dict, Optional

class GrinchController(IGrinchController, Notifiable, SeasonProvider, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(GrinchController, self).__init__()
        self.__serverSettings = None
        self.__prbHintManager = None
        self.__isPrimeTime = False
        self.__isAvailable = False
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onSeasonStatusUpdated = Event.Event()
        self.onConfigChanged = Event.Event()
        return

    def init(self):
        super(GrinchController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.addNotificator(SimpleNotifier(self.__getNotificationTimer, self.__showNotification))
        g_playerEvents.onPrbDispatcherCreated += self.__onPrbDispatcherCreated

    def onLobbyInited(self, _):
        self.__showNotification()

    def fini(self):
        self.onPrimeTimeStatusUpdated.clear()
        self.onSeasonStatusUpdated.clear()
        self.onConfigChanged.clear()
        self.clearNotification()
        self.__clear()
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        super(GrinchController, self).fini()

    def onAccountBecomePlayer(self):
        super(GrinchController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onAccountBecomeNonPlayer(self):
        self.__clear()
        super(GrinchController, self).onAccountBecomeNonPlayer()

    def onPrbEntitySwitched(self):
        super(GrinchController, self).onPrbEntitySwitched()
        if not self.isEventPrbActive():
            vehID = AccountSettings.getFavorites(CURRENT_VEHICLE)
            g_currentVehicle.selectVehicle(vehID or 0)
        if self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.STRONGHOLD:
            showDefaultHangar()

    def isBattlesPossible(self):
        return self.isEnabled() and self.getCurrentSeason() is not None

    def isEnabled(self):
        return self.getConfig()['isEnabled']

    def isAvailable(self):
        return not self.isFrozen() and self.getCurrentSeason() is not None

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def isEventPrbActive(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInUnit(PREBATTLE_TYPE.GRINCH) or state.isInPreQueue(QUEUE_TYPE.GRINCH)
        else:
            return False

    @property
    def prbHintManager(self):
        if self.__prbHintManager is None:
            self.__prbHintManager = PrbRandomHintManager()
        return self.__prbHintManager

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings().get(Configs.GRINCH_CONFIG.value)

    def getModeSettings(self):
        return makeTupleByDict(GrinchConfig, self.getConfig()) if self.getConfig() else GrinchConfig.defaults()

    def getSquadConfig(self):
        return self.getModeSettings().squadConfig

    @adisp_process
    def selectMode(self, useFade=False):
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            return
        elif self.isFrozen():
            self.__systemMessages.proto.serviceChannel.pushClientMessage({'state': EventStates.SUSPEND}, SCH_CLIENT_MSG_TYPE.GRINCH_EVENT_STATE)
            return
        else:
            result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.GRINCH), fadeCtx={'layer': WindowLayer.OVERLAY} if useFade else None)
            if not result:
                return
            showHangar()
            return

    @adisp_process
    def selectRandomMode(self, useFade=True):
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            return
        else:
            result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM), fadeCtx={'layer': WindowLayer.OVERLAY} if useFade else None)
            return None if not result else None

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateEventBattlesSettings
        self.__isAvailable = self.isAvailable()
        self.__resetTimer()
        return

    def __updateEventBattlesSettings(self, diff):
        if Configs.GRINCH_CONFIG.value in diff:
            self.__resetTimer()
            self.__checkForAvailabilityUpdate()
            self.onConfigChanged(diff)

    def __clear(self):
        self.stopGlobalListening()
        self.stopNotification()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = None
        return

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __getNotificationTimer(self):
        timeLeft = self.getClosestStateChangeTime() - time_utils.getCurrentLocalServerTimestamp()
        return timeLeft + 1 if timeLeft > 0 else 0

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__showNotification()

    def __timerUpdate(self):
        status, _, isPrimeTime = self.getPrimeTimeStatus()
        if isPrimeTime is not self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
        self.onPrimeTimeStatusUpdated(status)

    def __showNotification(self):
        periodInfo = self.getPeriodInfo()
        if periodInfo.periodType == PeriodType.AVAILABLE:
            chapNum = int(periodInfo.seasonBorderLeft.userName)
            if not isStartChapterNotifationShown(chapNum):
                self.__dispatchEventStateNotification(EventStates.BATTLES_CHAPTER_BEGIN, periodInfo)
                setStartChapterNotificationShown(chapNum)
        if periodInfo.periodType == PeriodType.BETWEEN_SEASONS:
            chapNum = int(periodInfo.seasonBorderLeft.userName)
            if not isEndedChapterNotifationShown(chapNum):
                self.__dispatchEventStateNotification(EventStates.BATTLES_CHAPTER_FINISH, periodInfo)
                setEndedChapterNotificationShown(chapNum)
        if periodInfo.periodType == PeriodType.AFTER_SEASON and not isFinishedNotifationShown():
            self.__dispatchEventStateNotification(EventStates.BATTLES_FINISH, periodInfo)
            setFinishedNotificationShown()
        self.onSeasonStatusUpdated(periodInfo.periodType)

    def __dispatchEventStateNotification(self, eventType, periodInfo):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'state': eventType,
         'periodInfo': periodInfo}, SCH_CLIENT_MSG_TYPE.GRINCH_EVENT_STATE)

    def __checkForAvailabilityUpdate(self):
        isAvailable = self.isAvailable()
        if self.__isAvailable != isAvailable:
            eventType = EventStates.RESUME if isAvailable else EventStates.SUSPEND
            self.__systemMessages.proto.serviceChannel.pushClientMessage({'state': eventType}, SCH_CLIENT_MSG_TYPE.GRINCH_EVENT_STATE)
            self.__isAvailable = isAvailable

    def __onPrbDispatcherCreated(self):
        self.startGlobalListening()

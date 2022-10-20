# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_battles_controller.py
import typing
import Event
import adisp
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process
from constants import QUEUE_TYPE, BigWorld, PREBATTLE_TYPE
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.listener import IPrbListener
from gui.prb_control.entities.event.pre_queue.entity import EventBattleEntity
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin
from gui.shared.utils import SelectorBattleTypesUtils
from helpers import dependency, time_utils
from shared_utils import nextTick
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from season_provider import SeasonProvider
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.prb_control.dispatcher import g_prbLoader
if typing.TYPE_CHECKING:
    from helpers.server_settings import _EventBattlesConfig

class EventBattlesController(IEventBattlesController, Notifiable, SeasonProvider, IPrbListener, PerformanceAnalyzerMixin):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(EventBattlesController, self).__init__()
        self.__serverSettings = None
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onEventDisabled = Event.Event()
        self.onCompleteActivePhase = Event.Event()
        return

    def init(self):
        super(EventBattlesController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))

    def fini(self):
        self.onPrimeTimeStatusUpdated.clear()
        self.onEventDisabled.clear()
        self.onCompleteActivePhase.clear()
        self.clearNotification()
        self.__clear()
        super(EventBattlesController, self).fini()

    def onDisconnected(self):
        super(EventBattlesController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(EventBattlesController, self).onAvatarBecomePlayer()
        self.__clear()

    def onAccountBecomePlayer(self):
        super(EventBattlesController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onLobbyInited(self, event):
        nextTick(self.__eventAvailabilityUpdate)()

    def isEnabled(self):
        return self.getConfig().isEnabled

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def isEventShutDown(self):
        progressCtrl = self.getHWProgressCtrl()
        return True if progressCtrl is None else not self.isEnabled() and not progressCtrl.isPostPhase()

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().eventBattlesConfig

    @adisp.adisp_process
    def selectEventBattle(self):
        prebattleType = PREBATTLE_ACTION_NAME.EVENT_BATTLE
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            return
        else:
            isSuccess = yield dispatcher.doSelectAction(PrbAction(prebattleType))
            if isSuccess:
                self.updateAccountSettings()
            return

    def updateAccountSettings(self):
        prebattleType = PREBATTLE_ACTION_NAME.EVENT_BATTLE
        if not SelectorBattleTypesUtils.isKnownBattleType(prebattleType):
            SelectorBattleTypesUtils.setBattleTypeAsKnown(prebattleType)
        phase = self.getHWProgressCtrl().phasesHalloween
        activePhaseIndex = phase.getActivePhaseIndex()
        savedPhase = phase.getPrevPhase()
        if savedPhase != activePhaseIndex:
            phase.setPrevPhase(activePhaseIndex)

    def getModeSettings(self):
        return self.getConfig()

    def isEventPrbActive(self):
        return self.prbEntity and self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.EVENT

    def getCurrentQueueType(self):
        vehicle = g_currentVehicle.item
        return QUEUE_TYPE.EVENT_BATTLES_2 if vehicle and vehicle.isWheeledTech else QUEUE_TYPE.EVENT_BATTLES

    def getHWProgressCtrl(self):
        component = getattr(BigWorld.player(), 'HWAccountComponent', None)
        return None if not component else component.getHWProgressCtrl()

    def isEventHangar(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        state = prbDispatcher.getFunctionalState() if prbDispatcher is not None else None
        return state is not None and (state.isInPreQueue(QUEUE_TYPE.EVENT_BATTLES) or state.isInUnit(PREBATTLE_TYPE.EVENT) or state.isInPreQueue(QUEUE_TYPE.EVENT_BATTLES_2))

    def isCurrentQueueEnabled(self):
        return self.isQueueEnabled(self.getCurrentQueueType())

    def isQueueEnabled(self, queueType):
        queueSettings = self.getConfig().queueSettings
        return queueType not in queueSettings or queueSettings[queueType]['isEnabled']

    @adisp_process
    def doLeaveEventPrb(self):
        if self.isEventPrbActive():
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateEventBattlesSettings
        self.__resetTimer()
        return

    def __updateEventBattlesSettings(self, diff):
        if 'event_battles_config' in diff:
            if self.isEventHangar() and not self.isEnabled():
                self.onEventDisabled()
                if self.isEventShutDown():
                    EventBattleEntity.pushMessageEventTermination()
                return
            self.__resetTimer()

    def __clear(self):
        self.stopNotification()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = None
        return

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)

    def __eventAvailabilityUpdate(self):
        if self.prbEntity is None:
            return
        elif not self.isEventPrbActive():
            return
        else:
            progressCtrl = self.getHWProgressCtrl()
            if not self.isAvailable() or not progressCtrl or progressCtrl.isPostPhase():
                self.doLeaveEventPrb()
            return

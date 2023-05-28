# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/respawn_message_panel.py
import logging
import weakref
import BigWorld
import BattleReplay
from ReplayEvents import g_replayEvents
from VehicleBRRespawnEffectComponent import VehicleBRRespawnEffectComponent
from battle_royale.gui.Scaleform.daapi.view.battle.respawn_messages_formatters import formatRespawnActivatedMessage, formatRespawnFinishedMessage, formatRespawnNotAvailableMessage, formatAllyInBattleMessage, formatStayInCoverMessage, formatPickUpSphereMessage, formatAllyRespawnedMessage, formatRespawnNotAvailableSoonMessage, formatRespawnActivatedSquadMessage
from battle_royale.gui.Scaleform.daapi.view.common.respawn_ability import RespawnAbility
from battle_royale.gui.battle_control.controllers.notification_manager import INotificationManagerListener, NotificationType
from battle_royale.gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from constants import ARENA_BONUS_TYPE, ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.BRRespawnMessagePanelMeta import BRRespawnMessagePanelMeta
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController, IArenaPeriodController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.avatar_getter import isVehicleAlive
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from items.battle_royale import isSpawnedBot
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
RESPAWNING_TIMER_DELAY = 1

class RespawnMessagePanel(BRRespawnMessagePanelMeta, ISpawnListener, IArenaPeriodController, IArenaVehiclesController, INotificationManagerListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    TIME_TO_SHOW = 5
    RESPAWN_DELAY_BEFORE_SHOW = 1
    RESPAWN_COMPLETED_DELAY_BEFORE_SHOW = 2

    def __init__(self):
        super(RespawnMessagePanel, self).__init__()
        self.__vehicleIDs = []
        self.__lives = -1
        self.notificationManager = None
        self.__respawnTimestampSent = False
        self.__timeoutCallbackID = None
        self.__msgCallbackID = None
        self.__delayCallbackID = None
        self.__delayTime = 0
        self.__endTime = 0
        self._message = None
        return

    def _populate(self):
        super(RespawnMessagePanel, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        if self.sessionProvider.arenaVisitor.bonus.isSquadSupported():
            self.__initSquadPlayers()
            VehicleBRRespawnEffectComponent.onRespawned += self.__onVehicleRespawned
        deathScreenCtrl = self.sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onShowDeathScreen += self.__onShowDeathScreen
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
        return

    def __setMsgCallback(self):
        self.__msgCallbackID = None
        length = self.__tick()
        if length > 0:
            self.__msgCallbackID = BigWorld.callback(length if length < 1 else 1, self.__setMsgCallback)
        else:
            self.__delayTime = 0
            self.__endTime = 0
            self._message = None
            self.as_hideMessageS()
        return

    def _calculate(self):
        return max(0, self.__endTime - BigWorld.serverTime())

    def __clearMsgCallback(self):
        if self.__msgCallbackID is not None:
            BigWorld.cancelCallback(self.__msgCallbackID)
            self.__msgCallbackID = None
        if self.__delayCallbackID is not None:
            BigWorld.cancelCallback(self.__delayCallbackID)
            self.__delayCallbackID = None
        return

    def __tick(self):
        floatLength = self._calculate()
        if not floatLength:
            return 0
        intLength = max(int(floatLength), 0)
        self.as_setMessageTimeS(intLength)
        return floatLength

    def addNotificationManager(self, notificationManager):
        self.notificationManager = weakref.ref(notificationManager)
        self.notificationManager().addRespawnPanelHandler(self.sendMessage)

    def _dispose(self):
        self.notificationManager = None
        if self.__timeoutCallbackID:
            BigWorld.cancelCallback(self.__timeoutCallbackID)
            self.__timeoutCallbackID = None
        self.__clearMsgCallback()
        self.sessionProvider.removeArenaCtrl(self)
        if self.sessionProvider.arenaVisitor.bonus.isSquadSupported():
            VehicleBRRespawnEffectComponent.onRespawned -= self.__onVehicleRespawned
        deathScreenCtrl = self.sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onShowDeathScreen -= self.__onShowDeathScreen
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
        super(RespawnMessagePanel, self)._dispose()
        return

    def getCtrlScope(self):
        return _SCOPE.PERIOD | _SCOPE.VEHICLES

    def __onRespawnBaseMoving(self, *_):
        message = formatRespawnFinishedMessage(self.TIME_TO_SHOW, self.RESPAWN_COMPLETED_DELAY_BEFORE_SHOW)
        self.__addMessage(NotificationType.respFinishedMsg, message)

    def __initSquadPlayers(self):
        self.__vehicleIDs = []
        arenaDP = self.sessionProvider.getArenaDP()
        collection = vos_collections.AllyItemsCollection().ids(arenaDP)
        for vId in collection:
            vInfoVO = arenaDP.getVehicleInfo(vId)
            playerVehId = BigWorld.player().observedVehicleID or arenaDP.getPlayerVehicleID()
            if not vInfoVO.isObserver() and playerVehId != vId and not isSpawnedBot(vInfoVO.vehicleType.tags):
                self.__vehicleIDs.append(vId)

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if periodCtrl is not None and periodCtrl.getPeriod() < ARENA_PERIOD.BATTLE:
            return
        else:
            if vInfoVO.vehicleID in self.__vehicleIDs:
                _logger.debug('invalidateVehicleStatus %s, %s', vInfoVO.vehicleID, vInfoVO.isAlive())
                if isVehicleAlive() and not vInfoVO.isAlive() and self.__lives == 0:
                    _logger.debug('formatPickUpSphereMessage')
                    message = formatPickUpSphereMessage(self.TIME_TO_SHOW, self.RESPAWN_DELAY_BEFORE_SHOW)
                    self.__addMessage(NotificationType.pickUpSphereMsg, message)
            return

    def _destroy(self):
        super(RespawnMessagePanel, self)._destroy()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        return

    def updateRespawnTime(self, timeLeft):
        if timeLeft > 0:
            bonusType = self.sessionProvider.arenaVisitor.getArenaBonusType()
            isSquadMode = bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE
            if isSquadMode and isVehicleAlive():
                _logger.debug('formatStayInCoverMessage %s', timeLeft)
                message = formatStayInCoverMessage(timeLeft, RESPAWNING_TIMER_DELAY)
                idx = NotificationType.stayInCoverMsg
            else:
                if isSquadMode:
                    _logger.debug('formatRespawnActivatedSquadMessage %s', timeLeft)
                    message = formatRespawnActivatedSquadMessage(timeLeft, self.RESPAWN_DELAY_BEFORE_SHOW)
                else:
                    _logger.debug('formatRespawnActivatedMessage %s', timeLeft)
                    message = formatRespawnActivatedMessage(timeLeft, self.RESPAWN_DELAY_BEFORE_SHOW)
                idx = NotificationType.respActivatedMsg
            self.__addMessage(idx, message)

    def updateBlockToRessurecTime(self, blockTime):
        if blockTime > 0:
            _logger.debug('formatAllyInBattleMessage %s', blockTime)
            message = formatAllyInBattleMessage(blockTime, self.RESPAWN_DELAY_BEFORE_SHOW)
            self.__addMessage(NotificationType.allyInBattleMsg, message)

    def updateLives(self, livesLeft, prev):
        self.__lives = livesLeft if livesLeft is not None else 0
        if livesLeft is None or prev is None:
            return
        else:
            if livesLeft < 0:
                _logger.debug('formatRespawnNotAvailableMessage')
                message = formatRespawnNotAvailableMessage(self.TIME_TO_SHOW)
                self.__addMessage(NotificationType.respNotAvailableMsg, message)
            return

    def __onVehicleRespawned(self, vehicleID):
        if vehicleID in self.__vehicleIDs:
            _logger.debug('formatAllyRespawnedMessage')
            message = formatAllyRespawnedMessage(self.TIME_TO_SHOW, self.RESPAWN_DELAY_BEFORE_SHOW)
            self.__addMessage(NotificationType.allyRespawnedMessage, message)

    @staticmethod
    def __getTimeGoneFromStart(endTime, length):
        startTime = endTime - length
        return BigWorld.serverTime() - startTime

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        timesGoneFromStart = self.__getTimeGoneFromStart(endTime, length)
        self.__onPeriodChange(period, timesGoneFromStart)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        timesGoneFromStart = self.__getTimeGoneFromStart(endTime, length)
        self.__onPeriodChange(period, timesGoneFromStart)

    def __onPeriodChange(self, period, timesGoneFromStart):
        if period == ARENA_PERIOD.BATTLE and not self.__respawnTimestampSent:
            bonusType = self.sessionProvider.arenaVisitor.getArenaBonusType()
            isSquadMode = bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE
            respawnPeriod = RespawnAbility().soloRespawnPeriod if not isSquadMode else RespawnAbility().platoonRespawnPeriod
            secondsLeft = max(respawnPeriod - timesGoneFromStart, 0)
            self.__respawnTimestampSent = True
            timeToNotification = max(secondsLeft - ONE_MINUTE, 0)
            if timeToNotification:
                self.__timeoutCallbackID = BigWorld.callback(timeToNotification, self.__showNotAvailableSoonNotification)

    def __showNotAvailableSoonNotification(self):
        self.__timeoutCallbackID = None
        message = formatRespawnNotAvailableSoonMessage(self.TIME_TO_SHOW)
        self.__addMessage(NotificationType.respNotAvailableSoonMsg, message)
        return

    def __addMessage(self, idx, message):
        if self.notificationManager:
            if idx in (NotificationType.respActivatedMsg, NotificationType.allyInBattleMsg, NotificationType.stayInCoverMsg):
                message['showBefore'] = BigWorld.serverTime() + message['time'] + message['delay']
            else:
                message['showBefore'] = BigWorld.serverTime() + ONE_MINUTE
            self.notificationManager().addRespawnMessage(idx, message)

    def sendMessage(self, message, sendAgain=True):
        if not message:
            self.__clearMsgCallback()
            if not self.__delayTime and self._message:
                self.as_hideMessageS()
            self.__delayTime = 0
            self.__endTime = 0
            self._message = None
            return
        else:
            self.__endTime = message['time'] + message['delay'] + BigWorld.serverTime()
            if not sendAgain:
                return
            self.__delayTime = message['delay']
            message['delay'] = 0
            self._message = message
            if self.__delayTime:
                self.__startDelayTimer()
            else:
                self.__onDelayFinished()
            return

    def __onDelayFinished(self):
        self.__delayCallbackID = None
        self.__delayTime = 0
        if not self._message:
            self.__clearMsgCallback()
            return
        else:
            self._message['time'] = int(self._calculate())
            self.as_addMessageS(self._message)
            self.__clearMsgCallback()
            self.__setMsgCallback()
            return

    def __startDelayTimer(self):
        self.__delayCallbackID = BigWorld.callback(self.__delayTime, self.__onDelayFinished)

    def __onShowDeathScreen(self):
        self.notificationManager().clearQueue()

    def __onReplayTimeWarpStart(self):
        self.notificationManager().clearQueue()

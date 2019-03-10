# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/respawn_ctrl.py
from collections import namedtuple
import BigWorld
import Event
from constants import RESPAWN_TYPES
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from items import vehicles
from gui.battle_control.view_components import ViewComponentsController
from PlayerEvents import g_playerEvents
_Vehicle = namedtuple('_Vehicle', ('intCD', 'type', 'settings'))
_RespawnInfo = namedtuple('_RespawnInfo', ('vehicleID', 'respawnTime', 'respawnType', 'autoRespawnTime'))

class IRespawnView(object):

    def start(self, vehsList, isLimited):
        raise NotImplementedError

    def show(self, selectedID, vehsList, cooldowns, limits=0):
        raise NotImplementedError

    def hide(self):
        raise NotImplementedError

    def setSelectedVehicle(self, vehicleID, vehsList, cooldowns, limits=0):
        raise NotImplementedError

    def updateTimer(self, timeLeft, vehsList, cooldowns, limits=0):
        raise NotImplementedError

    def setLimits(self, respawnLimits):
        pass

    def setBattleCtx(self, battleCtx):
        pass


_RESPAWN_SOUND_ID = 'start_battle'

class RespawnsController(ViewComponentsController):
    __slots__ = ('__weakref__', '__isUIInited', '__vehicles', '__cooldowns', '__respawnInfo', '__timerCallback', '__eManager', 'onRespawnVisibilityChanged', 'onVehicleDeployed', 'onRespawnInfoUpdated', 'onPlayerRespawnLivesUpdated', 'onTeamRespawnLivesRestored', 'onRespawnVehiclesUpdated', '__isUiShown', '__isShowUiAllowed', '__limits', '__playerRespawnLives', '__respawnSoundNotificationRequest', '__battleCtx')
    showUiAllowed = property(lambda self: self.__isShowUiAllowed, lambda self, value: self.__setShowUiAllowed(value))
    respawnInfo = property(lambda self: self.__respawnInfo)
    playerLives = property(lambda self: self.__playerRespawnLives)
    vehicles = property(lambda self: self.__vehicles)

    def __init__(self, setup):
        super(RespawnsController, self).__init__()
        self.__isUIInited = False
        self.__vehicles = []
        self.__cooldowns = {}
        self.__limits = {}
        self.__respawnInfo = None
        self.__timerCallback = None
        self.__isUiShown = False
        self.__isShowUiAllowed = False
        self.__playerRespawnLives = -1
        self.__respawnSoundNotificationRequest = False
        self.__battleCtx = setup.battleCtx
        self.__eManager = Event.EventManager()
        self.onRespawnVisibilityChanged = Event.Event(self.__eManager)
        self.onVehicleDeployed = Event.Event(self.__eManager)
        self.onRespawnInfoUpdated = Event.Event(self.__eManager)
        self.onPlayerRespawnLivesUpdated = Event.Event(self.__eManager)
        self.onTeamRespawnLivesRestored = Event.Event(self.__eManager)
        self.onRespawnVehiclesUpdated = Event.Event(self.__eManager)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.RESPAWN

    def startControl(self):
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def stopControl(self):
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        self.__stopTimer()
        self.clearViewComponents()
        self.__vehicles = None
        self.__cooldowns = None
        self.__respawnInfo = None
        self.__limits = None
        self.__battleCtx = None
        return

    def setViewComponents(self, *components):
        super(RespawnsController, self).setViewComponents(*components)
        if not self._viewComponents:
            return
        self.__refresh()
        for viewCmp in self._viewComponents:
            viewCmp.setBattleCtx(self.__battleCtx)

    def respawnPlayer(self):
        BigWorld.player().base.respawnController_performRespawn()

    def chooseVehicleForRespawn(self, vehicleID):
        BigWorld.player().base.respawnController_chooseVehicleForRespawn(vehicleID)

    def movingToRespawn(self):
        self.__respawnInfo = None
        self.__stopTimer()
        self.__respawnSoundNotificationRequest = True
        return

    def spawnVehicle(self, _):
        if BigWorld.player().isVehicleAlive:
            self.__respawnInfo = None
            self.onVehicleDeployed()
        if self.__respawnSoundNotificationRequest:
            BigWorld.callback(1.0, self.__triggerRespawnSoundNotification)
            self.__respawnSoundNotificationRequest = False
        self.__hide()
        return

    def updateRespawnVehicles(self, vehsList):
        self.__vehicles = []
        for v in vehsList:
            descr = vehicles.getVehicleType(v['compDescr'])
            self.__vehicles.append(_Vehicle(descr.compactDescr, descr, v['settings']))

        self.onRespawnVehiclesUpdated(self.__vehicles)

    def updateRespawnCooldowns(self, cooldowns):
        self.__cooldowns = cooldowns

    def updateRespawnInfo(self, respawnInfo):
        intCD = vehicles.getVehicleTypeCompactDescr(respawnInfo['compDescr'])
        self.__respawnInfo = _RespawnInfo(intCD, respawnInfo['manualRespawnPiT'], respawnInfo['respawnType'], respawnInfo['autoRespawnPiT'])
        self.__refresh()
        self.onRespawnInfoUpdated(self.__respawnInfo)

    def updateVehicleLimits(self, respawnLimits):
        self.__limits = respawnLimits
        if not self._viewComponents:
            return
        for viewCmp in self._viewComponents:
            viewCmp.setLimits(respawnLimits)

    def updatePlayerRespawnLives(self, respawnLives):
        self.__playerRespawnLives = respawnLives
        self.onPlayerRespawnLivesUpdated(respawnLives)

    def restoredTeamRespawnLives(self, teams):
        self.onTeamRespawnLivesRestored(teams)

    def isRespawnVisible(self):
        return self.__isUiShown

    def getLimits(self):
        return self.__limits

    def _show(self):
        if not self._viewComponents:
            return
        if not self.__isUIInited:
            self.__isUIInited = True
            isLimited = self.__respawnInfo.respawnType == RESPAWN_TYPES.LIMITED
            for viewCmp in self._viewComponents:
                viewCmp.start(self.__vehicles, isLimited)

        for viewCmp in self._viewComponents:
            viewCmp.show(self.__respawnInfo.vehicleID, self.__vehicles, self.__cooldowns, self.__limits)

        self.__isUiShown = True
        self.__startTimer()
        self.onRespawnVisibilityChanged(True)
        self.__startTimer()
        self.__isUiShown = True

    def __setShowUiAllowed(self, value):
        self.__isShowUiAllowed = value
        self.__refresh()

    def __triggerRespawnSoundNotification(self):
        getSoundNotifications().play(_RESPAWN_SOUND_ID)

    def __onRoundFinished(self, *args):
        self.__hide()

    def __refresh(self):
        if self.__respawnInfo is None or self._viewComponents is None:
            return
        else:
            if self.__respawnInfo is not None and not self.__isUiShown and self.__isShowUiAllowed:
                self._show()
            elif self.__isUiShown and not self.__isShowUiAllowed:
                self.__hide()
            elif self.__isUiShown:
                self.__stopTimer()
                self.__startTimer()
            return

    def __hide(self):
        if not self.__isUiShown:
            return
        self.__stopTimer()
        if not self._viewComponents:
            return
        for viewCmp in self._viewComponents:
            viewCmp.hide()
            self.__isUiShown = False
            self.onRespawnVisibilityChanged(False)

    def __startTimer(self):
        self.__timerCallback = None
        if self.__respawnInfo is None:
            return
        else:
            respawnTime = self.__respawnInfo.respawnTime
            timeLeft = max(0, respawnTime - BigWorld.serverTime())
            autoRespawnTime = self.__respawnInfo.autoRespawnTime
            autoTimeLeft = max(0, autoRespawnTime - BigWorld.serverTime())
            for viewCmp in self._viewComponents:
                viewCmp.updateTimer([timeLeft, autoTimeLeft], self.__vehicles, self.__cooldowns, self.__limits)

            if timeLeft > 0 or autoTimeLeft > 0:
                self.__timerCallback = BigWorld.callback(1, self.__startTimer)
            return

    def __stopTimer(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

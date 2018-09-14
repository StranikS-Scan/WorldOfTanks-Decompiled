# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/respawn_ctrl.py
import weakref
import BigWorld
import Event
from collections import namedtuple
from constants import RESPAWN_TYPES
from GasAttackSettings import GasAttackState
from gui.battle_control.arena_info.interfaces import IArenaRespawnController
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
from items import vehicles
_SHOW_UI_COOLDOWN = 3.0
_Vehicle = namedtuple('_Vehicle', ('intCD', 'type', 'vehAmmo'))
_RespawnInfo = namedtuple('_RespawnInfo', ('vehicleID', 'respawnTime', 'respawnType'))

class IRespawnView(object):

    def start(self, vehsList, isLimited):
        raise NotImplementedError

    def show(self, selectedID, vehsList, cooldowns):
        raise NotImplementedError

    def hide(self):
        raise NotImplementedError

    def setSelectedVehicle(self, vehicleID, vehsList, cooldowns):
        raise NotImplementedError

    def updateTimer(self, timeLeft, vehsList, cooldowns):
        raise NotImplementedError

    def showGasAttackInfo(self, vehsList, cooldowns):
        raise NotImplementedError


_RESPAWN_SOUND_ID = 'respawn'

class RespawnsController(IArenaRespawnController, IViewComponentsController):
    __slots__ = ('__ui', '__isUIInited', '__vehicles', '__cooldowns', '__respawnInfo', '__timerCallback', '__showUICallback', '__soundNotifications', '__gasAttackMgr', '__eManager', 'onRespawnVisibilityChanged')

    def __init__(self, setup):
        super(RespawnsController, self).__init__()
        self.__ui = None
        self.__isUIInited = False
        self.__vehicles = []
        self.__cooldowns = {}
        self.__respawnInfo = None
        self.__timerCallback = None
        self.__showUICallback = None
        if setup.gasAttackMgr is not None:
            self.__gasAttackMgr = weakref.proxy(setup.gasAttackMgr)
        else:
            self.__gasAttackMgr = None
        self.__eManager = Event.EventManager()
        self.onRespawnVisibilityChanged = Event.Event(self.__eManager)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.RESPAWN

    def startControl(self, battleCtx, _):
        pass

    def stopControl(self):
        if self.__showUICallback is not None:
            BigWorld.cancelCallback(self.__showUICallback)
            self.__showUICallback = None
        self.__stopTimer()
        if self.__gasAttackMgr is not None:
            self.__gasAttackMgr.onAttackPreparing -= self.__onGasAttack
            self.__gasAttackMgr.onAttackStarted -= self.__onGasAttack
            self.__gasAttackMgr = None
        self.__ui = None
        self.__vehicles = None
        self.__cooldowns = None
        self.__respawnInfo = None
        return

    def setViewComponents(self, *components):
        self.__ui = components[0]
        self.__start()

    def clearViewComponents(self):
        self.__ui = None
        return

    def chooseVehicleForRespawn(self, vehicleID):
        BigWorld.player().base.chooseVehicleForRespawn(vehicleID)
        self.__ui.setSelectedVehicle(vehicleID, self.__vehicles, self.__cooldowns)

    def startPostmortem(self):
        self.__hide()

    def movingToRespawn(self):
        self.__respawnInfo = None
        self.__stopTimer()
        self.__cancelDelayedShow()
        getSoundNotifications().play(_RESPAWN_SOUND_ID)
        return

    def spawnVehicle(self, _):
        if BigWorld.player().isVehicleAlive:
            self.__respawnInfo = None
        self.__hide()
        return

    def updateRespawnVehicles(self, vehsList):
        self.__vehicles = []
        for v in vehsList:
            descr = vehicles.getVehicleType(v['compDescr'])
            self.__vehicles.append(_Vehicle(descr.compactDescr, descr, v['vehAmmo']))

    def updateRespawnCooldowns(self, cooldowns):
        self.__cooldowns = cooldowns

    def updateRespawnInfo(self, respawnInfo):
        intCD = vehicles.getVehicleTypeCompactDescr(respawnInfo['compDescr'])
        self.__respawnInfo = _RespawnInfo(intCD, respawnInfo['expiryRespawnDelay'], respawnInfo['respawnType'])
        needCooldown = respawnInfo.get('afterDeath', False)
        self.__showIfReady(needCooldown)

    def __start(self):
        if self.__gasAttackMgr is not None:
            self.__gasAttackMgr.onAttackPreparing += self.__onGasAttack
            self.__gasAttackMgr.onAttackStarted += self.__onGasAttack
        self.__showIfReady(needCooldown=False)
        return

    def __showIfReady(self, needCooldown):
        if self.__respawnInfo is None or self.__ui is None:
            return
        else:
            if self.__respawnInfo.respawnTime > BigWorld.serverTime():
                if needCooldown:
                    self.__showUICallback = BigWorld.callback(_SHOW_UI_COOLDOWN, self.__show)
                else:
                    self.__show()
            else:
                self.__respawnInfo = None
            return

    def __cancelDelayedShow(self):
        if self.__showUICallback is not None:
            BigWorld.cancelCallback(self.__showUICallback)
            self.__showUICallback = None
        return

    def __show(self):
        self.__cancelDelayedShow()
        if self.__ui is None:
            return
        else:
            if not self.__isUIInited:
                self.__isUIInited = True
                isLimited = self.__respawnInfo.respawnType == RESPAWN_TYPES.LIMITED
                self.__ui.start(self.__vehicles, isLimited)
            self.__ui.show(self.__respawnInfo.vehicleID, self.__vehicles, self.__cooldowns)
            if self.__gasAttackMgr is not None and self.__gasAttackMgr.state in (GasAttackState.ATTACK, GasAttackState.PREPARE):
                self.__ui.showGasAttackInfo(self.__vehicles, self.__cooldowns)
            else:
                self.__startTimer()
            self.onRespawnVisibilityChanged(True)
            return

    def __hide(self):
        self.__stopTimer()
        self.__cancelDelayedShow()
        if self.__ui is not None:
            self.__ui.hide()
            self.onRespawnVisibilityChanged(False)
        return

    def __startTimer(self):
        self.__timerCallback = None
        respawnTime = self.__respawnInfo.respawnTime
        timeLeft = max(0, respawnTime - BigWorld.serverTime())
        self.__ui.updateTimer(timeLeft, self.__vehicles, self.__cooldowns)
        if timeLeft > 0:
            self.__timerCallback = BigWorld.callback(1, self.__startTimer)
        return

    def __stopTimer(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

    def __onGasAttack(self):
        if self.__respawnInfo is not None:
            if self.__showUICallback is not None:
                self.__show()
            else:
                self.__stopTimer()
                self.__ui.showGasAttackInfo(self.__vehicles, self.__cooldowns)
            self.__respawnInfo = None
        return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/RespawnsController.py
import weakref
import BigWorld
from collections import namedtuple
from GasAttackSettings import GasAttackState
from constants import RESPAWN_TYPES
from gui.battle_control.arena_info import hasGasAttack
from items import vehicles
from gui.battle_control.arena_info.interfaces import IArenaRespawnController
from gui.battle_control.avatar_getter import getSoundNotifications
_SHOW_UI_COOLDOWN = 3.0
_Vehicle = namedtuple('_Vehicle', ('intCD', 'type', 'vehAmmo'))
_RespawnInfo = namedtuple('_RespawnInfo', ('vehicleID', 'respawnTime', 'respawnType'))

class RespawnsController(IArenaRespawnController):
    __slots__ = ('__ui', '__isUIInited', '__vehicles', '__cooldowns', '__respawnInfo', '__timerCallback', '__battle', '__showUICallback', '__respawnSndName', '__soundNotifications', '__gasAttackMgr')

    def __init__(self, ctx):
        super(RespawnsController, self).__init__()
        self.__ui = None
        self.__isUIInited = False
        self.__battle = None
        self.__vehicles = []
        self.__cooldowns = {}
        self.__respawnInfo = None
        self.__timerCallback = None
        self.__showUICallback = None
        self.__respawnSndName = 'respawn'
        self.__gasAttackMgr = None
        if hasGasAttack():
            self.__gasAttackMgr = ctx.gasAttackMgr
        return

    def start(self, ui, battleProxy):
        self.__ui = weakref.proxy(ui)
        self.__battle = battleProxy
        if self.__gasAttackMgr is not None:
            self.__gasAttackMgr.onAttackPreparing += self.__onGasAttack
            self.__gasAttackMgr.onAttackStarted += self.__onGasAttack
        if self.__respawnInfo is not None:
            if self.__respawnInfo.respawnTime > BigWorld.serverTime():
                self.__show()
            else:
                self.__respawnInfo = None
        return

    def stop(self):
        if self.__showUICallback is not None:
            BigWorld.cancelCallback(self.__showUICallback)
            self.__showUICallback = None
        self.__stopTimer()
        if self.__gasAttackMgr is not None:
            self.__gasAttackMgr.onAttackPreparing -= self.__onGasAttack
            self.__gasAttackMgr.onAttackStarted -= self.__onGasAttack
            self.__gasAttackMgr = None
        self.__ui = None
        self.__battle = None
        return

    def clear(self):
        self.__vehicles = None
        self.__cooldowns = None
        self.__respawnInfo = None
        return

    def setBattleCtx(self, battleCtx):
        pass

    def chooseVehicleForRespawn(self, vehicleID):
        BigWorld.player().base.chooseVehicleForRespawn(vehicleID)
        self.__ui.setSelectedVehicle(vehicleID, self.__vehicles, self.__cooldowns)

    def movingToRespawn(self):
        self.__respawnInfo = None
        self.__stopTimer()
        getSoundNotifications().play(self.__respawnSndName)
        return

    def spawnVehicle(self, vehicleID):
        if BigWorld.player().isVehicleAlive:
            self.__respawnInfo = None
        if self.__ui is not None:
            self.__ui.hide()
            self.__battle.minimap.useNormalSize()
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
        if self.__ui is not None:

            def show():
                self.__showUICallback = None
                self.__show()
                return

            if respawnInfo.get('afterDeath', False):
                self.__showUICallback = BigWorld.callback(_SHOW_UI_COOLDOWN, show)
            else:
                show()
        return

    def __show(self):
        if self.__ui is None:
            return
        else:
            if not self.__isUIInited:
                self.__isUIInited = True
                isLimited = self.__respawnInfo.respawnType == RESPAWN_TYPES.LIMITED
                self.__ui.start(self.__vehicles, isLimited)
            self.__ui.show(self.__respawnInfo.vehicleID, self.__vehicles, self.__cooldowns)
            self.__battle.radialMenu.forcedHide()
            self.__battle.minimap.useRespawnSize()
            if self.__gasAttackMgr is not None and self.__gasAttackMgr.state in (GasAttackState.ATTACK, GasAttackState.PREPARE):
                self.__ui.showGasAttackInfo(self.__vehicles, self.__cooldowns)
            else:
                self.__startTimer()
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
            self.__stopTimer()
            self.__ui.showGasAttackInfo(self.__vehicles, self.__cooldowns)
            self.__respawnInfo = None
        return

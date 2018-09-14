# Embedded file name: scripts/client/gui/battle_control/RespawnsController.py
import weakref
import BigWorld
from collections import namedtuple
import operator
from gui.shared import g_itemsCache
from items import vehicles
from gui.battle_control.arena_info.interfaces import IArenaRespawnController
_Vehicle = namedtuple('_Vehicle', ('intCD', 'type', 'vehAmmo'))
_RespawnInfo = namedtuple('_RespawnInfo', ('vehicleID', 'respawnTime'))

class RespawnsController(IArenaRespawnController):
    __slots__ = ('__ui', '__vehicles', '__cooldowns', '__respawnInfo', '__timerCallback', '__battle', '__showUICallback')
    __SHOW_UI_COOLDOWN = 3.0

    def __init__(self):
        super(RespawnsController, self).__init__()
        self.__ui = None
        self.__battle = None
        self.__vehicles = []
        self.__cooldowns = {}
        self.__respawnInfo = None
        self.__timerCallback = None
        self.__showUICallback = None
        return

    def start(self, ui, battleProxy):
        self.__ui = weakref.proxy(ui)
        self.__battle = battleProxy
        self.__ui.start(self.__vehicles)
        if self.__respawnInfo is not None:
            if BigWorld.player().isGuiVisible:
                self.__battle.showAll(False)
            self.__ui.show(self.__respawnInfo.vehicleID, self.__vehicles, self.__cooldowns)
            self.__battle.radialMenu.forcedHide()
            self.__startTimer()
        return

    def stop(self):
        if self.__showUICallback is not None:
            BigWorld.cancelCallback(self.__showUICallback)
            self.__showUICallback = None
        self.__stopTimer()
        self.__ui = None
        self.__battle = None
        return

    def destroy(self):
        self.__vehicles = None
        self.__cooldowns = None
        self.__respawnInfo = None
        return

    def setBattleCtx(self, battleCtx):
        pass

    def chooseVehicleForRespawn(self, vehicleID):
        BigWorld.player().base.chooseVehicleForRespawn(vehicleID)
        self.__ui.setSelectedVehicle(vehicleID, self.__vehicles, self.__cooldowns)

    def spawnVehicle(self, vehicleID):
        self.__respawnInfo = None
        if self.__ui is not None:
            if BigWorld.player().isGuiVisible:
                self.__battle.showAll(True)
            self.__ui.hide()
            self.__stopTimer()
        return

    def updateRespawnVehicles(self, vehsList):
        self.__vehicles = []
        vehs = map(lambda v: (g_itemsCache.items.getItemByCD(vehicles.getVehicleTypeCompactDescr(v['compDescr'])), v), vehsList)
        for v, vData in sorted(vehs, key=operator.itemgetter(0)):
            self.__vehicles.append(_Vehicle(v.intCD, v.descriptor.type, vData['vehAmmo']))

    def updateRespawnCooldowns(self, cooldowns):
        self.__cooldowns = cooldowns

    def updateRespawnInfo(self, respawnInfo):
        intCD = vehicles.getVehicleTypeCompactDescr(respawnInfo['compDescr'])
        self.__respawnInfo = _RespawnInfo(intCD, respawnInfo['expiryRespawnDelay'])
        if self.__ui is not None:

            def show():
                self.__showUICallback = None
                self.__show()
                return

            if respawnInfo.get('afterDeath', False):
                self.__showUICallback = BigWorld.callback(self.__SHOW_UI_COOLDOWN, show)
            else:
                show()
        return

    def __show(self):
        if BigWorld.player().isGuiVisible:
            self.__battle.showAll(False)
        self.__ui.show(self.__respawnInfo.vehicleID, self.__vehicles, self.__cooldowns)
        self.__battle.radialMenu.forcedHide()
        self.__startTimer()

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

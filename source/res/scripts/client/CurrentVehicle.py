# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CurrentVehicle.py
# Compiled at: 2019-03-04 05:33:02
import BigWorld
from AccountCommands import LOCK_REASON
from account_helpers.AccountSettings import AccountSettings
from account_helpers.AccountPrebattle import AccountPrebattle
from adisp import process, async
from Event import Event, EventManager
from constants import WOT_CLASSIC_LOCK_MODE
from gui.Scaleform.Waiting import Waiting

class _CurrentVehicle(object):

    def __init__(self):
        self.firstTimeInitialized = False
        self.__eventManager = EventManager()
        self.onChanged = Event(self.__eventManager)
        self.__vehicle = None
        self.__changeCallbackID = None
        self.__clanLock = 0
        return

    def __reset(self):
        self.firstTimeInitialized = False
        self.__vehicle = None
        return

    def isVehicleTypeLocked(self):
        return self.__clanLock != 0

    def cleanup(self):
        self.reset(True)
        self.__eventManager.clear()

    def __setVehicleToServer(self, id):
        AccountSettings.setFavorites('current', id)

    def __repr__(self):
        return 'CurrentVehicle(%s)' % str(self.__vehicle)

    def __getVehicle(self):
        return self.__vehicle

    def __setVehicle(self, newVehicle):
        self.__request(newVehicle.inventoryId)

    def setVehicleById(self, id):
        self.__request(id)

    vehicle = property(__getVehicle, __setVehicle)

    def __getRepairCost(self):
        return self.__vehicle.repairCost

    def __setRepairCost(self, newValue):
        if self.__vehicle.repairCost != newValue:
            self.__vehicle.repairCost = newValue
            self.onChanged()

    repairCost = property(__getRepairCost, __setRepairCost)

    def isBroken(self):
        return self.__vehicle.repairCost > 0

    def setLocked(self, newValue):
        if self.__vehicle.lock != newValue:
            self.__vehicle.lock = newValue
            self.onChanged()

    def isCrewFull(self):
        return self.isPresent() and None not in self.__vehicle.crew and self.__vehicle.crew != []

    def isInBattle(self):
        return self.__vehicle.lock == LOCK_REASON.ON_ARENA

    def isInHangar(self):
        return self.isPresent() and not self.isInBattle()

    def isAwaitingBattle(self):
        return self.__vehicle.lock == LOCK_REASON.IN_QUEUE

    def isLocked(self):
        return self.__vehicle.lock != LOCK_REASON.NONE

    def isAlive(self):
        return self.isPresent() and not self.isBroken() and not self.isLocked()

    def isReadyToFight(self):
        isBSVehicleLockMode = AccountPrebattle.getSettings().get('vehicleLockMode', False)
        isCurrentVehicleTypeLocked = self.isVehicleTypeLocked()
        return self.isAlive() and self.isCrewFull() and (isBSVehicleLockMode and not isCurrentVehicleTypeLocked or not isBSVehicleLockMode)

    def isPresent(self):
        return self.__vehicle is not None

    def getState(self):
        if not self.isInHangar():
            return None
        elif self.__vehicle.modelState != 'damaged':
            return self.__vehicle.modelState
        else:
            return 'undamaged'

    def getHangarMessage(self):
        message = '#menu:currentVehicleStatus/'
        ms = getattr(self.__vehicle, 'modelState', None)
        if self.vehicle is None:
            message += 'notpresent'
        elif self.isInBattle():
            message += 'inbattle'
        elif self.isLocked():
            message += 'locked'
        elif ms == 'undamaged' and not self.isCrewFull():
            message += 'crewNotFull'
        else:
            message += ms
        return message

    def reset(self, silent=False):
        self.__reset()
        if not silent:
            self.onChanged()

    @process
    def __request(self, inventoryId):
        Waiting.show('updateCurrentVehicle', True)
        from gui.Scaleform.utils.requesters import Requester, StatsRequester
        vehicles = yield Requester('vehicle').getFromInventory()
        vehicleTypeLocks = yield StatsRequester().getVehicleTypeLocks()
        old = self.__vehicle
        self.__vehicle = self.__findCurrent(inventoryId, vehicles)
        if self.__vehicle and self.__vehicle != old:
            self.__setVehicleToServer(self.__vehicle.inventoryId)
        self.__clanLock = vehicleTypeLocks.get(self.__vehicle.descriptor.type.compactDescr, {}).get(WOT_CLASSIC_LOCK_MODE, 0) if self.isPresent() else 0
        if not self.__changeCallbackID:
            self.__changeCallbackID = BigWorld.callback(0.1, self.__changeDone)

    def __changeDone(self):
        self.__changeCallbackID = None
        player = BigWorld.player()
        if player and hasattr(player, 'isPlayer') and player.isPlayer:
            self.onChanged()
        Waiting.hide('updateCurrentVehicle')
        return

    def __findCurrent(self, inventoryId, vehicles):
        for vehicle in vehicles:
            if vehicle.inventoryId == inventoryId:
                return vehicle

        vehicles.sort()
        if len(vehicles):
            return vehicles[0]
        else:
            return None

    def update(self):
        if self.firstTimeInitialized:
            self.__request(self.__vehicle.inventoryId if self.__vehicle else None)
        return

    @async
    @process
    def getFromServer(self, callback):
        currentId = AccountSettings.getFavorites('current')
        from gui.Scaleform.utils.requesters import Requester
        vehicles = yield Requester('vehicle').getFromInventory()
        self.__vehicle = self.__findCurrent(currentId, vehicles)
        self.onChanged()
        self.firstTimeInitialized = True
        callback(True)


g_currentVehicle = _CurrentVehicle()

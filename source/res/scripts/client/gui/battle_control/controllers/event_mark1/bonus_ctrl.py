# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_mark1/bonus_ctrl.py
import weakref
import BigWorld
import Event
from gui.battle_control.controllers.event_mark1.common import SoundViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from constants import VEHICLE_MISC_STATUS, FLAG_TYPES, MARK1_TEAM_NUMBER
from CTFManager import g_ctfManager
from gui.shared.utils.TimeInterval import TimeInterval
from debug_utils import LOG_DEBUG, LOG_WARNING
from items import vehicles

class STATES(object):
    ATTACK_REPAIR_TAKEN = 'attackRepairTaken'
    ATTACK_REPAIR_DELIVERED = 'attackRepairDelivered'
    DEFENCE_BOMB_TAKEN = 'defenceBombTaken'
    DEFENCE_BOMB_DELIVERED = 'defenceBombDelivered'
    BIG_GUN_TAKEN = 'bigGunTaken'
    MACHINE_GUN_TAKEN = 'machineGunTaken'


EXTRA_BIG_GUN = 'ingameammoBigGun'
EXTRA_MACHINE_GUN = 'machinegunReload'
_OPCODE_ARENA_BONUS_SNAPSHOT = 0
_OPCODE_ARENA_BONUS_ENABLED = 1
_OPCODE_ARENA_BONUS_DISABLED = -1
_OPCODE_ARENA_BONUS_TO_VEHICLE_MISC_STATUS = {_OPCODE_ARENA_BONUS_SNAPSHOT: VEHICLE_MISC_STATUS.BONUS_ON,
 _OPCODE_ARENA_BONUS_ENABLED: VEHICLE_MISC_STATUS.BONUS_ON,
 _OPCODE_ARENA_BONUS_DISABLED: VEHICLE_MISC_STATUS.BONUS_OFF}

class IFlagBonusNotificationView(object):

    def showState(self, state):
        raise NotImplementedError

    def carriedFlagDropped(self):
        raise NotImplementedError

    def showBombCountDown(self, timeLeft):
        raise NotImplementedError

    def hideBombCountDown(self):
        raise NotImplementedError


_CAPTURE_MAP = {(FLAG_TYPES.REPAIR_KIT, True): STATES.ATTACK_REPAIR_TAKEN,
 (FLAG_TYPES.EXPLOSIVE, False): STATES.DEFENCE_BOMB_TAKEN}
_DELIVERY_MAP = {(FLAG_TYPES.REPAIR_KIT, True): STATES.ATTACK_REPAIR_DELIVERED,
 (FLAG_TYPES.EXPLOSIVE, False): STATES.DEFENCE_BOMB_DELIVERED}
_SOUND_MAP = {STATES.BIG_GUN_TAKEN: 'mark1_big_gun',
 STATES.MACHINE_GUN_TAKEN: 'mark1_machine_gun',
 STATES.ATTACK_REPAIR_TAKEN: 'mark1_repair_kit_taken',
 STATES.ATTACK_REPAIR_DELIVERED: 'mark1_repair_kit_delivered',
 STATES.DEFENCE_BOMB_TAKEN: 'mark1_bomb_taken',
 STATES.DEFENCE_BOMB_DELIVERED: 'mark1_bomb_delivered'}

class Mark1BonusController(SoundViewComponentsController):

    def __init__(self, setup):
        super(Mark1BonusController, self).__init__()
        self.__ui = None
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__bonusCache = {}
        self.__bombCountDown = -1
        self.__bombTimer = None
        self.__eManager = Event.EventManager()
        self.onBonusBigGunTaken = Event.Event(self.__eManager)
        self.onBonusMachineGunTaken = Event.Event(self.__eManager)
        self.onBonusEnded = Event.Event(self.__eManager)
        self.onBombPlanted = Event.Event(self.__eManager)
        self.onBombExploded = Event.Event(self.__eManager)
        self.onMark1Killed = Event.Event(self.__eManager)
        self.onLastBombPlanted = Event.Event(self.__eManager)
        self.__eventHandler = {(EXTRA_BIG_GUN, VEHICLE_MISC_STATUS.BONUS_ON): self.__onBonusBigGunTaken,
         (EXTRA_BIG_GUN, VEHICLE_MISC_STATUS.BONUS_OFF): self.__onBonusEnded,
         (EXTRA_MACHINE_GUN, VEHICLE_MISC_STATUS.BONUS_ON): self.__onBonusMachineGunTaken,
         (EXTRA_MACHINE_GUN, VEHICLE_MISC_STATUS.BONUS_OFF): self.__onBonusEnded}
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.MARK1_BONUS

    def startControl(self, *args):
        self.__showEventsOnStart()
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
        g_ctfManager.onFlagRemoved += self.__onFlagRemoved

    def stopControl(self):
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
        g_ctfManager.onFlagRemoved -= self.__onFlagRemoved
        self.__eventHandler.clear()
        self.__eventHandler = None
        self.__eManager.clear()
        self.__eManager = None
        self.__destroyBombTimer()
        self.clearViewComponents()
        self.__arenaDP = None
        self.__bonusCache = {}
        return

    def setViewComponents(self, *components):
        self.__ui = components[0]
        self.__showEventsOnStart()

    def clearViewComponents(self):
        self.__ui = None
        return

    def bonusChangedFromAvatar(self, vehicleID, miscCode, extraIndex):
        self.__bonusChanged(vehicleID, miscCode, extraIndex)

    def bonusChangedFromArena(self, opcode, info):
        """
        Bonus info was received from Arena. We should ignore info for our Vehicle
        because it is set from Avatar. This solution is necessary for 'observer' case,
        when we are switching to other vehicles to show their bonus in Ammo panel
        :param opcode: 0 - full snapshot of current bonuses for arena,
                       1 - means that vehicle <vehicleID> has now <bonus idx> enabled
                       -1 - means that vehicle <vehicleID> has now <bonus idx> disabled
        :param info: {vehicleID: (bonus idx, bonus end time), ...}
                     'bonus end time' will be -1.0 for any vehicle except Mark1
        """
        for vehicleID, (extraIndex, endTime) in info.iteritems():
            if vehicleID != self.__getPlayerVehicleID():
                miscCode = _OPCODE_ARENA_BONUS_TO_VEHICLE_MISC_STATUS[opcode]
                vTypeInfoVO = self.__arenaDP.getVehicleInfo(vehicleID).vehicleType
                if vTypeInfoVO.isMark1:
                    timeLeft = endTime - BigWorld.serverTime()
                    self.__bonusChangedForMark1(miscCode, round(timeLeft), vehicleID)
                else:
                    self.__bonusChanged(vehicleID, miscCode, extraIndex)

    def getVehicleBonus(self, vehicleID):
        """
        Return bonus name if it on vehicle and vehicle is in AOI
        :param vehicleID: id of vehicle
        :return: EXTRA_BIG_GUN, EXTRA_MACHINE_GUN or None
        """
        if vehicleID in self.__bonusCache:
            miscCode, extraIndex = self.__bonusCache[vehicleID]
            if miscCode == VEHICLE_MISC_STATUS.BONUS_ON:
                extraName = self.__getExtraName(vehicleID, extraIndex)
                if extraName in (EXTRA_BIG_GUN, EXTRA_MACHINE_GUN):
                    result = extraName
                else:
                    result = None
            else:
                result = None
        else:
            result = None
        return result

    def getMark1BombTimeLeft(self):
        """
        Just return the counter.
        for values <=0 it means - no bomb
        for values >0 - timer in progress
        :return: value of time left
        """
        return self.__bombCountDown

    def showVehicleKilledMessage(self, targetID):
        """
        This method notifies about Mark1 death.
        :param targetID: id of dead vehicle
        """
        vTypeInfoVO = self.__arenaDP.getVehicleInfo(targetID).vehicleType
        if vTypeInfoVO.isMark1:
            self.onMark1Killed()
            g_ctfManager.onMark1Killed()

    def _getSoundMap(self):
        return _SOUND_MAP

    def _updateBombTimer(self):
        self.__bombCountDown -= 1
        if self.__bombCountDown < 0:
            self.__destroyBombTimer()
        else:
            self.__onBombPlanted(self.__bombCountDown)

    def __createBombTimer(self, timeLeft):
        self.__destroyBombTimer()
        self.__bombCountDown = timeLeft
        self.__onBombPlanted(self.__bombCountDown)
        self.__bombTimer = TimeInterval(1, self, '_updateBombTimer')
        self.__bombTimer.start()

    def __destroyBombTimer(self):
        if self.__bombTimer is not None:
            self.__bombTimer.stop()
            self.__bombTimer = None
            self.__bombCountDown = -1
            self.__onBombExploded()
        return

    def __bonusChanged(self, vehicleID, miscCode, extraIndex):
        """
        Bonus changed from Avatar or Arena
        :param vehicleID: id of vehicle
        :param miscCode: VEHICLE_MISC_STATUS.BONUS_ON or VEHICLE_MISC_STATUS.BONUS_OFF
        :param extraIndex: vehicle extra index
        """
        self.__bonusCache[vehicleID] = (miscCode, extraIndex)
        extraName = self.__getExtraName(vehicleID, extraIndex)
        if extraName:
            self.__processExtra((extraName, miscCode), vehicleID)

    @staticmethod
    def __getExtraName(vehicleID, extraIndex):
        """
        Return extra name or None
        :param vehicleID: id of vehicle
        :param extraIndex: index of extra
        """
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is not None:
            vehExtras = vehicle.typeDescriptor.extras
            if extraIndex < len(vehExtras):
                extraName = vehExtras[extraIndex].name
                result = extraName
            else:
                LOG_WARNING('ExtraIndex is out of range:', extraIndex)
                result = None
        else:
            result = None
        return result

    def __processExtra(self, eventKey, vehicleID):
        if eventKey in self.__eventHandler:
            handler = self.__eventHandler[eventKey]
            handler(vehicleID)
        else:
            LOG_DEBUG('Bonus event is not found for key', eventKey)

    def __bonusChangedForMark1(self, miscCode, timeLeft, mark1VehicleID):
        if miscCode == VEHICLE_MISC_STATUS.BONUS_ON and timeLeft <= 0:
            if self.__bombTimer is None:
                self.__onBombExploded()
            else:
                self.__destroyBombTimer()
        elif miscCode == VEHICLE_MISC_STATUS.BONUS_OFF:
            self.__destroyBombTimer()
        else:
            self.__createBombTimer(timeLeft)
            vehicle = BigWorld.entities.get(mark1VehicleID)
            if vehicle is not None:
                explosiveInfo = vehicles.g_cache.commonConfig['extrasDict']['explosive']
                if explosiveInfo.maxDamage >= vehicle.health:
                    self.onLastBombPlanted()
        return

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        if vehicleID == self.__getPlayerVehicleID():
            self.__showAndPlayByMapping(_CAPTURE_MAP, flagID)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        if vehicleID == self.__getPlayerVehicleID():
            self.__showAndPlayByMapping(_DELIVERY_MAP, flagID)

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        if loserVehicleID == self.__getPlayerVehicleID():
            if self.__ui is not None:
                self.__ui.carriedFlagDropped()
        return

    def __onFlagRemoved(self, flagID, flagTeam, vehicleID):
        if vehicleID == self.__getPlayerVehicleID():
            if self.__ui is not None:
                self.__ui.carriedFlagDropped()
        return

    def __onBonusBigGunTaken(self, vehicleID):
        self.onBonusBigGunTaken(vehicleID)
        if vehicleID == self.__getPlayerVehicleID():
            self.__showAndPlay(STATES.BIG_GUN_TAKEN)

    def __onBonusMachineGunTaken(self, vehicleID):
        self.onBonusMachineGunTaken(vehicleID)
        if vehicleID == self.__getPlayerVehicleID():
            self.__showAndPlay(STATES.MACHINE_GUN_TAKEN)

    def __onBonusEnded(self, vehicleID):
        self.onBonusEnded(vehicleID)

    def __onBombPlanted(self, timeLeft):
        self.onBombPlanted(timeLeft)
        if self.__ui is not None:
            self.__ui.showBombCountDown(timeLeft)
        return

    def __onBombExploded(self):
        g_ctfManager.onBombExploded()
        self.onBombExploded()
        if self.__ui is not None:
            self.__ui.hideBombCountDown()
        return

    def __getPlayerVehicleID(self):
        return self.__arenaDP.getPlayerVehicleID()

    def __showEventsOnStart(self):
        flagID = g_ctfManager.getVehicleCarriedFlagID(self.__getPlayerVehicleID())
        if flagID is not None:
            self.__showAndPlayByMapping(_CAPTURE_MAP, flagID)
        return

    def __showAndPlayByMapping(self, mapping, flagID):
        flagType = g_ctfManager.getFlagType(flagID)
        isMarkTeam = self.__arenaDP.getNumberOfTeam() == MARK1_TEAM_NUMBER
        key = (flagType, isMarkTeam)
        if key in mapping:
            self.__showAndPlay(mapping[key])

    def __showAndPlay(self, state):
        if self.__ui is not None:
            self.__ui.showState(state)
            self._playSound(state)
        return

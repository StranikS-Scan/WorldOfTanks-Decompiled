# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StationaryReloadController.py
import math
import typing
from collections import namedtuple
import BigWorld
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from constants import STATIONARY_RELOAD_STATE, GUN_LOCK_REASONS
from events_handler import eventHandler
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState, AmmoShootPossibility
from gui.shared.utils.decorators import ReprInjector
from helpers import dependency
from messenger_common_chat2 import messageArgs
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesEvents, createMechanicStatesEvents, IMechanicStatesComponent, IMechanicState
if typing.TYPE_CHECKING:
    from typing import Optional, Any
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents

class StationaryReloadAmmoState(DefaultComponentAmmoState):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, state, baseTime, timeLeft):
        super(StationaryReloadAmmoState, self).__init__()
        self.__state = state
        self.__baseTime = baseTime
        self.__timeLeft = timeLeft

    def __eq__(self, other):
        return isinstance(other, StationaryReloadAmmoState) and self.__state == other.stationaryReloadState and self.__baseTime == other.stationaryBaseTime and self.__timeLeft == other.stationaryTimeLeft

    @classmethod
    def fromComponentStatus(cls, status):
        return cls(status.state, status.baseTime, status.timeLeft)

    @property
    def stationaryReloadState(self):
        return self.__state

    @property
    def stationaryBaseTime(self):
        return self.__baseTime

    @property
    def stationaryTimeLeft(self):
        return self.__timeLeft

    def isReloadingBlocked(self):
        return self.__state not in (STATIONARY_RELOAD_STATE.RELOADING, STATIONARY_RELOAD_STATE.IDLE)

    def getShootPossibility(self, _):
        isShootPossible = self.__state == STATIONARY_RELOAD_STATE.IDLE
        return AmmoShootPossibility.NOT_DEFINED if isShootPossible else AmmoShootPossibility.DENIED

    def getSpecialReloadMessage(self):
        if self.__state not in STATIONARY_RELOAD_STATE.TO_RELOADING_STATES:
            return None
        else:
            ammo = self.__sessionProvider.shared.ammo
            timeLeft = math.ceil(ammo.getGunReloadingState().getActualValue())
            quantity = ammo.getShellsQuantityLeft()
            return (BATTLE_CHAT_COMMAND_NAMES.RELOADING_CASSETE, messageArgs(floatArg1=timeLeft, int32Arg1=quantity)) if quantity > 0 and quantity != ammo.getGunSettings().clip.size else (BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN, messageArgs(floatArg1=timeLeft))


class StationaryReloadModeState(namedtuple('StationaryReloadModeState', ('state', 'gunLockMask', 'sequenceEndTime')), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status):
        return cls(status.state, status.gunLockMask, status.sequenceEndTime)

    @property
    def sequenceTimeLeft(self):
        return max(0, self.sequenceEndTime - BigWorld.serverTime())

    def isTransition(self, other):
        return self.state != other.state or self.gunLockMask != other.gunLockMask


@ReprInjector.withParent()
class StationaryReloadController(VehicleDynamicComponent, IGunMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    DEFAULT_AMMO_STATE = StationaryReloadAmmoState(STATIONARY_RELOAD_STATE.IDLE, 0.0, 0.0)
    DEFAULT_MODE_STATE = StationaryReloadModeState(STATIONARY_RELOAD_STATE.IDLE, GUN_LOCK_REASONS.NONE, 0.0)

    def __init__(self):
        super(StationaryReloadController, self).__init__()
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    def set_status(self, _):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.STATIONARY_RELOAD

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getAmmoState(self):
        return StationaryReloadAmmoState.fromComponentStatus(self.status) if self.status else self.DEFAULT_AMMO_STATE

    def getMechanicState(self):
        return StationaryReloadModeState.fromComponentStatus(self.status) if self.status else self.DEFAULT_MODE_STATE

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(StationaryReloadController, self).onDestroy()

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = self.getAmmoState()

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.MANUAL_RELOAD)
        return False

    def _onAppearanceReady(self):
        super(StationaryReloadController, self)._onAppearanceReady()
        self.__mechanicPrefabSpawner.loadAppearancePrefab()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(StationaryReloadController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _onComponentAvatarUpdate(self, player):
        super(StationaryReloadController, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

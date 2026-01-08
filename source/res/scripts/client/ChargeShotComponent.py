# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ChargeShotComponent.py
import typing
import BigWorld
from constants import CHARGE_SHOT_FLAGS as FLAGS
from constants import VEHICLE_SETTING
from events_handler import eventHandler
from gui.battle_control.battle_constants import CANT_SHOOT_ERROR
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.component_wrappers import ifPlayerVehicle
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicState, IMechanicStatesComponent
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
if typing.TYPE_CHECKING:
    from items.components.gun_installation_components import GunInstallationSlot
    from items.components.shared_components import ChargeShotParams

@ReprInjector.simple('flags', 'level', 'baseTime', 'endTime')
class ChargeShotState(IMechanicState):
    __slots__ = ('flags', 'level', 'baseTime', 'endTime', 'hasCharging', 'hasShotBlock', 'canStart', 'isGunDestroyed')

    def __init__(self, flags, level=0, baseTime=0.0, endTime=0.0):
        self.flags = flags
        self.level = level
        self.endTime = endTime
        self.baseTime = baseTime
        self.hasCharging = bool(flags & FLAGS.CHARGING)
        self.hasShotBlock = bool(flags & FLAGS.SHOT_BLOCK)
        self.canStart = not bool(flags & FLAGS.CANT_START_MASK)
        self.isGunDestroyed = bool(flags & FLAGS.GUN_DESTROYED)

    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime() if self.endTime >= 0 else self.baseTime)

    def progress(self, timeLeft):
        return max(0.0, 1.0 - timeLeft / self.baseTime if self.baseTime > 0 else 1.0)

    def isTransition(self, other):
        return self.level != other.level or self.flags != other.flags


class ChargeShotAmmoState(DefaultComponentAmmoState):

    def __init__(self, mechanicState):
        self.__mechanicState = mechanicState

    def canChangeVehicleSetting(self, code):
        return not self.__mechanicState.hasCharging and not self.__mechanicState.hasShotBlock if code == VEHICLE_SETTING.CURRENT_SHELLS else super(ChargeShotAmmoState, self).canChangeVehicleSetting(code)

    def canShootValidation(self):
        return (False, CANT_SHOOT_ERROR.CHARGE_SHOT_BLOCKING) if self.__mechanicState.hasShotBlock else super(ChargeShotAmmoState, self).canShootValidation()


@ReprInjector.withParent()
class ChargeShotComponent(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    DEFAULT_MECHANIC_STATE = ChargeShotState(FLAGS.RELOADING)

    def __init__(self):
        super(ChargeShotComponent, self).__init__()
        self.__params = None
        self.__state = self.DEFAULT_MECHANIC_STATE
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.CHARGE_SHOT

    @property
    def statesEvents(self):
        return self.__statesEvents

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    def getComponentParams(self):
        return self.__params

    def getMechanicState(self):
        return self.__state

    def set_privateState(self, _):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    def set_publicState(self, _):
        player = BigWorld.player()
        if not self.isPlayerVehicle(player):
            self._updateComponentAppearance()

    def onDestroy(self):
        self.__statesEvents.destroy()
        self.__commandsEvents.destroy()
        super(ChargeShotComponent, self).onDestroy()

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = ChargeShotAmmoState(self.__state)

    @eventHandler
    def onDiscreteShotDone(self, gunInstallationSlot):
        if gunInstallationSlot.isMainInstallation():
            predictedState = ChargeShotState(self.__state.flags & ~FLAGS.CHARGING | FLAGS.RELOADING)
            self._updateComponentAppearance(predictedState=predictedState)
            self._updateComponentAvatar()

    @ifPlayerVehicle
    def tryActivate(self, player):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        state = self.__state
        flags = state.flags | FLAGS.GUN_DIVING if player.isOwnBarrelUnderWater else state.flags & ~FLAGS.GUN_DIVING
        if flags & FLAGS.CANT_START_MASK:
            if state.flags != flags:
                state = ChargeShotState(flags, state.level, state.baseTime, state.endTime)
        else:
            self.cell.tryCharge()
            baseTime = self.__params.timePerLevel[0]
            endTime = BigWorld.serverTime() + baseTime
            state = ChargeShotState(flags | FLAGS.CHARGING, 0, baseTime, endTime)
        self._updateComponentAppearance(predictedState=state)
        self._updateComponentAvatar()

    def _onAppearanceReady(self):
        super(ChargeShotComponent, self)._onAppearanceReady()
        self.__mechanicPrefabSpawner.loadAppearancePrefab()
        self.__state = self.__getCurrentState()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, predictedState=None, **kwargs):
        super(ChargeShotComponent, self)._onComponentAppearanceUpdate(**kwargs)
        self.__state = predictedState or self.__getCurrentState()
        self.__statesEvents.updateMechanicState(self.__state)

    def _onComponentAvatarUpdate(self, player):
        super(ChargeShotComponent, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    def _collectComponentParams(self, typeDescriptor):
        super(ChargeShotComponent, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)

    def __getCurrentState(self):
        if self.privateState is not None:
            privState = self.privateState
            newState = ChargeShotState(privState.flags, privState.level, 0.0, privState.endTime)
            if newState.hasCharging:
                newState.baseTime = self.__params.timePerLevel[newState.level]
            elif newState.hasShotBlock:
                newState.baseTime = self.__params.shotBlockTime
        elif self.publicState is not None:
            pubState = self.publicState
            newState = ChargeShotState(pubState.flags, pubState.level)
        else:
            newState = self.DEFAULT_MECHANIC_STATE
        return newState

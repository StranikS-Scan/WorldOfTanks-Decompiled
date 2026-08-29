# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BustleFeedController.py
from __future__ import absolute_import, division
import typing
import weakref
import BigWorld
from constants import ARENA_PERIOD, BUSTLE_FEED_STATE, BUSTLE_FEED_SWITCH_ACCESS
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.component_wrappers import ifAppearanceReady, ifPlayerVehicle, ifObservedVehicle
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.entities import ShotParams
from vehicles.mechanics.generic_mechanics.bustle_feed import createBustleFeedStatesEvents, DEFAULT_BUSTLE_FEED_PARAMS, BustleFeedComponentParams, BustleFeedState, BustleFeedAmmoState
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_inputs import createMechanicSingleInput
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
if typing.TYPE_CHECKING:
    import CGF
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents

class PlayerVehicleInputPredicate(object):

    def __init__(self, entity):
        super(PlayerVehicleInputPredicate, self).__init__()
        self._entityRef = weakref.ref(entity)

    def __call__(self):
        vehicle = self._entityRef()
        return vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() and self._hasBattleStarted()

    @staticmethod
    def _hasBattleStarted():
        player = BigWorld.player()
        return False if player is None or player.arena is None else player.arena.period in (ARENA_PERIOD.BATTLE, ARENA_PERIOD.AFTERBATTLE)


@ReprInjector.withParent()
class BustleFeedController(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    _INPUT_ACTION_NAME = 'ABILITY_1_INPUT_ACTION'
    _INPUT_PROFILE_NAME = 'ABILITY_1_INPUT_PROFILE'

    def __init__(self):
        super(BustleFeedController, self).__init__()
        self.__singleInput = None
        self.__componentParams = DEFAULT_BUSTLE_FEED_PARAMS
        self.__variableStorageGO = None
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createBustleFeedStatesEvents(self)
        self.__prefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__shootingBlockTimestamp = 0
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.BUSTLE_FEED

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        baseTime = -1.0
        endTime = 0.0
        state = BUSTLE_FEED_STATE.INACTIVE
        switchAccessState = BUSTLE_FEED_SWITCH_ACCESS.LOCKED
        if self.status is not None:
            state = self.status.state
            baseTime = self.status.baseTime
            endTime = self.status.endTime
            switchAccessState = self.status.switchAccessState
        return BustleFeedState(state, baseTime, endTime, switchAccessState)

    def getComponentParams(self):
        return self.__componentParams

    def getVariableStorageGO(self):
        return self.__variableStorageGO

    def setVariableStorageGO(self, go):
        self.__variableStorageGO = go

    def set_status(self, *_):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    def set_reloadStatus(self, *_):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = BustleFeedAmmoState(self.getMechanicState(), self.__componentParams.modifiedShells, self.__componentParams.shotReloadFactor)

    @eventHandler
    def onCollectShotParams(self, shotParamsList):
        if self.__shootingBlockTimestamp > BigWorld.time():
            shotParamsList.append(ShotParams(self.vehicleMechanic, 0, 0, False))

    @eventHandler
    def onObserverVehicleDataUpdated(self):
        self.__statesEvents.updateMechanicState(self.getMechanicState())
        self.__updateVehicleGunReloadTime()

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        self.__variableStorageGO = None
        self.__singleInput = None
        super(BustleFeedController, self).onDestroy()
        return

    @ifAppearanceReady
    def startBustleReload(self, shell, side):
        duration = self.__componentParams.activationTime
        self.__statesEvents.processReloadTriggered(shell, side, duration)

    @ifPlayerVehicle
    def tryActivate(self, _):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.SWITCH)
        self.cell.tryActivate()
        if not self.getMechanicState().isSwitchState():
            self.__shootingBlockTimestamp = BigWorld.time() + BigWorld.LatencyInfo().value[3]

    def _onAvatarReady(self, player):
        super(BustleFeedController, self)._onAvatarReady(player)
        if self.__singleInput is None:
            self.__singleInput = createMechanicSingleInput(self, profileName=self._INPUT_PROFILE_NAME, actionName=self._INPUT_ACTION_NAME, inputCallback=self.tryActivate)
        self.__updateVehicleGunReloadTime()
        return

    def _onAppearanceReady(self):
        super(BustleFeedController, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(BustleFeedController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__statesEvents.updateMechanicState(self.getMechanicState())
        self.__updateVehicleGunReloadTime()

    def _onComponentAvatarUpdate(self, player):
        super(BustleFeedController, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    def _collectComponentParams(self, typeDescriptor):
        super(BustleFeedController, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        self.__componentParams = BustleFeedComponentParams.fromMechanicParams(mechanicParams, typeDescriptor)

    @ifObservedVehicle
    def __updateVehicleGunReloadTime(self, player, _):
        if self.reloadStatus is not None:
            vehicleID = self.entity.id
            if self.reloadStatus.timeLeft == -2.0:
                timeLeft = self.reloadStatus.timeLeft
            else:
                timeLeft = max(0.0, self.reloadStatus.endTime - BigWorld.serverTime())
            player.updateVehicleGunReloadTime(vehicleID, timeLeft, self.reloadStatus.baseTime)
        return

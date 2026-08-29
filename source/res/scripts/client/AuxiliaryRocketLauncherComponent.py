# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AuxiliaryRocketLauncherComponent.py
from __future__ import absolute_import, division
import typing
from constants import SECONDARY_GUN_STATE
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.component_wrappers import ifPlayerVehicle
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.gun_mechanics.auxiliary_rocket_launcher import createAuxiliaryRocketLauncherStatesEvents, AuxiliaryRocketLauncherState, AuxiliaryRocketLauncherAmmoState
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_inputs import createAuxiliaryRocketLauncherInput
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

@ReprInjector.withParent()
class AuxiliaryRocketLauncherComponent(VehicleDynamicComponent, IGunMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):
    _SWITCH_MODE_INPUT_PROFILE_NAME = 'ABILITY_0_INPUT_PROFILE'
    _SWITCH_MODE_INPUT_ACTION_NAME = 'ABILITY_0_INPUT_ACTION'
    _ACTIVATE_INPUT_PROFILE_NAME = 'ARL_ACTIVATE_INPUT_PROFILE'
    _ACTIVATE_INPUT_ACTION_NAME = 'ARL_ACTIVATE_INPUT_ACTION'

    def __init__(self):
        super(AuxiliaryRocketLauncherComponent, self).__init__()
        self.__isInAimingMode = False
        self.__mechanicInput = None
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createAuxiliaryRocketLauncherStatesEvents(self)
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.AUXILIARY_ROCKET_LAUNCHER

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    @property
    def isInAimingMode(self):
        return self.__isInAimingMode

    def getMechanicState(self):
        state = SECONDARY_GUN_STATE.IDLE
        baseTime = 0.0
        endTime = -1.0
        if self.status:
            state = self.status.state
            baseTime = self.status.baseTime
            endTime = self.status.endTime
        isReloaded = bool(self.visualStatus.isReloaded)
        reloadStartTime = self.visualStatus.reloadStartTime
        return AuxiliaryRocketLauncherState(self.gunInstallationIndex, state, baseTime, endTime, isReloaded, reloadStartTime, self.__isInAimingMode)

    def getGunInstallationIndex(self):
        return self.gunInstallationIndex

    def set_status(self, _):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    def set_visualStatus(self, _):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        self.__mechanicInput = None
        super(AuxiliaryRocketLauncherComponent, self).onDestroy()
        return

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = AuxiliaryRocketLauncherAmmoState(self.__isInAimingMode)

    def _onAvatarReady(self, player):
        super(AuxiliaryRocketLauncherComponent, self)._onAvatarReady(player)
        if self.__mechanicInput is None:
            self.__mechanicInput = createAuxiliaryRocketLauncherInput(self, switchModeProfileName=self._SWITCH_MODE_INPUT_PROFILE_NAME, switchModeActionName=self._SWITCH_MODE_INPUT_ACTION_NAME, activateProfileName=self._ACTIVATE_INPUT_PROFILE_NAME, activateActionName=self._ACTIVATE_INPUT_ACTION_NAME, switchModeCallback=self.__switchAimingMode, activateCallback=self.__tryActivate)
        return

    def _onAppearanceReady(self):
        super(AuxiliaryRocketLauncherComponent, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(AuxiliaryRocketLauncherComponent, self)._onComponentAppearanceUpdate(**kwargs)
        self.__isInAimingMode = self.__isInAimingMode and self.getMechanicState().isValidForAimingMode()
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _onComponentAvatarUpdate(self, player):
        super(AuxiliaryRocketLauncherComponent, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    @ifPlayerVehicle
    def __switchAimingMode(self, player):
        self.__isInAimingMode = not self.__isInAimingMode
        self._updateComponentAppearance()
        self._updateComponentAvatar()
        if self.__isInAimingMode:
            player.cancelShootingCB()
            player.cancelChargeCB()

    def __tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.getMechanicState().state == SECONDARY_GUN_STATE.READY:
            self.cell.tryActivate()

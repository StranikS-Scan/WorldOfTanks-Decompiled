# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ShellParamsSwitcherController.py
from __future__ import absolute_import
import typing
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.gun_mechanics.shell_params_switcher import ShellParamsSwitcherMechanicState, ShellParamsSwitcherComponentParams, createShellParamsSwitcherStatesEvents, DEFAULT_SHELL_PARAMS_SWITCHER_PARAMS, DEFAULT_SHELL_PARAMS_SWITCHER_STATE, ShellParamsSwitcherAmmoState
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
    from vehicles.mechanics.gun_mechanics.shell_params_switcher import IShellParamsSwitcherMechanicState, IShellParamsSwitcherComponentParams

@ReprInjector.withParent()
class ShellParamsSwitcherController(VehicleDynamicComponent, IGunMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):

    def __init__(self):
        super(ShellParamsSwitcherController, self).__init__()
        self.__currentShellCD = None
        self.__componentParams = DEFAULT_SHELL_PARAMS_SWITCHER_PARAMS
        self.__mechanicState = DEFAULT_SHELL_PARAMS_SWITCHER_STATE
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__statesEvents = createShellParamsSwitcherStatesEvents(self)
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self._initComponent()
        return

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = ShellParamsSwitcherAmmoState(self.getMechanicState(), self.__componentParams.shellSubtypes.keys())

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.SHELL_PARAMS_SWITCHER

    @property
    def statesEvents(self):
        return self.__statesEvents

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    def getComponentParams(self):
        return self.__componentParams

    def getMechanicState(self):
        return self.__mechanicState

    def set_publicStatus(self, _):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    def set_status(self, _):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    @eventHandler
    def onCurrentShellChanged(self, intCD):
        self.__currentShellCD = intCD
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__statesEvents.destroy()
        self.__commandsEvents.destroy()
        super(ShellParamsSwitcherController, self).onDestroy()

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)

    def _collectComponentParams(self, typeDescriptor):
        super(ShellParamsSwitcherController, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        self.__componentParams = ShellParamsSwitcherComponentParams.fromMechanicParams(mechanicParams, typeDescriptor.type.compactDescr)

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(ShellParamsSwitcherController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateMechanicState()
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _onAppearanceReady(self):
        super(ShellParamsSwitcherController, self)._onAppearanceReady()
        self.__updateMechanicState()
        self.__statesEvents.processStatePrepared()

    def _onComponentAvatarUpdate(self, player):
        super(ShellParamsSwitcherController, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    def __updateMechanicState(self):
        shellCD = self.__currentShellCD
        self.__mechanicState = ShellParamsSwitcherMechanicState.fromComponentStatus(self.status, self.publicStatus, self.getComponentParams(), shellCD) if self.status is not None and self.publicStatus is not None else DEFAULT_SHELL_PARAMS_SWITCHER_STATE
        return

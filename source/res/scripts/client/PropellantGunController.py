# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PropellantGunController.py
from __future__ import absolute_import
import typing
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.component_wrappers import ifPlayerVehicle
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.gun_mechanics.propellant_gun import DEFAULT_PROPELLANT_GUN_PARAMS, DEFAULT_PROPELLANT_GUN_MECHANIC_STATE, PropellantGunMechanicState, PropellantGunComponentParams, createPropellantStatesEvents
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
    from vehicles.mechanics.gun_mechanics.propellant_gun import IPropellantGunComponentParams, IPropellantGunMechanicState

@ReprInjector.withParent()
class PropellantGunController(VehicleDynamicComponent, IGunMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):

    def __init__(self):
        super(PropellantGunController, self).__init__()
        self.__componentParams = DEFAULT_PROPELLANT_GUN_PARAMS
        self.__mechanicState = DEFAULT_PROPELLANT_GUN_MECHANIC_STATE
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__statesEvents = createPropellantStatesEvents(self)
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__isForbiddenShell = None
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.PROPELLANT_GUN

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getComponentParams(self):
        return self.__componentParams

    def getMechanicState(self):
        return self.__mechanicState

    def set_status(self, _=None):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__statesEvents.destroy()
        self.__commandsEvents.destroy()
        super(PropellantGunController, self).onDestroy()

    @eventHandler
    @ifPlayerVehicle
    def onCurrentShellChanged(self, _, intCD):
        self.__isForbiddenShell = intCD in self.__componentParams.forbiddenShells
        self._updateComponentAppearance()

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.__mechanicState.isAvailable:
            self.cell.switchOvercharge()

    def _onAppearanceReady(self):
        super(PropellantGunController, self)._onAppearanceReady()
        self.__updateMechanicState()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(PropellantGunController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateMechanicState()
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _collectComponentParams(self, typeDescriptor):
        super(PropellantGunController, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        self.__componentParams = PropellantGunComponentParams.fromMechanicParams(mechanicParams)

    def __updateMechanicState(self):
        self.__mechanicState = PropellantGunMechanicState.fromComponentStatus(self.status, self.__componentParams, isForbiddenShell=self.__isForbiddenShell) if self.status is not None else DEFAULT_PROPELLANT_GUN_MECHANIC_STATE
        return

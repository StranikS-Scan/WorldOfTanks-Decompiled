# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SpecBoostModeComponent.py
from __future__ import absolute_import, division
import typing
from constants import PHASED_MECHANIC_STATE
from gui.shared.utils.decorators import ReprInjector
from items.vehicle_mechanics_types import VehicleMechanic, VehicleMechanicKey, SpecBoostModeMechanicVariant
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.generic_mechanics.spec_boost_mode import ISpecBoostModeMechanicParams, ISpecBoostModeMechanicState, SpecBoostModeMechanicState, SpecBoostModeMechanicParams, DEFAULT_SPEC_BOOST_MODE_STATE, DEFAULT_SPEC_BOOST_MODE_PARAMS
from vehicles.mechanics.mechanic_commands import createMechanicCommandsEvents, IMechanicCommandsComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent, createMechanicStatesEvents
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

@ReprInjector.withParent()
class SpecBoostModeComponent(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):

    def __init__(self):
        super(SpecBoostModeComponent, self).__init__()
        self.__componentParams = DEFAULT_SPEC_BOOST_MODE_PARAMS
        self.__mechanicState = DEFAULT_SPEC_BOOST_MODE_STATE
        self.__commandsEvents = createMechanicCommandsEvents(self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self._initComponent()

    @property
    def vehicleMechanicKey(self):
        return VehicleMechanicKey(VehicleMechanic.SPEC_BOOST_MODE, SpecBoostModeMechanicVariant.fromString(self.mechanicVariant))

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

    def set_status(self, _):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(SpecBoostModeComponent, self).onDestroy()

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.getMechanicState().state == PHASED_MECHANIC_STATE.READY:
            self.cell.tryActivate()

    def _collectComponentParams(self, typeDescriptor):
        super(SpecBoostModeComponent, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanicKey)
        self.__componentParams = SpecBoostModeMechanicParams.fromMechanicParams(mechanicParams)

    def _onAppearanceReady(self):
        super(SpecBoostModeComponent, self)._onAppearanceReady()
        self.__updateMechanicState()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(SpecBoostModeComponent, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateMechanicState()
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def __updateMechanicState(self):
        self.__mechanicState = SpecBoostModeMechanicState.fromComponentStatus(self.status) if self.status is not None else DEFAULT_SPEC_BOOST_MODE_STATE
        return

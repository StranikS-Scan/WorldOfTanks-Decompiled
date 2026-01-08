# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TemperatureGunController.py
import typing
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.gun_mechanics.temperature.common import createTemperatureStatesEvents
from vehicles.mechanics.gun_mechanics.temperature.temperature_gun import DEFAULT_TEMPERATURE_COMPONENT_PARAMS, DEFAULT_TEMPERATURE_MECHANIC_STATE, TemperatureGunComponentParams, TemperatureGunMechanicState, TemperatureGunAmmoState
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
if typing.TYPE_CHECKING:
    from vehicles.mechanics.gun_mechanics.temperature.temperature_gun import ITemperatureGunComponentParams, ITemperatureGunMechanicState
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

@ReprInjector.withParent()
class TemperatureGunController(VehicleDynamicComponent, IGunMechanicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(TemperatureGunController, self).__init__()
        self.__componentParams = DEFAULT_TEMPERATURE_COMPONENT_PARAMS
        self.__mechanicState = DEFAULT_TEMPERATURE_MECHANIC_STATE
        self.__statesEvents = createTemperatureStatesEvents(self)
        self._initComponent()

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = TemperatureGunAmmoState(self.__mechanicState)

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.TEMPERATURE_GUN

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getComponentParams(self):
        return self.__componentParams

    def getMechanicState(self):
        return self.__mechanicState

    def set_stateStatus(self, _=None):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(TemperatureGunController, self).onDestroy()

    def _onAppearanceReady(self):
        super(TemperatureGunController, self)._onAppearanceReady()
        self.__updateMechanicState()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(TemperatureGunController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateMechanicState()
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _onComponentAvatarUpdate(self, player):
        super(TemperatureGunController, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    def _collectComponentParams(self, typeDescriptor):
        super(TemperatureGunController, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        self.__componentParams = TemperatureGunComponentParams.fromMechanicParams(mechanicParams)

    def __updateMechanicState(self):
        self.__mechanicState = TemperatureGunMechanicState.fromComponentStatus(self.stateStatus, self.__componentParams) if self.stateStatus is not None else DEFAULT_TEMPERATURE_MECHANIC_STATE
        return

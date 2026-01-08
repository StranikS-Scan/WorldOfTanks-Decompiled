# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/OverheatGunComponent.py
import typing
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.gun_mechanics.temperature.overheat_gun import DEFAULT_OVERHEAT_MECHANIC_STATE, DEFAULT_OVERHEAT_COMPONENT_PARAMS, OverheatGunComponentParams, OverheatGunMechanicState, OverheatGunAmmoState
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicStatesComponent
if typing.TYPE_CHECKING:
    from vehicles.mechanics.gun_mechanics.temperature.overheat_gun import IOverheatGunComponentParams, IOverheatGunMechanicState
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents

@ReprInjector.withParent()
class OverheatGunComponent(VehicleDynamicComponent, IGunMechanicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(OverheatGunComponent, self).__init__()
        self.__componentParams = DEFAULT_OVERHEAT_COMPONENT_PARAMS
        self.__mechanicState = DEFAULT_OVERHEAT_MECHANIC_STATE
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = OverheatGunAmmoState(self.__mechanicState)

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.OVERHEAT_GUN

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getComponentParams(self):
        return self.__componentParams

    def getMechanicState(self):
        return self.__mechanicState

    def set_state(self, _=None):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(OverheatGunComponent, self).onDestroy()

    def _onAppearanceReady(self):
        super(OverheatGunComponent, self)._onAppearanceReady()
        self.__updateMechanicState()
        self.__mechanicPrefabSpawner.loadAppearancePrefab()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(OverheatGunComponent, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateMechanicState()
        self.__statesEvents.updateMechanicState(self.getMechanicState())

    def _onComponentAvatarUpdate(self, player):
        super(OverheatGunComponent, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    def _collectComponentParams(self, typeDescriptor):
        super(OverheatGunComponent, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        self.__componentParams = OverheatGunComponentParams.fromMechanicParams(mechanicParams)

    def __updateMechanicState(self):
        self.__mechanicState = OverheatGunMechanicState.fromComponentStatus(self.state, self.__componentParams)

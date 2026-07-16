# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LowChargeShotController.py
from __future__ import absolute_import
import typing
from constants import LowChargeShotReloadingState
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from math_utils import almostEqual
from vehicles.components.component_wrappers import ifObservedVehicle
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import createMechanicStatesEvents, IMechanicStatesComponent
from vehicles.mechanics.gun_mechanics.low_charge_shot.private import LowChargeShotAmmoState, LowChargeShotMechanicState, LowChargeShotUILogging, DEFAULT_MECHANIC_STATE
if typing.TYPE_CHECKING:
    from items.components.shared_components import LowChargeShotParams

@ReprInjector.withParent()
class LowChargeShotController(VehicleDynamicComponent, IGunMechanicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(LowChargeShotController, self).__init__()
        self.__params = None
        self.__prevBaseTime = 0.0
        self.__mechanicState = DEFAULT_MECHANIC_STATE
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__uiLogging = LowChargeShotUILogging()
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.LOW_CHARGE_SHOT

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getComponentParams(self):
        return self.__params

    def getMechanicState(self):
        return self.__mechanicState

    def set_stateStatus(self, _=None):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(LowChargeShotController, self).onDestroy()

    @eventHandler
    def onObserverVehicleDataUpdated(self):
        self.__statesEvents.updateMechanicState(self.getMechanicState())
        self.__updateVehicleGunReloadTime()

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = LowChargeShotAmmoState(self.getMechanicState())

    @eventHandler
    def onCollectVehicleAttrs(self, vehAttrs):
        vehAttrs['{}/gunShotsSpeed'.format(VehicleMechanic.LOW_CHARGE_SHOT.value)] = self.gunShotsSpeedOverride

    def _onAppearanceReady(self):
        super(LowChargeShotController, self)._onAppearanceReady()
        self.__updateMechanicState()
        self.__statesEvents.processStatePrepared()

    def _onAvatarReady(self, player):
        super(LowChargeShotController, self)._onAvatarReady(player)
        self.__uiLogging.subscribe(self, player.arenaUniqueID)

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(LowChargeShotController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateMechanicState()
        self.__statesEvents.updateMechanicState(self.getMechanicState())
        self.__updateVehicleGunReloadTime()

    def _onComponentAvatarUpdate(self, player):
        super(LowChargeShotController, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    def _collectComponentParams(self, typeDescriptor):
        super(LowChargeShotController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)

    def __updateMechanicState(self):
        self.__prevBaseTime = self.__mechanicState.baseTime
        self.__mechanicState = LowChargeShotMechanicState.fromComponentStatus(self.stateStatus, self.__params) if self.stateStatus is not None else DEFAULT_MECHANIC_STATE
        return

    @ifObservedVehicle
    def __updateVehicleGunReloadTime(self, player, _):
        vehicleID = self.entity.id
        mechanicState = self.getMechanicState()
        if mechanicState.reloadingState == LowChargeShotReloadingState.EMPTY:
            player.updateVehicleGunReloadTime(vehicleID, -1, mechanicState.baseTime)
        elif mechanicState.reloadingState == LowChargeShotReloadingState.FULL_CHARGE:
            player.updateVehicleGunReloadTime(vehicleID, 0, mechanicState.baseTime)
        elif mechanicState.reloadingState in (LowChargeShotReloadingState.INITIAL_RELOAD, LowChargeShotReloadingState.LOW_CHARGE) or not almostEqual(self.__prevBaseTime, mechanicState.baseTime):
            player.updateVehicleGunReloadTime(vehicleID, mechanicState.calculateTimeLeft(), mechanicState.baseTime)

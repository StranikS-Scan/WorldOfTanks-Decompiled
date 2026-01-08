# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ChargeableBurstComponent.py
import typing
from collections import namedtuple
from events_handler import eventHandler
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents, IMechanicStatesEvents

class ChargeableBurstAmmoState(DefaultComponentAmmoState):

    def __init__(self, isBurstActive, shots, burstCount):
        super(ChargeableBurstAmmoState, self).__init__()
        self.__isBurstActive = isBurstActive
        self.__burstCount = burstCount
        self.__shots = shots

    @property
    def isBurstActive(self):
        return self.__isBurstActive

    @property
    def burstCount(self):
        return self.__burstCount

    @property
    def shots(self):
        return self.__shots


@ReprInjector.simple('isBurstActive', 'charges', 'shots')
class ChargeableBurstModeState(namedtuple('ChargeableBurstModeState', ('isBurstActive', 'charges', 'shots', 'penetrationCount', 'burstCount')), IMechanicState):

    def isTransition(self, other):
        return self.isBurstActive != other.isBurstActive


@ReprInjector.withParent()
class ChargeableBurstComponent(VehicleDynamicComponent, IGunMechanicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(ChargeableBurstComponent, self).__init__()
        self.__penetrationCount = 0
        self.__burstCount = 0
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.CHARGEABLE_BURST

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getComponentParams(self):
        return (self.__penetrationCount, self.__burstCount)

    def getMechanicState(self):
        return ChargeableBurstModeState(self.isBurstActive, self.charges, self.shots, self.__penetrationCount, self.__burstCount)

    def set_charges(self, prev):
        self._updateComponentAppearance()

    def set_shots(self, prev):
        self._updateComponentAppearance()

    def set_isBurstActive(self, prev):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(ChargeableBurstComponent, self).onDestroy()

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = ChargeableBurstAmmoState(self.isBurstActive, self.shots, self.__burstCount)

    def _onAppearanceReady(self):
        super(ChargeableBurstComponent, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(ChargeableBurstComponent, self)._onComponentAppearanceUpdate(**kwargs)
        mechanicState = self.getMechanicState()
        self.__statesEvents.updateMechanicState(mechanicState)

    def _onComponentAvatarUpdate(self, player):
        super(ChargeableBurstComponent, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    def _collectComponentParams(self, typeDescriptor):
        super(ChargeableBurstComponent, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        self.__penetrationCount = mechanicParams.penetrationCount
        self.__burstCount, _, _ = typeDescriptor.gun.burst

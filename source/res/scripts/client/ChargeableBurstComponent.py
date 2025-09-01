# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ChargeableBurstComponent.py
import typing
from collections import namedtuple
from vehicles.components.vehicle_component import VehicleDynamicComponent
from items.components.shared_components import ChargeableBurstParams
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents, IMechanicStatesEvents
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor

class ChargeableBurstModeState(namedtuple('ChargeableBurstModeState', ('isBurstActive', 'charges', 'shoots', 'penetrationCount', 'burstCount')), IMechanicState):

    def isTransition(self, other):
        return self.isBurstActive != other.isBurstActive


class ChargeableBurstComponent(VehicleDynamicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(ChargeableBurstComponent, self).__init__()
        self.__penetrationCount = 0
        self.__burstCount = 0
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return ChargeableBurstModeState(self.isBurstActive, self.charges, self.shoots, self.__penetrationCount, self.__burstCount)

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(ChargeableBurstComponent, self).onDestroy()

    def _onAppearanceReady(self):
        typeDescriptor = self.entity.typeDescriptor
        mechanicParams = typeDescriptor.mechanicsParams[ChargeableBurstParams.MECHANICS_NAME]
        self.__penetrationCount = mechanicParams.penetrationCount
        self.__burstCount, _ = typeDescriptor.gun.burst
        self.__statesEvents.processStatePrepared()
        super(ChargeableBurstComponent, self)._onAppearanceReady()

    def _onComponentAvatarUpdate(self, player):
        if self.entity.isDestroyed:
            return
        ammoCtrl = self.entity.guiSessionProvider.shared.ammo
        ammoCtrl.setBurstActive(self.isBurstActive)

    def _onComponentAppearanceUpdate(self):
        mechanicState = self.getMechanicState()
        self.__statesEvents.updateMechanicState(mechanicState)

    def set_charges(self, prev):
        self._updateComponentAppearance()

    def set_shoots(self, prev):
        self._updateComponentAppearance()

    def set_isBurstActive(self, prev):
        self._updateComponentAvatar()
        self._updateComponentAppearance()

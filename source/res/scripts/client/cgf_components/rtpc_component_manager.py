# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/rtpc_component_manager.py
import CGF
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from Sound import RTPCComponent
from Vehicular import KineticEnergyGetter, RemainingAmmoClipPercentGetter, OverheatValueGetter
from constants import IS_CLIENT
if IS_CLIENT:
    from Vehicle import Vehicle
else:

    class Vehicle(object):
        pass


class RTPCSourceType(object):
    VALUE = 0
    KINETIC_ENERGY = 1
    INTERVAL_BETWEEN_SHOTS = 2
    REMAINIG_AMMO_CLIP_PERCENT = 3
    OVERHEAT_VALUE = 4
    COUNT = 5


@autoregister(presentInAllWorlds=True)
class RTPCComponentManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RTPCComponentManager, self).__init__()
        self.__rtpcGameObjectToVehicleGameObject = {}

    def getVehicleComponentForRTPC(self, rtpcGameObject):
        vehicleGameObject = self.__rtpcGameObjectToVehicleGameObject.get(rtpcGameObject.id, None)
        return vehicleGameObject.findComponentByType(Vehicle) if vehicleGameObject is not None else None

    @onAddedQuery(CGF.GameObject, RTPCComponent, tickGroup='preInitGroup')
    def onRTPCAdded(self, gameObject, _):
        hierarchy = CGF.HierarchyManager(gameObject.spaceID)
        findResult = hierarchy.findComponentInParent(gameObject, Vehicle)
        if not findResult:
            return
        self.__rtpcGameObjectToVehicleGameObject[gameObject.id] = findResult[0]

    @onRemovedQuery(CGF.GameObject, RTPCComponent)
    def onRTPCRemoved(self, gameObject, _):
        self.__rtpcGameObjectToVehicleGameObject.pop(gameObject.id, None)
        return

    @onAddedQuery(CGF.GameObject, RTPCComponent, KineticEnergyGetter)
    def onKineticEnergyRTPCAdded(self, gameObject, rtpcComponent, _):
        vehicle = self.getVehicleComponentForRTPC(gameObject)
        if vehicle is not None and vehicle.appearance is not None:
            rtpcComponent.setRTPCsBySourceType(RTPCSourceType.KINETIC_ENERGY, vehicle.appearance.weaponEnergy)
        return

    @onProcessQuery(CGF.GameObject, RTPCComponent, RemainingAmmoClipPercentGetter, updatePeriod=0.2)
    def onRemainAmmoClipPercentRTPCProcess(self, gameObject, rtpcComponent, _):
        vehicle = self.getVehicleComponentForRTPC(gameObject)
        if vehicle is not None and vehicle.isPlayerVehicle:
            ammo = self.__sessionProvider.shared.ammo
            clipPercent = ammo.getClipPercentLeft() * 100 if ammo is not None else 0.0
            rtpcComponent.setRTPCsBySourceType(RTPCSourceType.REMAINIG_AMMO_CLIP_PERCENT, clipPercent)
        return

    @onProcessQuery(CGF.GameObject, RTPCComponent, OverheatValueGetter)
    def onOverheatValueRTPCAdded(self, gameObject, rtpcComponent, _):
        vehicle = self.getVehicleComponentForRTPC(gameObject)
        if vehicle is None:
            return
        else:
            temperatureGunController = vehicle.dynamicComponents.get('temperatureGunController')
            if temperatureGunController is not None:
                rtpcComponent.setRTPCsBySourceType(RTPCSourceType.OVERHEAT_VALUE, vehicle.temperatureGunController.temperatureProgress)
            return

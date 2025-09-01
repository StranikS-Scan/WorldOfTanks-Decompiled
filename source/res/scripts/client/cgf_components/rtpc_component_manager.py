# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/rtpc_component_manager.py
import typing
import CGF
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from Sound import RTPCComponent
from Vehicular import RemainingAmmoClipPercentGetter
from cgf_common.cgf_helpers import getVehicleGameObjectByGameObject, getVehicleEntityByVehicleGameObject

class RTPCSourceType(object):
    VALUE = 0
    INTERVAL_BETWEEN_SHOTS = 2
    REMAINIG_AMMO_CLIP_PERCENT = 3
    DISTANCE_TO_CANNON = 4


@autoregister(presentInAllWorlds=True)
class RTPCComponentManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RTPCComponentManager, self).__init__()
        self.__rtpcGameObjectToVehicleGameObject = {}

    def deactivate(self):
        self.__rtpcGameObjectToVehicleGameObject.clear()

    def getVehicleComponentForRTPC(self, rtpcGameObject):
        vehicleGameObject = self.__rtpcGameObjectToVehicleGameObject.get(rtpcGameObject.id)
        return getVehicleEntityByVehicleGameObject(vehicleGameObject) if vehicleGameObject is not None else None

    @onAddedQuery(CGF.GameObject, RTPCComponent, tickGroup='preInitGroup')
    def onRTPCAdded(self, gameObject, _):
        vehicleGameObject = getVehicleGameObjectByGameObject(gameObject)
        if vehicleGameObject is not None:
            self.__rtpcGameObjectToVehicleGameObject[gameObject.id] = vehicleGameObject
        return

    @onRemovedQuery(CGF.GameObject, RTPCComponent)
    def onRTPCRemoved(self, gameObject, _):
        self.__rtpcGameObjectToVehicleGameObject.pop(gameObject.id, None)
        return

    @onProcessQuery(CGF.GameObject, RTPCComponent, RemainingAmmoClipPercentGetter, period=0.2)
    def onRemainAmmoClipPercentRTPCProcess(self, gameObject, rtpcComponent, _):
        vehicle = self.getVehicleComponentForRTPC(gameObject)
        if vehicle is not None and vehicle.isPlayerVehicle:
            ammo = self.__sessionProvider.shared.ammo
            clipPercent = ammo.getClipPercentLeft() * 100 if ammo is not None else 0.0
            rtpcComponent.setRTPCsBySourceType(RTPCSourceType.REMAINIG_AMMO_CLIP_PERCENT, clipPercent)
        return

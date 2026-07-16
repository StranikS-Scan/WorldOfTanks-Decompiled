# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/rtpc_component_manager.py
from __future__ import absolute_import
import typing
import CGF
from constants import IS_EDITOR, IS_CGF_DUMP
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from Sound import RTPCComponent, RTPCSourceType
from Vehicular import RemainingAmmoClipPercentGetter
from cgf_common.cgf_helpers import getVehicleEntityByVehicleGameObject
if IS_EDITOR or IS_CGF_DUMP:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle

class RTPCComponentSystem(CGF.System):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    RTCPActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(RTPCComponent))
    RTCPDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRw(RTPCComponent))
    RTCPIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Rw(RTPCComponent), CGF.Has(RemainingAmmoClipPercentGetter))
    VehicleAccess = CGF.AccessReaction(Vehicle)
    Reactions = CGF.Reactions(RTCPActivated, RTCPDeactivated, RTCPIterate, VehicleAccess)

    def update(self):
        vehicleAccess = self.reaction(self.VehicleAccess)
        for go, _ in self.reaction(self.RTCPDeactivated):
            self.__rtpcGameObjectToVehicleGameObject.pop(go, None)

        for go, rtpc in self.reaction(self.RTCPActivated):
            vehicle = CGF.findParentWithReaction(go, vehicleAccess)
            if vehicle is not None:
                self.__rtpcGameObjectToVehicleGameObject[go] = vehicle.object

        for go, rtpc in self.reaction(self.RTCPIterate):
            vehicle = self.getVehicleComponentForRTPC(go)
            if vehicle is not None and vehicle.isPlayerVehicle:
                ammo = self.__sessionProvider.shared.ammo
                clipPercent = ammo.getClipPercentLeft() * 100 if ammo is not None else 0.0
                rtpc.setRTPCsBySourceType(RTPCSourceType.REMAINING_AMMO_CLIP_PERCENT, clipPercent)

        return

    def __init__(self):
        super(RTPCComponentSystem, self).__init__()
        self.__rtpcGameObjectToVehicleGameObject = {}

    def onMappingUnloaded(self):
        self.__rtpcGameObjectToVehicleGameObject.clear()

    def getVehicleComponentForRTPC(self, rtpcGameObject):
        vehicleGameObject = self.__rtpcGameObjectToVehicleGameObject.get(rtpcGameObject)
        return getVehicleEntityByVehicleGameObject(vehicleGameObject) if vehicleGameObject is not None else None

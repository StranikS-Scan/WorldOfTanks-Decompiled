# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/vehicle_components/nitro.py
from __future__ import absolute_import
import enum
import logging
import typing
import CGF
from constants import IS_EDITOR, IS_CGF_DUMP
from cgf_script.registration import ComponentProperty, registerComponent
from cgf_modules.variable_components import VariableStorageComponent
from CustomEffectManager import CustomEffectManager
if typing.TYPE_CHECKING:
    from typing import Optional
    from Vehicle import Vehicle
    VehAccessorType = typing.Union[Vehicle, CGF.ComponentAccessor[Vehicle]]
    EffectMgrAccessorType = typing.Union[CustomEffectManager, CGF.ComponentAccessor[CustomEffectManager]]
    VarStorageType = typing.Union[VariableStorageComponent, CGF.ComponentAccessor[VariableStorageComponent]]
elif IS_EDITOR or IS_CGF_DUMP:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle
logger = logging.getLogger(__name__)
NITRO_COUNT_KEY = 'vehicle/nitro/count'

@enum.unique
class NitroExhaustEffect(enum.IntEnum):
    NO_NITRO = 0
    BR_NITRO = 1
    FORSAGE_GAS = 2
    FORSAGE_DIESEL = 3


@registerComponent
class VehicleNitroExhaustEffectComponent(object):
    category = 'Vehicle'
    editorTitle = 'Nitro Exhaust Effect'
    domain = CGF.Domain.ClientEditor
    effect = ComponentProperty(type=CGF.PropertyType.Int, editorName='Effect Name', annotations={'comboBox': {n.name:str(n.value) for n in list(NitroExhaustEffect)}}, value=NitroExhaustEffect.FORSAGE_GAS.value)

    def __init__(self):
        self.vehicleGoUUID = CGF.INVALID_UUID
        self.effectMgrGoUUID = CGF.INVALID_UUID
        logger.debug('Created %s.', self)

    def initialize(self, vehGO, effectMgrGo):
        self.vehicleGoUUID = vehGO.uuid
        self.effectMgrGoUUID = effectMgrGo.uuid
        logger.debug('Initialized %s.', self)

    def clear(self):
        self.vehicleGoUUID = CGF.INVALID_UUID
        self.effectMgrGoUUID = CGF.INVALID_UUID
        logger.debug('Cleared  %s.', self)

    def destroy(self):
        self.clear()
        logger.debug('Destroyed  %s.', self)

    def __repr__(self):
        return '<VehNitroEffectComponent|{}>'.format((self.effect, self.vehicleGoUUID, self.effectMgrGoUUID))


class VehicleNitroExhaustEffectComponentSystem(CGF.System):
    NitroActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(VehicleNitroExhaustEffectComponent))
    NitroDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRw(VehicleNitroExhaustEffectComponent))
    NitroRemoved = CGF.RemoveReaction(CGF.ReactRw(VehicleNitroExhaustEffectComponent))
    VehicleVarAccess = CGF.AccessReaction(CGF.GameObject, CGF.Rw(Vehicle), CGF.Rw(VariableStorageComponent))
    EffectMgrAccess = CGF.AccessReaction(CGF.GameObject, CGF.Rw(CustomEffectManager))
    Reactions = CGF.Reactions(NitroRemoved, NitroDeactivated, NitroActivated, VehicleVarAccess, EffectMgrAccess)

    def update(self):
        nitroRemoved, nitroDeactivated, nitroActivated, vehVarAccess, effectMgrAccess = self.reactions
        for go, comp in nitroDeactivated:
            self._onNitroDeactivated(go, comp, vehVarAccess, effectMgrAccess)

        for comp in nitroRemoved:
            comp.clear()

        for go, comp in nitroActivated:
            self._onNitroActivated(go, comp, vehVarAccess, effectMgrAccess)

    def _onNitroActivated(self, go, component, vehVarAccess, effectMgrAccess):
        vehResult = CGF.findParentWithReaction(go, vehVarAccess)
        if vehResult is None:
            logger.warning('[NitroEffect:%s] Activate. Vehicle lookup failed.', go.id)
            return
        else:
            vehGo, veh, varStorage = vehResult
            if not self._isVehicleValid(veh):
                logger.warning('[NitroEffect:%s] Activate. Invalid vehicle returned from lookup.', go.id)
                return
            if not varStorage:
                logger.warning('[NitroEffect:%s] Activate. Missing var storage for vehicle<%s>.', go.id, veh.id)
                return
            effectMgrResult = CGF.findParentWithReaction(go, effectMgrAccess)
            if effectMgrResult is None:
                logger.warning('[NitroEffect:%s] Activate. Effect manager lookup failed for vehicle<%s>.', go.id, veh.id)
                return
            effectMgrGo, effectMgr = effectMgrResult
            if not effectMgr:
                logger.warning('[NitroEffect:%s] Activate. Effect manager accessor is missing for vehicle<%s>.', go.id, veh.id)
                return
            component.initialize(vehGo, effectMgrGo)
            self._changeAppliedNitroCount(vehGo, varStorage, 1)
            self._setNitroEffect(effectMgr, component.effect)
            logger.debug('[NitroEffect:%s] Activated. Veh<%s>, effect<%s>.', go.id, veh.id, component.effect)
            return

    def _onNitroDeactivated(self, go, component, vehVarAccess, effectMgrAccess):
        vehicleGoUUID = component.vehicleGoUUID
        effectMgrGoUUID = component.effectMgrGoUUID
        component.clear()
        vehGo, vehicle, varStorage = vehVarAccess.find(vehicleGoUUID)
        if not self._isVehicleValid(vehicle) or not varStorage:
            appliedNitroCount = 0
            logger.debug('[NitroEffect:%s] Deactivate. No vehicle.', go.id)
        else:
            appliedNitroCount = self._changeAppliedNitroCount(vehGo, varStorage, -1)
        _, effectMgr = effectMgrAccess.find(effectMgrGoUUID)
        if not effectMgr:
            logger.debug('[NitroEffect:%s] Deactivate. No effect mrg no vehicle.', go.id)
            return
        if appliedNitroCount <= 0:
            self._setNitroEffect(effectMgr, NitroExhaustEffect.NO_NITRO.value)
        logger.debug('[NitroEffect:%s] Deactivated.', go.id)

    @staticmethod
    def _setNitroEffect(effectMgr, nitro):
        effectMgr.variables['Nitro'] = nitro
        logger.debug('Nitro effect was set: nitro=%s', nitro)

    @staticmethod
    def _changeAppliedNitroCount(vehGo, varStorage, value):
        prevCount = varStorage.getVarVal(NITRO_COUNT_KEY) or 0
        newCount = max(prevCount + value, 0)
        varStorage.modify(vehGo, NITRO_COUNT_KEY, newCount)
        logger.debug('Nitro applied count was changed: prev=%s, new=%s.', prevCount, newCount)
        return newCount

    @staticmethod
    def _isVehicleValid(vehicle):
        return bool(vehicle) and not vehicle.isDestroyed

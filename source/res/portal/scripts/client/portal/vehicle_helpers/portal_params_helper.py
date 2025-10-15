# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/vehicle_helpers/portal_params_helper.py
import typing
from collections import Iterable
from itertools import izip_longest
from helpers import dependency
from portal.skeletons.portal_event_controller import IPortalEventController
from portal.gui.impl.gen.view_models.views.lobby.params_ttx_model import TtxComparisonStatus
if typing.TYPE_CHECKING:
    from typing import Optional, List
COMMON_PARAMS = ('maxHealth', 'avgDamage', 'hullArmor', 'avgPiercingPower', 'turretArmor', 'aimingTime', 'turretRotationSpeed', 'shotDispersionAngle', 'chassisRotationSpeed', 'avgDamagePerMinute', 'enginePower', 'speedLimits')
CLASSIC_GUN_PARAMS = ('reloadTime', 'reloadTimeSecs')
AUTORELOAD_GUN_PARAMS = ('clipFireRate', 'autoReloadTime')
DUAL_GUN_PARAMS = ('clipFireRate', 'reloadTimeSecs')
CLIP_GUN_PARAMS = ('clipFireRate', 'autoReloadTime', 'reloadTime')
INVERTED_PARAMS = ('reloadTimeSecs', 'clipFireRate', 'autoReloadTime', 'aimingTime', 'shotDispersionAngle')
MODIFIER_TO_FACTOR = {'gun/reloadTime': 'gunReloadTimeFactor',
 'engine/power': 'enginePowerFactor',
 'damageFactor': 'damageFactor'}

class PortalParam(object):

    def __init__(self):
        self.name = None
        self.values = []
        return


class PortalParamValue(object):

    def __init__(self):
        self.value = None
        self.status = TtxComparisonStatus.DEFAULT
        return


class PortalParamsHelper(object):
    __portalController = dependency.descriptor(IPortalEventController)

    @staticmethod
    def getVehicleParams(vehicle):
        appliedModifiers = PortalParamsHelper.__portalController.getVehicleModifiers(vehicle)
        PortalParamsHelper.__applyModifiers(vehicle, appliedModifiers)
        gunParams = PortalParamsHelper.__getVehicleGunParams(vehicle.descriptor)
        neededParams = list(COMMON_PARAMS)
        allParamNames = vehicle.getParams()['parameters'].keys()
        insertPos = 0
        for param in gunParams:
            if param in allParamNames:
                neededParams.insert(len(COMMON_PARAMS) + 1 - insertPos * 2, param)
                insertPos += 1

        vehParams = {paramName:param for paramName, param in vehicle.getParams()['parameters'].iteritems() if paramName in neededParams}
        engineFwSpeed = vehicle.typeDescr.xphysics['engines'][vehicle.descriptor.engine.name]['smplFwMaxSpeed']
        vehParams['speedLimits'][0] = engineFwSpeed
        params = []
        for paramName in neededParams:
            paramValues = vehParams.get(paramName)
            if paramValues is None:
                continue
            param = PortalParam()
            param.name = paramName
            paramValues = tuple(paramValues) if isinstance(paramValues, Iterable) else (paramValues,)
            for paramValue in paramValues:
                value = PortalParamValue()
                value.value = paramValue
                param.values.append(value)

            params.append(param)

        vehicle.descriptor.rebuildAttrs()
        return params

    @staticmethod
    def getComparedParams(originalParams, comparedParams):
        for comparedParam in comparedParams:
            originalParam = [ param for param in originalParams if param.name == comparedParam.name ]
            originalValues = originalParam[0].values if originalParam else []
            for comparedValue, originalValue in izip_longest(comparedParam.values, originalValues):
                if comparedValue is None:
                    continue
                isInverse = comparedParam.name in INVERTED_PARAMS
                increaseStatus = TtxComparisonStatus.DECREASE if isInverse else TtxComparisonStatus.INCREASE
                decreaseStatus = TtxComparisonStatus.INCREASE if isInverse else TtxComparisonStatus.DECREASE
                if originalValue is not None and len(comparedParam.values) == len(originalValues):
                    if comparedValue.value > originalValue.value:
                        comparedValue.status = increaseStatus
                    elif comparedValue.value < originalValue.value:
                        comparedValue.status = decreaseStatus

        return comparedParams

    @staticmethod
    def applyModifiersAndGetParams(vehicle, modifiers):
        PortalParamsHelper.__applyModifiers(vehicle, modifiers)
        return PortalParamsHelper.getVehicleParams(vehicle)

    @staticmethod
    def __getVehicleGunParams(vehDescr):
        gunParams = CLASSIC_GUN_PARAMS
        if vehDescr.isDualgunVehicle:
            gunParams = DUAL_GUN_PARAMS
        elif vehDescr.isClipGun:
            gunParams = CLIP_GUN_PARAMS
        elif vehDescr.isAutoReloadGun:
            gunParams = AUTORELOAD_GUN_PARAMS
        return gunParams

    @staticmethod
    def __applyModifiers(vehicle, modifiers):
        attributes = vehicle.miscAttrs
        for modifier in modifiers:
            modType = modifier['type']
            modValue = modifier['modifier']
            attributes[MODIFIER_TO_FACTOR[modType]] *= modValue

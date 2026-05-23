# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/utils.py
from __future__ import absolute_import, division
import math
import typing
from collections import OrderedDict
from builtins import round
from future.utils import listvalues
import BigWorld
import GUI
import armor_inspector
import math_utils
from constants import VehicleArmorTags, VehicleTurretTags
from AvatarInputHandler import cameras
from Vehicle import SegmentCollisionResultExt
from account_helpers.AccountSettings import AccountSettings, AttackerVehicleConfiguration
from account_helpers.settings_core.settings_constants import ArmorInspector as ArmorInspectorSettingsKeys
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_value_model import ArmorValueModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_model import MinorShortTooltipTypes
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config import getConfig
from items import vehicles
from shared_utils.vehicle_utils import getMatinfo
from vehicle_systems.tankStructure import TankPartIndexes
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_model import ArmorModel
    from HangarVehicle import HangarVehicle
    from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config.models import ArmorScaleModel
    from frameworks.wulf import Array
    from items.vehicles import VehicleDescriptor
    from typing import Optional
    from gui.impl.lobby.vehicle_hub.sub_presenters.armor.penetration_utils import ShellParams
    MatInfo = typing.Tuple[int, float, float, int]
MIN_HIT_ANGLE_COS = 1e-05
COLLISION_RAY_LENGTH = 1500
RAD_TO_DEG = 180.0 / math.pi
_HALF_PI = math.pi * 0.5
SPACED_ARMOR_DAMAGE_FACTOR = 0.0
AP_SHELLS_NORMALIZATION = 5 / RAD_TO_DEG
PENETRATION_SEGMENTS = 5
COMMON_MATERIALS_INDEX = 1000
LEFT_TRACK = 'leftTrack'
RIGHT_TRACK = 'rightTrack'
SURVEYING_DEVICE = 'surveyingDevice'
ARMOR_INSPECTOR_NAMES = (VehicleArmorTags.CHASSIS,
 VehicleArmorTags.GUN,
 VehicleArmorTags.GUN_MASK,
 VehicleArmorTags.HULL,
 VehicleArmorTags.TURRET,
 VehicleArmorTags.SCREEN,
 VehicleArmorTags.SURVEYING,
 VehicleArmorTags.WHEELS)
NOMINAL_ARMOR_PARTS_LIST = (VehicleArmorTags.HULL, VehicleArmorTags.TURRET)
DEFAULT_ATTACKER_GUN_SHOT_INDEX = 0

class MaterialUIData(object):
    __slots__ = ('partName', 'nominalArmor', 'viewAngle', 'resArmor', 'color', 'count', 'isSpacedArmor')

    def __init__(self, partName, viewAngle, isSpacedArmor, nominalArmor, resArmor=None, color='', count=1):
        self.partName = partName
        self.nominalArmor = nominalArmor
        self.viewAngle = viewAngle
        self.resArmor = resArmor if resArmor else nominalArmor
        self.color = color
        self.count = count
        self.isSpacedArmor = isSpacedArmor


def _calculateSegmentCount(scaleMin, scaleMax, colorLen, maxArmor):
    if colorLen > 1:
        delta = (scaleMax - scaleMin) // (colorLen - 1)
        count = min(max(int((maxArmor - scaleMin) // delta) + 1, 1), colorLen)
        return count
    return colorLen


def _fillArmorValues(model, colorList, scale, maxArmor):
    model.clear()
    colorLen = len(colorList)
    segmentCount = _calculateSegmentCount(scale.min, scale.max, colorLen, maxArmor)
    overlay = R.images.gui.maps.icons.lobby.armor_inspector.overlay()
    for i, color in enumerate(colorList):
        armorValueModel = ArmorValueModel()
        armorValueModel.setIsActive(i < segmentCount)
        armorValueModel.setOverlay(overlay)
        leftValue = rightValue = ''
        if i == 0:
            leftValue = '0'
        if i == segmentCount - 1:
            rightValue = str(maxArmor)
        if i == colorLen - 1:
            armorValueModel.setColor(color)
        armorValueModel.setLeftValue(leftValue)
        armorValueModel.setRightValue(rightValue)
        model.addViewModel(armorValueModel)

    model.invalidate()


def _fillPenetrationValues(model):
    model.clear()
    overlay = R.images.gui.maps.icons.lobby.armor_inspector.overlay()
    for i in range(PENETRATION_SEGMENTS):
        armorValueModel = ArmorValueModel()
        armorValueModel.setOverlay(overlay)
        leftValue = rightValue = ''
        if i == 0:
            leftValue = '0'
        if i == PENETRATION_SEGMENTS - 1:
            rightValue = '100'
        armorValueModel.setLeftValue(leftValue)
        armorValueModel.setRightValue(rightValue)
        model.addViewModel(armorValueModel)

    model.invalidate()


def _fillNoDamageValues(model, ricochetColor, noDamageColor):
    model.clear()
    overlay = R.images.gui.maps.icons.lobby.armor_inspector.overlay()
    armorValueModel = ArmorValueModel()
    armorValueModel.setOverlay(overlay)
    armorValueModel.setLeftValue(backport.text(R.strings.armor_inspector.armorValues.title.ricochet()))
    armorValueModel.setColor(ricochetColor)
    model.addViewModel(armorValueModel)
    armorValueModel = ArmorValueModel()
    armorValueModel.setOverlay(overlay)
    armorValueModel.setRightValue(backport.text(R.strings.armor_inspector.armorValues.title.no_damage()))
    armorValueModel.setColor(noDamageColor)
    model.addViewModel(armorValueModel)
    model.invalidate()


def fillArmorData(model, tier, normalArmorMax, spacedArmorMax, isColorBlind):
    config = getConfig()
    actualColorList = config.getActualColorList(isColorBlind)
    tierModel = config.tierList.getTierModel(tier)
    aiR = R.images.gui.maps.icons.armor_inspector
    mainGradient = aiR.main_armor_cb() if isColorBlind else aiR.main_armor()
    spacedGradient = aiR.spaced_armor_cb() if isColorBlind else aiR.spaced_armor()
    penGradient = aiR.penetration_chance_cb() if isColorBlind else aiR.penetration_chance()
    mainArmorModel = model.getMainArmor()
    spacedArmorModel = model.getSpacedArmor()
    _fillArmorValues(mainArmorModel, actualColorList.normalArmor, tierModel.normalArmor, normalArmorMax)
    _fillArmorValues(spacedArmorModel, actualColorList.spacedArmor, tierModel.spacedArmor, spacedArmorMax)
    model.setMainGradient(mainGradient)
    model.setSpacedGradient(spacedGradient)
    _fillPenetrationValues(model.getPenetrationChance())
    _fillNoDamageValues(model.getNoDamage(), actualColorList.ricochet, actualColorList.noDamage)
    model.setPenetrationGradient(penGradient)


def getMaterialsAtCursor(vehicleEntity, collisions=None, shellParams=None):
    materials = []
    parts = collisions if collisions is not None else getCollisionsAtCursor(vehicleEntity)
    ignoredMaterials = set()
    typeDescriptor = vehicleEntity.typeDescriptor
    collisions = vehicleEntity.appearance.collisions
    for _, hitAngleCos, matInfo, partID in parts:
        if matInfo is not None:
            isSpacedArmor = matInfo.vehicleDamageFactor == SPACED_ARMOR_DAMAGE_FACTOR
            if (partID, matInfo.kind) not in ignoredMaterials:
                if partID > vehicleEntity.appearance.collisions.maxStaticPartIndex:
                    partName = VehicleArmorTags.SCREEN if isSpacedArmor else VehicleArmorTags.HULL
                elif partID >= len(TankPartIndexes.ALL):
                    partName = VehicleArmorTags.CHASSIS
                elif partID > -1:
                    name = TankPartIndexes.getName(partID)
                    partName = VehicleArmorTags(name)
                else:
                    partName = VehicleArmorTags.WHEELS
                if isSpacedArmor:
                    if partName == VehicleArmorTags.GUN:
                        if matInfo.extra is None:
                            partName = VehicleArmorTags.GUN_MASK
                    if partName in NOMINAL_ARMOR_PARTS_LIST:
                        partName = VehicleArmorTags.SCREEN
                elif partID == TankPartIndexes.GUN and VehicleTurretTags.OSCILLATING in typeDescriptor.turret.tags:
                    partName = VehicleArmorTags.TURRET
                if partID == TankPartIndexes.TURRET and VehicleTurretTags.TURRETLESS in typeDescriptor.turret.tags:
                    partName = VehicleArmorTags.GUN
                if partID == TankPartIndexes.CHASSIS and typeDescriptor.isWheeledVehicle:
                    partName = VehicleArmorTags.SCREEN
                if partID > -1:
                    armorName = collisions.getBodyName(partID, matInfo.kind)
                    if SURVEYING_DEVICE in armorName:
                        partName = VehicleArmorTags.SURVEYING
                    elif LEFT_TRACK in armorName or RIGHT_TRACK in armorName:
                        partName = VehicleArmorTags.CHASSIS
                tags = matInfo.tags
                if tags is not None:
                    for tag in tags:
                        if tag in ARMOR_INSPECTOR_NAMES:
                            partName = tag
                            break

                nominalArmor = round(matInfo.armor)
                viewAngle = round(math.acos(hitAngleCos) * RAD_TO_DEG, 1)
                currentMaterial = MaterialUIData(partName=partName, nominalArmor=nominalArmor, viewAngle=viewAngle, isSpacedArmor=isSpacedArmor)
                if matInfo.useHitAngle:
                    effectiveArmor = _calculateEffectiveArmor(matInfo, hitAngleCos, shellParams)
                    currentMaterial.resArmor = round(effectiveArmor, 1)
                if matInfo.collideOnceOnly:
                    ignoredMaterials.add((partID, matInfo.kind))
                materials.append(currentMaterial)
            if not isSpacedArmor:
                break

    return materials


def _calculateEffectiveArmor(matInfo, hitAngleCos, shellParams):
    armorValue = float(matInfo.armor or 0.0)
    if armorValue <= MIN_HIT_ANGLE_COS:
        return armorValue
    else:
        normalizationAngle = AP_SHELLS_NORMALIZATION
        shellCaliber = 0.0
        if shellParams is not None:
            normalizationAngle = shellParams.normalizationAngle
            shellCaliber = shellParams.shellCaliber
        hitAngleCos = min(max(hitAngleCos, MIN_HIT_ANGLE_COS), 1.0)
        normalizedCos = applyNormalizationForArmor(hitAngleCos, armorValue, matInfo, normalizationAngle, shellCaliber)
        return armorValue if normalizedCos <= MIN_HIT_ANGLE_COS else armorValue / normalizedCos


def applyNormalizationForArmor(hitAngleCos, armorValue, matInfo, normalizationAngle, shellCaliber):
    if normalizationAngle <= MIN_HIT_ANGLE_COS or hitAngleCos >= 1.0:
        resultCos = max(hitAngleCos, MIN_HIT_ANGLE_COS)
        return resultCos
    if getattr(matInfo, 'checkCaliberForHitAngleNorm', False) and armorValue > MIN_HIT_ANGLE_COS:
        if shellCaliber > MIN_HIT_ANGLE_COS and armorValue * 2.0 < shellCaliber:
            normalizationAngle *= 1.4 * shellCaliber / (armorValue * 2.0)
    hitAngleCos = math_utils.clamp(-1.0, 1.0, hitAngleCos)
    hitAngle = min(math.acos(hitAngleCos) - normalizationAngle, _HALF_PI)
    if hitAngle <= MIN_HIT_ANGLE_COS:
        return 1.0
    resultCos = max(math.cos(hitAngle), MIN_HIT_ANGLE_COS)
    return resultCos


def getModuleForTurretRotation(vehicleEntity):
    parts = getCollisionsAtCursor(vehicleEntity)
    for distance, _, matInfo, partID in parts:
        if matInfo is not None:
            if partID > vehicleEntity.appearance.collisions.maxStaticPartIndex:
                partName = VehicleArmorTags.HULL
            elif partID >= len(TankPartIndexes.ALL):
                partName = VehicleArmorTags.CHASSIS
            elif partID > -1:
                name = TankPartIndexes.getName(partID)
                partName = VehicleArmorTags(name)
            else:
                partName = VehicleArmorTags.WHEELS
            if partName == VehicleArmorTags.TURRET and matInfo.vehicleDamageFactor == SPACED_ARMOR_DAMAGE_FACTOR:
                continue
            return (partName, distance)

    return (None, None)


def getCollisionsAtCursor(vehicleEntity):
    cursorPosition = GUI.mcursor().position
    ray, startPoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
    endPoint = startPoint + ray * COLLISION_RAY_LENGTH
    res = []
    if vehicleEntity.appearance.collisions is not None:
        collisions = vehicleEntity.appearance.collisions.collideAllWorld(startPoint, endPoint)
        if collisions:
            for dist, hitAngleCos, matKind, parIndex in collisions:
                matInfo = getMatinfo(vehicleEntity, parIndex, matKind, vehicleEntity.typeDescriptor.type.isWheeledVehicle)
                res.append(SegmentCollisionResultExt(dist, hitAngleCos, matInfo, parIndex))

    return res


def _normalizedToPixels(xNorm, yNorm, screenWidth, screenHeight):
    x = int((xNorm + 1) / 2 * screenWidth)
    y = int((1 - yNorm) / 2 * screenHeight)
    return (x, y)


def _convertMatInfo(matInfo):
    return (matInfo.kind,
     matInfo.armor if matInfo.armor is not None else 0.0,
     matInfo.vehicleDamageFactor,
     (matInfo.useHitAngle or False) | (matInfo.mayRicochet or False) << 1 | (matInfo.collideOnceOnly or False) << 2 | (matInfo.checkCaliberForRicochet or False) << 3 | (matInfo.checkCaliberForHitAngleNorm or False) << 4 | bool(matInfo.extra) << 5)


def _buildStaticMatInfos(vehicle):
    typeDescriptor = vehicle.typeDescriptor
    partDescriptors = ((TankPartIndexes.CHASSIS, typeDescriptor.chassis),
     (TankPartIndexes.HULL, typeDescriptor.hull),
     (TankPartIndexes.TURRET, typeDescriptor.turret),
     (TankPartIndexes.GUN, typeDescriptor.gun))
    materialsByPart = {}
    commonMaterialsInfo = vehicles.g_cache.commonConfig['materials'].values()
    materialsByPart[COMMON_MATERIALS_INDEX] = [ _convertMatInfo(matInfo) for matInfo in commonMaterialsInfo ]
    for partIndex, descriptor in partDescriptors:
        materialsByPart[partIndex] = [ _convertMatInfo(matInfo) for _, matInfo in descriptor.materials.items() ]

    return materialsByPart


def _buildDynamicMatInfos(vehicle):
    if vehicle is None:
        return {}
    else:
        collisionComponent = vehicle.appearance.collisions
        if collisionComponent is None:
            return {}
        dynamicMaterials = {}
        for partIndex in collisionComponent.partIndices:
            if partIndex <= collisionComponent.maxStaticPartIndex:
                continue
            partGO = collisionComponent.getPartGameObject(partIndex)
            if partGO is None or not partGO.isValid():
                continue
            partMaterials = BigWorld.getMaterials(partGO)
            if not partMaterials:
                continue
            partMaterialInfos = [ _convertMatInfo(matInfo) for matInfo in partMaterials if matInfo is not None ]
            if partMaterialInfos:
                dynamicMaterials[partIndex] = partMaterialInfos

        return dynamicMaterials


def _buildWheelsMatInfos(vehicle):
    if vehicle is None or not vehicle.typeDescriptor.isWheeledVehicle:
        return {}
    else:
        collisionComponent = vehicle.appearance.collisions
        if collisionComponent is None:
            return {}
        wheelsMaterials = {}
        for partIndex in collisionComponent.partIndices:
            if partIndex >= 0:
                continue
            wheelName = collisionComponent.getPartName(partIndex)
            if wheelName:
                wheelMatInfo = vehicle.typeDescriptor.chassis.wheelsArmor.get(wheelName)
                if wheelMatInfo:
                    converted = _convertMatInfo(wheelMatInfo)
                    wheelsMaterials[partIndex] = [converted]

        return wheelsMaterials


def getAllMatInfos(vehicle):
    materialsByPart = _buildStaticMatInfos(vehicle)
    if vehicle is not None:
        materialsByPart.update(_buildDynamicMatInfos(vehicle))
        materialsByPart.update(_buildWheelsMatInfos(vehicle))
    return {} if not materialsByPart else materialsByPart


def getCursorPositionInPixels():
    positionX, positionY = GUI.mcursor().position
    screenWidth, screenHeight = BigWorld.windowSize()
    return _normalizedToPixels(positionX, positionY, screenWidth, screenHeight)


def colorInt2Str(value):
    return '#{0:06X}'.format(value)


def stackMaterials(materials, tier):
    consolidatedMap = OrderedDict()
    tierModel = getConfig().tierList.getTierModel(tier)
    for material in materials:
        nominalArmor = material.nominalArmor
        partName = material.partName
        isSpacedArmor = material.isSpacedArmor
        key = (partName, isSpacedArmor)
        if key in consolidatedMap:
            consolidated = consolidatedMap[key]
            consolidated.nominalArmor += nominalArmor
            consolidated.resArmor += material.resArmor
            if partName != VehicleArmorTags.GUN_MASK:
                consolidated.count += 1
        scaleModel = tierModel.spacedArmor if isSpacedArmor else tierModel.normalArmor
        minimum, maximum = scaleModel.min, scaleModel.max
        fraction = (math_utils.clamp(minimum, maximum, nominalArmor) - minimum) / (maximum - minimum)
        consolidatedMap[key] = MaterialUIData(partName=partName, nominalArmor=nominalArmor, viewAngle=material.viewAngle, resArmor=material.resArmor, isSpacedArmor=isSpacedArmor, color=colorInt2Str(armor_inspector.getColor(fraction, isSpacedArmor)))

    return listvalues(consolidatedMap)


def getMaxArmor(vehicle):
    materials = getAllMatInfos(vehicle)
    mainArmor = 0
    spacedArmor = 0
    for partMat in materials.values():
        for mat in partMat:
            armorValue = mat[1]
            vehicleDamageFactor = mat[2]
            if vehicleDamageFactor != 0:
                mainArmor = max(mainArmor, armorValue)
            spacedArmor = max(spacedArmor, armorValue)

    return (int(mainArmor), int(spacedArmor))


def getArmorInspectorSetting(settingName):
    return AccountSettings.getSettings(ArmorInspectorSettingsKeys.SETTINGS).get(settingName)


def setArmorInspectorSetting(settingName, settingValue):
    settings = AccountSettings.getSettings(ArmorInspectorSettingsKeys.SETTINGS)
    settings.update({settingName: settingValue})
    AccountSettings.setSettings(ArmorInspectorSettingsKeys.SETTINGS, settings)


def getDefaultAttackerVehicleConfigByCD(compactDescr):
    return AttackerVehicleConfiguration(compactDescr, None, DEFAULT_ATTACKER_GUN_SHOT_INDEX)


def getDefaultAttackerVehicleConfigByLvl(level):
    attackerCD = vehicles.makeVehicleTypeCompDescrByName(getConfig().tierList.getTierModel(level).defaultVehicle)
    return getDefaultAttackerVehicleConfigByCD(attackerCD)


def getArmorInspectorAttackerVehicleConfig(level):
    settings = AccountSettings.getSessionSettings(ArmorInspectorSettingsKeys.SESSION_ATTACKING_VEHICLES)
    return settings[level] if settings and level in settings else getDefaultAttackerVehicleConfigByLvl(level)


def setArmorInspectorAttackerVehicleConfig(level, compactDescr=None, gunCompactDescr=None, activeGunShotIndex=None):
    currentConfig = AccountSettings.getSessionSettings(ArmorInspectorSettingsKeys.SESSION_ATTACKING_VEHICLES)
    currentAttackerVehicle = currentConfig.get(level) or getDefaultAttackerVehicleConfigByLvl(level)
    newAttackerVehicle = currentAttackerVehicle
    if compactDescr is not None:
        newAttackerVehicle = getDefaultAttackerVehicleConfigByCD(compactDescr)
    if gunCompactDescr is not None:
        newAttackerVehicle = newAttackerVehicle._replace(gunCompactDescr=gunCompactDescr)
        newAttackerVehicle = newAttackerVehicle._replace(activeGunShotIndex=DEFAULT_ATTACKER_GUN_SHOT_INDEX)
    if activeGunShotIndex is not None:
        newAttackerVehicle = newAttackerVehicle._replace(activeGunShotIndex=activeGunShotIndex)
    newConfig = dict(currentConfig)
    newConfig[level] = newAttackerVehicle
    AccountSettings.setSessionSettings(ArmorInspectorSettingsKeys.SESSION_ATTACKING_VEHICLES, newConfig)
    return


MINOR_SHORT_TOOLTIP_DATA = {MinorShortTooltipTypes.MAIN_ARMOR.value: {'icon': R.images.gui.maps.icons.lobby.armor_inspector.main_armor(),
                                           'header': backport.text(R.strings.armor_inspector.tooltip.minorShort.mainArmor.header()),
                                           'description': backport.text(R.strings.armor_inspector.tooltip.minorShort.mainArmor.description())},
 MinorShortTooltipTypes.SPACED_ARMOR.value: {'icon': R.images.gui.maps.icons.lobby.armor_inspector.spaced_armor(),
                                             'header': backport.text(R.strings.armor_inspector.tooltip.minorShort.spacedArmor.header()),
                                             'description': backport.text(R.strings.armor_inspector.tooltip.minorShort.spacedArmor.description())},
 MinorShortTooltipTypes.DEALING_DAMAGE_CHANCE.value: {'icon': R.images.gui.maps.icons.lobby.armor_inspector.damage_chance(),
                                                      'header': backport.text(R.strings.armor_inspector.tooltip.minorShort.damageChance.header()),
                                                      'description': backport.text(R.strings.armor_inspector.tooltip.minorShort.damageChance.description())},
 MinorShortTooltipTypes.NO_DAMAGE.value: {'icon': R.images.gui.maps.icons.lobby.armor_inspector.no_damage(),
                                          'header': backport.text(R.strings.armor_inspector.tooltip.minorShort.noDamage.header()),
                                          'description': backport.text(R.strings.armor_inspector.tooltip.minorShort.noDamage.description())},
 MinorShortTooltipTypes.RICOCHET.value: {'icon': R.images.gui.maps.icons.lobby.armor_inspector.ricochet(),
                                         'header': backport.text(R.strings.armor_inspector.tooltip.minorShort.ricochet.header()),
                                         'description': backport.text(R.strings.armor_inspector.tooltip.minorShort.ricochet.description())},
 MinorShortTooltipTypes.ATTACKING_CONFIGURATION.value: {'icon': None,
                                                        'header': backport.text(R.strings.armor_inspector.tooltip.minorShort.attackingConfiguration.header()),
                                                        'description': backport.text(R.strings.armor_inspector.tooltip.minorShort.attackingConfiguration.description())}}

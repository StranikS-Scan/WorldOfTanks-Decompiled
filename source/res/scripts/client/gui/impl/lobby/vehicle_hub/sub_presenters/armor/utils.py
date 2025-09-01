# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/utils.py
from __future__ import absolute_import, division
import math
from collections import OrderedDict
from future.builtins import round
import typing
import BigWorld
import GUI
import armor_inspector
import math_utils
from AvatarInputHandler import cameras
from Vehicle import SegmentCollisionResultExt
from constants import VehicleArmorTags, VehicleTurretTags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_value_model import ArmorValueModel
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
    MatInfo = typing.Tuple[int, float, float]
MIN_HIT_ANGLE_COS = 1e-05
COLLISION_RAY_LENGTH = 1500
RAD_TO_DEG = 180.0 / math.pi
SPACED_ARMOR_DAMAGE_FACTOR = 0.0
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


def fillArmorData(model, tier, normalArmorMax, spacedArmorMax, isColorBlind):
    config = getConfig()
    actualColorList = config.getActualColorList(isColorBlind)
    tierModel = config.tierList.getTierModel(tier)
    aiR = R.images.gui.maps.icons.armor_inspector
    mainGradient = aiR.main_armor_cb() if isColorBlind else aiR.main_armor()
    spacedGradient = aiR.spaced_armor_cb() if isColorBlind else aiR.spaced_armor()
    mainArmorModel = model.getMainArmor()
    spacedArmorModel = model.getSpacedArmor()
    _fillArmorValues(mainArmorModel, actualColorList.normalArmor, tierModel.normalArmor, normalArmorMax)
    _fillArmorValues(spacedArmorModel, actualColorList.spacedArmor, tierModel.spacedArmor, spacedArmorMax)
    model.setMainGradient(mainGradient)
    model.setSpacedGradient(spacedGradient)


def getMaterialsAtCursor(vehicleEntity, spaceID):
    materials = []
    parts = _getCollisionsAtCursor(vehicleEntity)
    ignoredMaterials = set()
    typeDescriptor = vehicleEntity.typeDescriptor
    collisions = vehicleEntity.appearance.collisions
    for _, hitAngleCos, matInfo, partID in parts:
        if matInfo is not None:
            isSpacedArmor = matInfo.vehicleDamageFactor == SPACED_ARMOR_DAMAGE_FACTOR
            if (partID, matInfo.kind) not in ignoredMaterials:
                if partID > vehicleEntity.appearance.collisions.maxStaticPartIndex:
                    partName = VehicleArmorTags.HULL
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
                    hitAngleCos = max(MIN_HIT_ANGLE_COS, hitAngleCos)
                    currentMaterial.resArmor = round(matInfo.armor / hitAngleCos, 1)
                if matInfo.collideOnceOnly:
                    ignoredMaterials.add((partID, matInfo.kind))
                materials.append(currentMaterial)
            if not isSpacedArmor:
                break

    return materials


def _getCollisionsAtCursor(vehicleEntity):
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


def getAllMatInfos(typeDescriptor):

    def convertMatInfo(matInfo):
        return (matInfo.kind, matInfo.armor if matInfo.armor is not None else 0.0, matInfo.vehicleDamageFactor)

    partDescriptors = ((TankPartIndexes.CHASSIS, typeDescriptor.chassis),
     (TankPartIndexes.HULL, typeDescriptor.hull),
     (TankPartIndexes.TURRET, typeDescriptor.turret),
     (TankPartIndexes.GUN, typeDescriptor.gun))
    commonMaterialsInfo = vehicles.g_cache.commonConfig['materials'].values()
    materialsAll = [tuple()] * (len(partDescriptors) + 1)
    materialsAll[0] = tuple((convertMatInfo(matInfo) for matInfo in commonMaterialsInfo))
    for partIndex, descriptor in partDescriptors:
        materialsAll[partIndex + 1] = tuple(((matInfo.kind, matInfo.armor if matInfo.armor is not None else 0.0, matInfo.vehicleDamageFactor) for _, matInfo in descriptor.materials.items()))

    return materialsAll


def getCursorPositionInPixels():
    positionX, positionY = GUI.mcursor().position
    screenWidth, screenHeight = BigWorld.windowSize()
    return _normalizedToPixels(positionX, positionY, screenWidth, screenHeight)


def _colorInt2Str(value):
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
        consolidatedMap[key] = MaterialUIData(partName=partName, nominalArmor=nominalArmor, viewAngle=material.viewAngle, resArmor=material.resArmor, isSpacedArmor=isSpacedArmor, color=_colorInt2Str(armor_inspector.getColor(fraction, isSpacedArmor)))

    return list(consolidatedMap.values())


def getMaxArmor(typeDescriptor):
    materials = getAllMatInfos(typeDescriptor)
    mainArmor = 0
    spacedArmor = 0
    for partMat in materials:
        for mat in partMat:
            armorValue = mat[1]
            vehicleDamageFactor = mat[2]
            if vehicleDamageFactor != 0:
                mainArmor = max(mainArmor, armorValue)
            spacedArmor = max(spacedArmor, armorValue)

    return (int(mainArmor), int(spacedArmor))

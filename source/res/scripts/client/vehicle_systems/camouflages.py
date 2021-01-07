# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/camouflages.py
import logging
from collections import namedtuple, defaultdict
from copy import deepcopy
from itertools import product
from string import lower
import typing
import BigWorld
import Math
import Vehicular
import AnimationSequence
from helpers import dependency
from skeletons.gui.shared import IItemsCache
import items.vehicles
from constants import IS_EDITOR
from items.vehicles import makeIntCompactDescrByID, getItemByCompactDescr
from items.customizations import parseOutfitDescr, CustomizationOutfit, createNationalEmblemComponents, isEditedStyle
from vehicle_outfit.outfit import Outfit
from vehicle_outfit.packers import ProjectionDecalPacker
from vehicle_systems.tankStructure import VehiclePartsTuple
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_constants import ModificationType, C11N_MASK_REGION, DEFAULT_DECAL_SCALE_FACTORS, SeasonType, CustomizationType, EMPTY_ITEM_ID, DEFAULT_DECAL_CLIP_ANGLE, ApplyArea, MATCHING_TAGS_SUFFIX, MAX_PROJECTION_DECALS_PER_AREA, CamouflageTilingType, CustomizationTypeNames, SLOT_TYPE_NAMES, DEFAULT_DECAL_TINT_COLOR, Options, SLOT_DEFAULT_ALLOWED_MODEL, ItemTags
from gui.shared.gui_items.customization.c11n_items import Customization
import math_utils
from helpers import newFakeModel
from soft_exception import SoftException
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from items.components.shared_components import ProjectionDecalSlotDescription
    from vehicle_outfit.containers import MultiSlot
    from items.vehicles import VehicleDescrType
_logger = logging.getLogger(__name__)
RepaintParams = namedtuple('PaintParams', ('enabled', 'baseColor', 'color', 'metallic', 'gloss', 'fading', 'strength'))
RepaintParams.__new__.__defaults__ = (False,
 0,
 (0, 0, 0),
 Math.Vector4(0.0),
 Math.Vector4(0.0),
 0.0,
 0.0)
CamoParams = namedtuple('CamoParams', ('mask', 'excludeMap', 'tiling', 'rotation', 'weights', 'c0', 'c1', 'c2', 'c3'))
CamoParams.__new__.__defaults__ = ('',
 '',
 Math.Vector4(0.0),
 0,
 Math.Vector4(0.0),
 0,
 0,
 0,
 0)
ProjectionDecalGenericParams = namedtuple('ProjectionDecalGenericParams', ('tintColor', 'position', 'rotation', 'scale', 'decalMap', 'glossDecalMap', 'applyAreas', 'clipAngle', 'mirroredHorizontally', 'mirroredVertically', 'doubleSided', 'scaleBySlotSize'))
ProjectionDecalGenericParams.__new__.__defaults__ = (Math.Vector4(0.0),
 Math.Vector3(0.0),
 Math.Vector3(0.0, 1.0, 0.0),
 1.0,
 '',
 '',
 0.0,
 0.0,
 False,
 False,
 False,
 True)
ModelAnimatorParams = namedtuple('ModelAnimatorParams', ('transform', 'attachNode', 'animatorName'))
ModelAnimatorParams.__new__.__defaults__ = (math_utils.createIdentityMatrix(), '', '')
LoadedModelAnimator = namedtuple('LoadedModelAnimator', ('animator', 'node', 'attachmentPartNode'))
AttachmentParams = namedtuple('AttachmentParams', ('transform', 'attachNode', 'modelName', 'sequenceId', 'attachmentLogic', 'initialVisibility', 'partNodeAlias'))
AttachmentParams.__new__.__defaults__ = (math_utils.createIdentityMatrix(),
 '',
 '',
 None,
 '',
 True,
 '')
_isDeferredRenderer = isRendererPipelineDeferred()
_DEFAULT_GLOSS = 0.509
_DEFAULT_METALLIC = 0.23
_DEAD_VEH_WEIGHT_COEFF = 0.1
_PROJECTION_DECAL_PREVIEW_ALPHA = 0.5

def prepareFashions(isDamaged):
    if isDamaged:
        fashions = [None,
         None,
         None,
         None]
    else:
        fashions = [BigWorld.WGVehicleFashion(),
         BigWorld.WGBaseFashion(),
         BigWorld.WGBaseFashion(),
         BigWorld.WGBaseFashion()]
    return VehiclePartsTuple(*fashions)


def updateFashions(appearance):
    isDamaged = not appearance.isAlive
    if isDamaged:
        return
    else:
        fashions = list(appearance.fashions)
        if not all(fashions):
            _logger.warning('Skipping attempt to create C11nComponent for appearance with a missing fashion.')
            appearance.c11nComponent = None
            return
        vDesc = appearance.typeDescriptor
        outfit = appearance.outfit
        outfitData = getOutfitData(appearance, outfit, vDesc, isDamaged)
        appearance.c11nComponent = appearance.createComponent(Vehicular.C11nComponent, fashions, appearance.compoundModel, outfitData)
        return


def _currentMapSeason():
    if IS_EDITOR:
        return SeasonType.SUMMER
    else:
        arena = BigWorld.player().arena
        if arena is not None:
            mapKind = arena.arenaType.vehicleCamouflageKind
            return SeasonType.fromArenaKind(mapKind)
        return


def getOutfitComponent(outfitCD, vehicleDescriptor=None, seasonType=None):
    if outfitCD:
        outfitComponent = parseOutfitDescr(outfitCD)
        if seasonType is None:
            seasonType = _currentMapSeason()
        if outfitComponent.styleId != 0 and outfitComponent.styleId != EMPTY_ITEM_ID and seasonType is not None:
            intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, outfitComponent.styleId)
            styleDescr = getItemByCompactDescr(intCD)
            if IS_EDITOR:
                if hasattr(outfitComponent, 'edSeasonsMask'):
                    anyOutfit = styleDescr.outfits[seasonType]
                    seasonType = anyOutfit.edSeasonsMask
            baseOutfitComponent = deepcopy(styleDescr.outfits[seasonType])
            if vehicleDescriptor and ItemTags.ADD_NATIONAL_EMBLEM in styleDescr.tags:
                emblems = createNationalEmblemComponents(vehicleDescriptor)
                baseOutfitComponent.decals.extend(emblems)
            if isEditedStyle(outfitComponent):
                outfitComponent = baseOutfitComponent.applyDiff(outfitComponent)
            else:
                outfitComponent = baseOutfitComponent
            if IS_EDITOR:

                def setupAlternateItem(itemType, outfit, sourceOutfit, collectionName):
                    alternateItem = outfit.editorData.alternateItems[itemType]
                    if alternateItem != 0:
                        sourceComponents = getattr(sourceOutfit, collectionName)
                        if sourceComponents is not None:
                            if itemType != CustomizationType.MODIFICATION:
                                for componentItem in sourceComponents:
                                    componentItem.id = alternateItem

                            else:
                                for index, _ in enumerate(sourceComponents):
                                    sourceComponents[index] = alternateItem

                                setattr(sourceOutfit, collectionName, sourceComponents)
                    return

                anyOutfit = styleDescr.outfits[seasonType]
                setupAlternateItem(CustomizationType.DECAL, anyOutfit, outfitComponent, 'decals')
                setupAlternateItem(CustomizationType.PROJECTION_DECAL, anyOutfit, outfitComponent, 'projection_decals')
                setupAlternateItem(CustomizationType.PAINT, anyOutfit, outfitComponent, 'paints')
                setupAlternateItem(CustomizationType.CAMOUFLAGE, anyOutfit, outfitComponent, 'camouflages')
                setupAlternateItem(CustomizationType.MODIFICATION, anyOutfit, outfitComponent, 'modifications')
                setupAlternateItem(CustomizationType.PERSONAL_NUMBER, anyOutfit, outfitComponent, 'personal_numbers')
        return outfitComponent
    else:
        return CustomizationOutfit()


def prepareBattleOutfit(outfitCD, vehicleDescriptor, vehicleId):
    vehicleCD = vehicleDescriptor.makeCompactDescr()
    outfitComponent = getOutfitComponent(outfitCD, vehicleDescriptor)
    outfit = Outfit(component=outfitComponent, vehicleCD=vehicleCD)
    player = BigWorld.player()
    forceHistorical = player.isHistoricallyAccurate and player.playerVehicleID != vehicleId and not outfit.isHistorical()
    return Outfit(vehicleCD=vehicleCD) if forceHistorical else outfit


def createSlotMap(vehDescr, slotTypeName):
    slotsByIdMap = {}
    for vehiclePartSlots in (vehDescr.hull.slotsAnchors,
     vehDescr.chassis.slotsAnchors,
     vehDescr.turret.slotsAnchors,
     vehDescr.gun.slotsAnchors):
        for vehicleSlot in vehiclePartSlots:
            if vehicleSlot.type == slotTypeName:
                slotsByIdMap[vehicleSlot.slotId] = vehicleSlot

    return slotsByIdMap


def getCamoPrereqs(outfit, vDesc):
    result = []
    if not outfit:
        return result
    else:
        for partIdx, descId in enumerate(TankPartNames.ALL):
            container = outfit.getContainer(partIdx)
            slot = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE)
            if not slot:
                continue
            intCD = slot.getItemCD()
            if intCD:
                camouflage = getItemByCompactDescr(intCD)
                result.append(camouflage.texture)
                exclusionMap = vDesc.type.camouflage.exclusionMask
                compDesc = getattr(vDesc, descId, None)
                if compDesc is not None:
                    if compDesc.camouflage.exclusionMask:
                        exclusionMap = compDesc.camouflage.exclusionMask
                result.append(exclusionMap)

        return result


def getCamo(appearance, outfit, containerId, vDesc, descId, isDamaged, default=None):
    result = default
    if not outfit:
        return result
    else:
        container = outfit.getContainer(containerId)
        slot = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE)
        if not slot:
            return result
        intCD = slot.getItemCD()
        if intCD:
            camouflage = getItemByCompactDescr(intCD)
            component = slot.getComponent()
            try:
                palette = camouflage.palettes[component.palette]
            except IndexError:
                palette = camouflage.palettes[0]

            weights = Math.Vector4(*[ (c >> 24) / 255.0 for c in palette ])
            if isDamaged:
                weights *= _DEAD_VEH_WEIGHT_COEFF
            vehPartCompDesc = getattr(vDesc, descId, None)
            if not vehPartCompDesc:
                return result
            area = vehPartCompDesc.customizableVehicleAreas.get(lower(CustomizationTypeNames[CustomizationType.CAMOUFLAGE]), (0, None))[0]
            if not area:
                return result
            tiling, exclusionMap = processTiling(appearance, vDesc, descId, camouflage, component)
            camoAngle = camouflage.rotation[descId]
            result = CamoParams(camouflage.texture, exclusionMap or '', tiling, camoAngle, weights, palette[0], palette[1], palette[2], palette[3])
        return result


def processTiling(appearance, vDesc, descId, camouflage, component):
    tilingSettings = camouflage.tilingSettings
    tilingType = tilingSettings[0]
    if camouflage.tiling.get(vDesc.type.compactDescr) is not None or tilingType == CamouflageTilingType.LEGACY:
        return processLegacyTiling(vDesc, descId, camouflage, component)
    else:
        vehPartCompDesc = getattr(vDesc, descId, None)
        if vehPartCompDesc is None:
            raise SoftException("Get descId '{}' attr from vDesc of vehicle '{}' error".format(descId, vDesc.type.name))
        vehLength = appearance.computeFullVehicleLength()
        if vehLength <= 0:
            raise SoftException("Invalid length {} of vehicle '{}'".format(vehLength, vDesc.type.name))
        vehPartCamouflage = vehPartCompDesc.camouflage
        textureSize = (BigWorld.PyTextureProvider(camouflage.texture).width, BigWorld.PyTextureProvider(camouflage.texture).height)
        aoTextureSize = vehPartCamouflage.aoTextureSize
        if not aoTextureSize:
            raise SoftException("Vehicle '{}' has not required texture size parameters".format(vDesc.type.name))
        vehDensity = vDesc.type.camouflage.density
        vehPartDensity = vehPartCamouflage.density
        try:
            scale = camouflage.scales[component.patternSize]
        except IndexError:
            scale = 0

        return (computeTiling(tilingSettings, textureSize, aoTextureSize, vehDensity, vehPartDensity, vehLength, scale), vehPartCompDesc.camouflage.exclusionMask)


def computeTiling(tilingSettings, textureSize, aoTextureSize, vehDensity, vehPartDensity, vehLength, scale):
    tilingType = tilingSettings[0]
    factor = tilingSettings[1]
    factorX = factor[0]
    factorY = factor[1]
    textureWidth = textureSize[0]
    textureHeight = textureSize[1]
    if tilingType == CamouflageTilingType.ABSOLUTE:
        coeficientX = factorX
        coeficientY = factorY
    elif tilingType == CamouflageTilingType.RELATIVE:
        coeficientX = textureWidth * factorX / vehLength
        coeficientY = textureHeight * factorY / vehLength
    elif tilingType == CamouflageTilingType.RELATIVEWITHFACTOR:
        coeficientX = textureWidth * factorX / vehLength * vehDensity[0]
        coeficientY = textureHeight * factorY / vehLength * vehDensity[1]
    else:
        raise SoftException('Unexpected tilingType {}'.format(tilingType))
    coeficientTextureX = aoTextureSize[0] / textureWidth
    coeficientTextureY = aoTextureSize[1] / textureHeight
    tilingX = coeficientTextureX * coeficientX / vehPartDensity[0] * scale
    tilingY = coeficientTextureY * coeficientY / vehPartDensity[1] * scale
    offset = tilingSettings[2]
    return (tilingX,
     tilingY,
     offset[0],
     offset[1])


def processLegacyTiling(vDesc, descId, camouflage, component):
    tiling = camouflage.tiling.get(vDesc.type.compactDescr)
    if tiling is None:
        tiling = vDesc.type.camouflage.tiling
    try:
        scale = camouflage.scales[component.patternSize]
    except IndexError:
        scale = 0

    if tiling:
        tiling = (tiling[0] * scale,
         tiling[1] * scale,
         tiling[2],
         tiling[3])
    exclusionMap = vDesc.type.camouflage.exclusionMask
    vehPartCompDesc = getattr(vDesc, descId, None)
    if vehPartCompDesc is not None:
        coeff = vehPartCompDesc.camouflage.tiling
        if coeff is not None:
            if tiling is not None:
                tiling = (tiling[0] * coeff[0],
                 tiling[1] * coeff[1],
                 tiling[2] + coeff[2],
                 tiling[3] + coeff[3])
            else:
                tiling = coeff
        if vehPartCompDesc.camouflage.exclusionMask:
            exclusionMap = vehPartCompDesc.camouflage.exclusionMask
    return (tiling, exclusionMap)


def getRepaint(outfit, containerId, vDesc):
    enabled = False
    quality = fading = 0.0
    overlapMetallic = overlapGloss = None
    nationID = vDesc.type.customizationNationID
    colorId = vDesc.type.baseColorID
    defaultColors = items.vehicles.g_cache.customization20().defaultColors
    defaultColor = defaultColors[nationID][colorId]
    intCD = outfit.misc.slotFor(GUI_ITEM_TYPE.MODIFICATION).getItemCD()
    if intCD:
        mod = getItemByCompactDescr(intCD)
        enabled = True
        quality = mod.getEffectValue(ModificationType.PAINT_AGE, quality)
        fading = mod.getEffectValue(ModificationType.PAINT_FADING, fading)
        overlapMetallic = mod.getEffectValue(ModificationType.METALLIC, overlapMetallic)
        overlapGloss = mod.getEffectValue(ModificationType.GLOSS, overlapGloss)
    container = outfit.getContainer(containerId)
    paintSlot = container.slotFor(GUI_ITEM_TYPE.PAINT)
    capacity = paintSlot.capacity()
    camoSlot = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE)
    if camoSlot is not None:
        if camoSlot.getItemCD():
            enabled = True
    colors = [defaultColor] * capacity
    metallics = [overlapMetallic or _DEFAULT_METALLIC] * (capacity + 1)
    glosses = [overlapGloss or _DEFAULT_GLOSS] * (capacity + 1)
    for idx in range(capacity):
        intCD = paintSlot.getItemCD(idx)
        if intCD:
            paint = getItemByCompactDescr(intCD)
            enabled = True
            colors[idx] = paint.color
            metallics[idx] = overlapMetallic or paint.metallic
            glosses[idx] = overlapGloss or paint.gloss
        if not (containerId == TankPartIndexes.GUN and idx == C11N_MASK_REGION):
            colors[idx] = colors[0]
            metallics[idx] = overlapMetallic or metallics[0]
            glosses[idx] = overlapGloss or glosses[0]

    colors = tuple(colors)
    metallics = tuple(metallics)
    glosses = tuple(glosses)
    return RepaintParams(enabled, defaultColor, colors, metallics, glosses, fading, quality) if enabled else RepaintParams(enabled, defaultColor)


def getAttachmentsAnimatorsPrereqs(attachments, spaceId):
    prereqs = []
    for attachment in attachments:
        if attachment.sequenceId is None:
            continue
        sequenceItem = __createSequenceItem(attachment.sequenceId)
        if sequenceItem is None:
            continue
        prereqs.append(AnimationSequence.Loader(sequenceItem.sequenceName, spaceId))

    return prereqs


def getAttachmentsAnimators(attachments, spaceId, loadedAnimators, compoundModel):
    animators = []
    for attachment in attachments:
        if attachment.sequenceId is None:
            continue
        sequenceItem = __createSequenceItem(attachment.sequenceId)
        if sequenceItem is None:
            continue
        if sequenceItem.sequenceName in loadedAnimators.failedIDs:
            _logger.error('Failed to load attachment sequence: "%s"', sequenceItem.sequenceName)
            continue
        animWrapper = AnimationSequence.PartWrapperContainer(compoundModel, spaceId, attachment.partNodeAlias)
        node = compoundModel.node(attachment.attachNode)
        animator = __prepareAnimator(loadedAnimators, sequenceItem.sequenceName, animWrapper, node, attachment.partNodeAlias)
        if animator is None:
            continue
        animators.append(animator)

    return animators


def getModelAnimatorsPrereqs(outfit, spaceId):
    multiSlot = outfit.misc.slotFor(GUI_ITEM_TYPE.SEQUENCE)
    prereqs = []
    for _, intCD, _ in multiSlot.items():
        item = getItemByCompactDescr(intCD)
        prereqs.append(AnimationSequence.Loader(item.sequenceName, spaceId))

    return prereqs


def getModelAnimators(outfit, vehicleDescr, spaceId, loadedAnimators, compoundModel):
    params = __getModelAnimators(outfit, vehicleDescr)
    animators = []
    for param in params:
        if param.animatorName in loadedAnimators.failedIDs:
            _logger.error('Failed to load sequence: "%s"', param.animatorName)
            continue
        fakeModel = newFakeModel()
        node = compoundModel.node(param.attachNode)
        node.attach(fakeModel, param.transform)
        animWrapper = AnimationSequence.ModelWrapperContainer(fakeModel, spaceId)
        animator = __prepareAnimator(loadedAnimators, param.animatorName, animWrapper, node)
        if animator is None:
            continue
        animators.append(animator)

    return animators


def __prepareAnimator(loadedAnimators, animatorName, wrapperToBind, node, attachmentPartNode=None):
    if animatorName in loadedAnimators.failedIDs:
        return None
    else:
        animator = loadedAnimators.pop(animatorName)
        animator.bindTo(wrapperToBind)
        if hasattr(animator, 'setBoolParam'):
            animator.setBoolParam('isDeferred', _isDeferredRenderer)
        return LoadedModelAnimator(animator, node, attachmentPartNode)


def __getParams(outfit, vehicleDescr, slotTypeName, slotType, paramsConverter):
    result = []
    slotsByIdMap = createSlotMap(vehicleDescr, slotTypeName)
    multiSlot = outfit.misc.slotFor(slotType)
    capacity = multiSlot.capacity()
    for idx in range(capacity):
        slotData = multiSlot.getSlotData(idx)
        if not slotData.isEmpty():
            if slotData.component.slotId in slotsByIdMap:
                slotParams = slotsByIdMap[slotData.component.slotId]
                result.append(paramsConverter(slotParams, slotData, idx))
            else:
                _logger.warning('SlotId mismatch (slotId=%(slotId)d component=%(component)s)', {'slotId': slotData.component.slotId,
                 'component': slotData.component})
                continue

    return result


def __createTransform(slotParams, slotData):
    worldTransform = math_utils.createRTMatrix(slotParams.rotation, slotParams.position)
    objectTransform = math_utils.createRTMatrix(Math.Vector3(slotData.component.rotation), Math.Vector3(slotData.component.position))
    worldTransform.postMultiply(objectTransform)
    return worldTransform


def __getModelAnimators(outfit, vehicleDescr):

    def getModelAnimatorParams(slotParams, slotData, _):
        item = getItemByCompactDescr(slotData.intCD)
        return ModelAnimatorParams(transform=__createTransform(slotParams, slotData), attachNode=slotParams.attachNode, animatorName=item.sequenceName)

    return __getParams(outfit, vehicleDescr, 'sequence', GUI_ITEM_TYPE.SEQUENCE, getModelAnimatorParams)


@dependency.replace_none_kwargs(guiItemsFactory=IGuiItemsFactory)
def __createSequenceItem(sequenceId, guiItemsFactory=None):
    try:
        from gui.customization.shared import C11N_ITEM_TYPE_MAP
        intCD = makeIntCompactDescrByID('customizationItem', C11N_ITEM_TYPE_MAP.get(GUI_ITEM_TYPE.SEQUENCE), sequenceId)
        sequenceItem = guiItemsFactory.createCustomization(intCD)
    except KeyError:
        _logger.error('Could not find sequence item with id=%d', sequenceId)
        return None

    return sequenceItem


def getAttachments(outfit, vehicleDescr):

    def getAttachmentParams(slotParams, slotData, idx):
        item = getItemByCompactDescr(slotData.intCD)
        return AttachmentParams(transform=__createTransform(slotParams, slotData), attachNode=slotParams.attachNode, modelName=item.modelName, sequenceId=item.sequenceId, attachmentLogic=item.attachmentLogic, initialVisibility=item.initialVisibility, partNodeAlias='attachment' + str(idx))

    return __getParams(outfit, vehicleDescr, 'attachment', GUI_ITEM_TYPE.ATTACHMENT, getAttachmentParams)


def _getMatchingTag(slot):
    for tag in slot.tags:
        if tag.endswith(MATCHING_TAGS_SUFFIX):
            return tag

    return None


def _matchTaggedProjectionDecalsToSlots(projectionDecalsMultiSlot, slotsByTagMap):
    taggedDecals = []
    appliedDecals = []
    for _, _, component in projectionDecalsMultiSlot.items():
        if component.slotId == ProjectionDecalPacker.STYLED_SLOT_ID and component.tags:
            taggedDecals.append(component)
        appliedDecals.append(component)

    if not taggedDecals:
        return True
    slots = _findProjectionDecalsSlotsByTags(taggedDecals, appliedDecals, slotsByTagMap)
    if not slots:
        return False
    for component, slotParams in zip(taggedDecals, slots):
        component.slotId = slotParams.slotId

    return True


def _findProjectionDecalsSlotsByTags(decals, appliedDecals, slotsByTagMap):
    resultSlots = []
    for tagsOrder in product(*[ decal.tags for decal in decals ]):
        slotsByTags = deepcopy(slotsByTagMap)
        slots = []
        for tag in tagsOrder:
            slot = slotsByTags.pop(tag, None)
            if slot is not None and slot not in slots:
                slots.append(slot)
            break
        else:
            if _checkSlotsOrder(slots, appliedDecals):
                resultSlots = _compareSlotsOrders(resultSlots, slots, decals)

    return resultSlots


def _getAppliedAreas(mask):
    areas = []
    for area in ApplyArea.RANGE:
        if mask & area:
            areas.append(area)

    return areas


def _checkSlotsOrder(slots, appliedDecals):
    areas = defaultdict(int)
    for decal in appliedDecals:
        for area in _getAppliedAreas(decal.showOn):
            areas[area] += 1

    for slot in slots:
        appliedAreas = _getAppliedAreas(slot.showOn)
        if all((areas[area] < MAX_PROJECTION_DECALS_PER_AREA for area in appliedAreas)):
            for area in appliedAreas:
                areas[area] += 1

        return False

    return True


def _compareSlotsOrders(slotsA, slotsB, decals):
    if not slotsA or not slotsB:
        return slotsA or slotsB
    slotsAIds = [ decal.tags.index(_getMatchingTag(slot)) for slot, decal in zip(slotsA, decals) ]
    slotsAIds.sort()
    slotsBIds = [ decal.tags.index(_getMatchingTag(slot)) for slot, decal in zip(slotsB, decals) ]
    slotsBIds.sort()
    return slotsA if slotsBIds >= slotsAIds else slotsB


def getGenericProjectionDecals(outfit, vehDesc):
    decalsParams = []
    style = outfit.style
    model = style.modelsSet if style is not None and style.modelsSet else SLOT_DEFAULT_ALLOWED_MODEL
    for slotParams in __vehicleSlotsByType(vehDesc, SLOT_TYPE_NAMES.FIXED_PROJECTION_DECAL):
        if model in slotParams.compatibleModels:
            if IS_EDITOR and (slotParams.edResourceId <= 0 or not slotParams.slotWrapper.canDraw):
                continue
            fixedDecalParams = __getFixedProjectionDecalParams(slotParams)
            decalsParams.append(fixedDecalParams)

    if not IS_EDITOR:
        if decalsParams:
            return decalsParams
    slotsByIdMap, slotsByTagMap = __createVehSlotsMaps(vehDesc)
    projectionDecalsMultiSlot = outfit.misc.slotFor(GUI_ITEM_TYPE.PROJECTION_DECAL)
    if style is not None:
        succeeded = _matchTaggedProjectionDecalsToSlots(projectionDecalsMultiSlot, slotsByTagMap)
        if not succeeded:
            _logger.error('Failed to match tagged projection decals of style: %(styleId)s to vehicle: %(vehName)s slots.', {'styleId': outfit.id,
             'vehName': vehDesc.type.name})
            return decalsParams
    for idx in projectionDecalsMultiSlot.order():
        slotData = projectionDecalsMultiSlot.getSlotData(idx)
        if slotData.isEmpty():
            continue
        item = getItemByCompactDescr(slotData.intCD)
        component = slotData.component
        slotId = component.slotId
        if slotId != ProjectionDecalPacker.STYLED_SLOT_ID:
            if slotId not in slotsByIdMap:
                _logger.error('Projection Decal slot mismatch. SlotId: %(slotId)s; Vehicle: %(vehName)s', {'slotId': slotId,
                 'vehName': vehDesc.type.name})
                continue
            slotParams = slotsByIdMap[slotId]
        elif component.tags:
            continue
        else:
            slotParams = None
        decalParams = __getProjectionDecalParams(vehDesc, item, component, slotParams)
        if decalParams is not None:
            decalsParams.append(decalParams)

    return decalsParams


def __vehicleSlotsByType(vehDesc, slotType):
    for partName in TankPartNames.ALL:
        partDesc = getattr(vehDesc, partName, None)
        if partDesc is None:
            continue
        for slot in partDesc.slotsAnchors:
            if slot.type == slotType:
                yield slot

    return


def __createVehSlotsMaps(vehDesc):
    slotsByIdMap = {}
    slotsByTagMap = {}
    for slotParams in __vehicleSlotsByType(vehDesc, SLOT_TYPE_NAMES.PROJECTION_DECAL):
        slotsByIdMap[slotParams.slotId] = slotParams
        matchingTag = _getMatchingTag(slotParams)
        if matchingTag is not None:
            slotsByTagMap[matchingTag] = slotParams

    return (slotsByIdMap, slotsByTagMap)


def __getFixedProjectionDecalParams(slotParams):
    intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.PROJECTION_DECAL, slotParams.itemId)
    item = getItemByCompactDescr(intCD)
    tintColor = __getProjectionDecalTintColor()
    mirroredHorizontally = slotParams.options & Options.MIRRORED_HORIZONTALLY
    mirroredVertically = slotParams.options & Options.MIRRORED_VERTICALLY
    params = ProjectionDecalGenericParams(tintColor=tintColor, position=Math.Vector3(slotParams.position), rotation=Math.Vector3(slotParams.rotation), scale=Math.Vector3(slotParams.scale), decalMap=item.texture, glossDecalMap=item.glossTexture, applyAreas=slotParams.showOn, clipAngle=slotParams.clipAngle, mirroredHorizontally=mirroredHorizontally, mirroredVertically=mirroredVertically, doubleSided=slotParams.doubleSided, scaleBySlotSize=True)
    return params


def __getProjectionDecalParams(vehDesc, item, component, slotParams=None):
    texture, glossTexture = __getProjectionDecalTextures(item, component, vehDesc)
    if texture is None or glossTexture is None:
        _logger.error('Failed to get textures for Projection Decal: %(itemId)s; Vehicle: %(vehName)s; Component: %(component)s', {'itemId': item.id,
         'vehName': vehDesc.type.name,
         'component': component})
        return
    else:
        tintColor = __getProjectionDecalTintColor(component)
        scale = __getProjectionDecalScale(component, slotParams)
        mirroredHorizontally = bool(component.isMirroredHorizontally())
        mirroredVertically = bool(component.isMirroredVertically())
        if slotParams is None:
            position = Math.Vector3(component.position)
            rotation = Math.Vector3(component.rotation)
            applyAreas = component.showOn
            clipAngle = DEFAULT_DECAL_CLIP_ANGLE
            doubleSided = component.doubleSided
        else:
            position = Math.Vector3(slotParams.position)
            rotation = Math.Vector3(slotParams.rotation)
            applyAreas = slotParams.showOn
            clipAngle = slotParams.clipAngle
            doubleSided = slotParams.doubleSided
        params = ProjectionDecalGenericParams(tintColor=tintColor, position=position, rotation=rotation, scale=scale, decalMap=texture, glossDecalMap=glossTexture, applyAreas=applyAreas, clipAngle=clipAngle, mirroredHorizontally=mirroredHorizontally, mirroredVertically=mirroredVertically, doubleSided=doubleSided, scaleBySlotSize=True)
        return params


def __getProjectionDecalTintColor(component=None):
    tintColor = component.tintColor if component is not None else DEFAULT_DECAL_TINT_COLOR
    tintColor = Math.Vector4(tintColor)
    tintColor /= 255
    if component is not None and component.preview:
        tintColor.w *= _PROJECTION_DECAL_PREVIEW_ALPHA
    return tintColor


def __getProjectionDecalScale(component, slotParams=None):
    if slotParams is not None:
        scale = slotParams.scale or component.scale
    else:
        scale = component.scale
    scale = Math.Vector3(scale)
    if component.scaleFactorId:
        scaleFactors = slotParams.scaleFactors if slotParams is not None else DEFAULT_DECAL_SCALE_FACTORS
        scaleFactor = scaleFactors[component.scaleFactorId - 1]
        scale.x *= scaleFactor
        scale.z *= scaleFactor
    return scale


def __getProjectionDecalTextures(item, component, vehDesc):
    texture = item.texture
    glossTexture = item.glossTexture
    if IS_EDITOR:
        return (texture, glossTexture)
    else:
        if item.isProgressive():
            progressionLevel = component.progressionLevel
            if progressionLevel == 0:
                itemsCache = dependency.instance(IItemsCache)
                inventory = itemsCache.items.inventory
                intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.PROJECTION_DECAL, item.id)
                progressData = inventory.getC11nProgressionData(intCD, vehDesc.type.compactDescr)
                if progressData is not None:
                    progressionLevel = progressData.currentLevel
            if progressionLevel:
                texture = Customization.getTextureByProgressionLevel(texture, progressionLevel)
                if glossTexture:
                    glossTexture = Customization.getTextureByProgressionLevel(glossTexture, progressionLevel)
            else:
                return (None, None)
        return (texture, glossTexture)


def getOutfitData(appearance, outfit, vehicleDescr, isDamaged):
    camos = []
    paints = []
    for fashionIdx, descId in enumerate(TankPartNames.ALL):
        camos.append(getCamo(appearance, outfit, fashionIdx, vehicleDescr, descId, isDamaged))
        paints.append(getRepaint(outfit, fashionIdx, vehicleDescr))

    decals = getGenericProjectionDecals(outfit, vehicleDescr)
    return (camos, paints, decals)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/customization_outfit.py
from collections import OrderedDict, defaultdict
from string import lower, upper
from typing import List, Dict, Tuple, Any, Optional
from debug_utils import LOG_ERROR
from items.components import c11n_components as cn
from items.components.c11n_constants import ApplyArea, CustomizationType, CustomizationTypeNames, HIDDEN_CAMOUFLAGE_ID, EMPTY_ITEM_ID
from items.named_vector import NamedVector
from items.utils import getDifferVehiclePartNames
from serialization import ComponentBinSerializer
from serialization.field import intField, strField, intArrayField, customArrayField
from serialization.serializable_component import SerializableComponent
from soft_exception import SoftException
from wrapped_reflection_framework import ReflectionMetaclass
from .attachment import AttachmentComponent
from .camouflage import CamouflageComponent
from .decal import DecalComponent
from .insignia import InsigniaComponent
from .paint import PaintComponent
from .personal_number import PersonalNumberComponent
from .projection_decal import ProjectionDecalComponent
from .sequence import SequenceComponent
from ..types import C11nSerializationTypes
__all__ = ('CustomizationOutfit', 'getAllItemsFromOutfit')

def _setComponentsRegion(component, region):
    if hasattr(component, 'appliedTo'):
        setattr(component, 'appliedTo', region)
    elif hasattr(component, 'slotId'):
        setattr(component, 'slotId', region)
    else:
        LOG_ERROR('Unable to set region {0} for component {1}'.format(region, component))


def __ignoreItem(itemId, cache, ignoreEmpty, ignoreStyleOnly):
    if itemId != EMPTY_ITEM_ID:
        if ignoreStyleOnly and cache[itemId].isStyleOnly:
            return True
    elif ignoreEmpty:
        return True
    return False


def getAllItemsFromOutfit(cc, outfit, ignoreHiddenCamouflage=True, ignoreEmpty=True, ignoreStyleOnly=True, skipStyle=False):
    result = defaultdict(int)
    for i in outfit.modifications:
        if __ignoreItem(i, cc.modifications, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.ModificationItem.makeIntDescr(i)] = 1

    for d in outfit.decals:
        decalId = d.id
        if __ignoreItem(decalId, cc.decals, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.DecalItem.makeIntDescr(decalId)] += ApplyArea.getAppliedCount(d.appliedTo)

    for d in outfit.projection_decals:
        decalId = d.id
        if __ignoreItem(decalId, cc.projection_decals, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.ProjectionDecalItem.makeIntDescr(decalId)] += 1

    for number in outfit.personal_numbers:
        numberId = number.id
        if __ignoreItem(numberId, cc.personal_numbers, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.PersonalNumberItem.makeIntDescr(numberId)] += ApplyArea.getAppliedCount(number.appliedTo)

    for p in outfit.paints:
        paintId = p.id
        if paintId != EMPTY_ITEM_ID:
            if ignoreStyleOnly and cc.paints[paintId].isStyleOnly:
                continue
            count = cc.paints[paintId].getAmount(p.appliedTo)
        elif not ignoreEmpty:
            count = ApplyArea.getAppliedCount(p.appliedTo)
        else:
            continue
        result[cn.PaintItem.makeIntDescr(paintId)] += count

    for ce in outfit.camouflages:
        camouflageId = ce.id
        if ce.id == HIDDEN_CAMOUFLAGE_ID:
            if ignoreHiddenCamouflage:
                continue
        elif __ignoreItem(camouflageId, cc.camouflages, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.CamouflageItem.makeIntDescr(camouflageId)] += ApplyArea.getAppliedCount(ce.appliedTo)

    if outfit.styleId and not skipStyle:
        result[cn.StyleItem.makeIntDescr(outfit.styleId)] = 1
    return dict(result)


class CustomizationOutfit(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = C11nSerializationTypes.OUTFIT
    fields = OrderedDict((('modifications', intArrayField()),
     ('paints', customArrayField(PaintComponent.customType)),
     ('camouflages', customArrayField(CamouflageComponent.customType)),
     ('decals', customArrayField(DecalComponent.customType)),
     ('styleId', intField(nonXml=True)),
     ('projection_decals', customArrayField(ProjectionDecalComponent.customType)),
     ('insignias', customArrayField(InsigniaComponent.customType)),
     ('personal_numbers', customArrayField(PersonalNumberComponent.customType)),
     ('sequences', customArrayField(SequenceComponent.customType)),
     ('attachments', customArrayField(AttachmentComponent.customType)),
     ('styleProgressionLevel', intField()),
     ('serial_number', strField()),
     ('overrideDefaultAttachments', intField())))
    __slots__ = ('modifications', 'paints', 'camouflages', 'decals', 'styleId', 'projection_decals', 'insignias', 'personal_numbers', 'sequences', 'overrideDefaultAttachments', 'attachments', 'styleProgressionLevel', 'serial_number')

    def __init__(self, modifications=None, paints=None, camouflages=None, decals=None, projection_decals=None, personal_numbers=None, styleId=0, insignias=None, sequences=None, overrideDefaultAttachments=0, attachments=None, styleProgressionLevel=0, serial_number=None):
        self.modifications = modifications or []
        self.paints = paints or []
        self.camouflages = camouflages or []
        self.decals = decals or []
        self.styleId = styleId or 0
        self.insignias = insignias or []
        self.projection_decals = projection_decals or []
        self.personal_numbers = personal_numbers or []
        self.sequences = sequences or []
        self.overrideDefaultAttachments = overrideDefaultAttachments or 0
        self.attachments = attachments or []
        self.styleProgressionLevel = styleProgressionLevel or 0
        self.serial_number = serial_number or ''
        super(CustomizationOutfit, self).__init__()

    def __nonzero__(self):
        for v in getattr(type(self), '__slots__'):
            if getattr(self, v):
                return True

        return False

    def getInvisibilityCamouflageId(self):
        for ce in self.camouflages:
            if ce.appliedTo & ApplyArea.HULL:
                return ce.id

        return None

    def makeCompDescr(self):
        if not self:
            return ''
        for typeId in CustomizationType.APPLIED_TO_TYPES:
            componentsAttrName = '{}s'.format(lower(CustomizationTypeNames[typeId]))
            components = CustomizationOutfit.applyAreaBitmaskToDict(getattr(self, componentsAttrName))
            setattr(self, componentsAttrName, CustomizationOutfit.shrinkAreaBitmask(components))

        return ComponentBinSerializer().serialize(self)

    @property
    def empty(self):
        return not self

    @staticmethod
    def applyAreaBitmaskToDict(components):
        res = {}
        for c in components:
            i = 1
            while i <= c.appliedTo:
                if c.appliedTo & i:
                    cpy = c.copy()
                    cpy.appliedTo = 0
                    res.setdefault(i, []).append(cpy)
                i *= 2

        return res

    @staticmethod
    def slotIdToDict(components):
        res = {}
        for c in components:
            cpy = c.copy()
            slotId = cpy.slotId
            cpy.slotId = 0
            res.setdefault(slotId, []).append(cpy)

        return res

    @staticmethod
    def shrinkAreaBitmask(components):
        grouped = {}
        for at, lst in components.iteritems():
            for i in lst:
                grouped.setdefault(i, []).append(at)

        res = []
        for item, group in grouped.iteritems():
            curItem = item.copy()
            curItem.appliedTo = reduce(int.__or__, group, 0)
            res.append(curItem)

        return res

    def applyDiff(self, outfit):
        resultOutfit = self.copy()
        resultOutfit.styleProgressionLevel = outfit.styleProgressionLevel
        resultOutfit.serial_number = outfit.serial_number
        for itemType in CustomizationType.RANGE:
            typeName = lower(CustomizationTypeNames[itemType])
            componentsAttrName = '{}s'.format(typeName)
            if componentsAttrName not in self.__slots__:
                continue
            modifiedComponents = getattr(outfit, componentsAttrName, None)
            baseComponents = getattr(resultOutfit, componentsAttrName, None)
            components = []
            if itemType == CustomizationType.MODIFICATION:
                if EMPTY_ITEM_ID not in modifiedComponents:
                    components = modifiedComponents or baseComponents
            else:
                isAppliedTo = itemType in CustomizationType.APPLIED_TO_TYPES
                toDict = self.applyAreaBitmaskToDict if isAppliedTo else self.slotIdToDict
                modifiedComponents = toDict(modifiedComponents)
                baseComponents = toDict(baseComponents)
                modifiedRegions = set(modifiedComponents)
                baseRegions = set(baseComponents)
                for region in baseRegions - modifiedRegions:
                    for component in baseComponents[region]:
                        component = component.copy()
                        _setComponentsRegion(component, region)
                        components.append(component)

                for region in modifiedRegions - baseRegions:
                    for component in modifiedComponents[region]:
                        component = component.copy()
                        _setComponentsRegion(component, region)
                        components.append(component)

                for region in modifiedRegions & baseRegions:
                    for component in modifiedComponents[region]:
                        component = component.copy()
                        if component.id != EMPTY_ITEM_ID:
                            _setComponentsRegion(component, region)
                            components.append(component)

                if isAppliedTo:
                    components = self.applyAreaBitmaskToDict(components)
                    components = self.shrinkAreaBitmask(components)
            setattr(resultOutfit, componentsAttrName, components)

        return resultOutfit

    def getDiff(self, outfit):
        resultOutfit = self.copy()
        for itemType in CustomizationType.FULL_RANGE:
            typeName = lower(CustomizationTypeNames[itemType])
            componentsAttrName = '{}s'.format(typeName)
            if componentsAttrName not in self.__slots__:
                continue
            modifiedComponents = getattr(resultOutfit, componentsAttrName, None)
            baseComponents = getattr(outfit, componentsAttrName, None)
            components = []
            if itemType == CustomizationType.MODIFICATION:
                if modifiedComponents != baseComponents:
                    components = modifiedComponents or [EMPTY_ITEM_ID]
            else:
                isAppliedTo = itemType in CustomizationType.APPLIED_TO_TYPES
                toDict = self.applyAreaBitmaskToDict if isAppliedTo else self.slotIdToDict
                modifiedComponents = toDict(modifiedComponents)
                baseComponents = toDict(baseComponents)
                modifiedRegions = set(modifiedComponents)
                baseRegions = set(baseComponents)
                for region in baseRegions - modifiedRegions:
                    component = baseComponents[region][0].copy()
                    if itemType == CustomizationType.PROJECTION_DECAL and component.matchingTag:
                        continue
                    component.id = EMPTY_ITEM_ID
                    _setComponentsRegion(component, region)
                    components.append(component)

            for region in modifiedRegions - baseRegions:
                component = modifiedComponents[region][0].copy()
                if itemType == CustomizationType.PROJECTION_DECAL and component.matchingTag:
                    continue
                _setComponentsRegion(component, region)
                components.append(component)

            for region in modifiedRegions & baseRegions:
                component = modifiedComponents[region][0].copy()
                if itemType == CustomizationType.PROJECTION_DECAL and component.matchingTag:
                    continue
                if component != baseComponents[region][0]:
                    _setComponentsRegion(component, region)
                    components.append(component)

            setattr(resultOutfit, componentsAttrName, components)

        return resultOutfit

    def dismountComponents(self, applyArea, dismountTypes=CustomizationType.DISMOUNT_TYPE):
        toMove = defaultdict(int)
        areas = [ i for i in ApplyArea.RANGE if i & applyArea ]
        for c11nType in dismountTypes:
            if c11nType is CustomizationType.STYLE:
                continue
            components = getattr(self, '{}s'.format(lower(CustomizationTypeNames[c11nType])))
            if c11nType in CustomizationType.APPLIED_TO_TYPES:
                for component in components:
                    for area in areas:
                        if component.appliedTo & area:
                            component.appliedTo &= ~area
                            if c11nType == CustomizationType.CAMOUFLAGE and component.id == HIDDEN_CAMOUFLAGE_ID:
                                continue
                            toMove[(c11nType, component.id)] += 1

                components[:] = [ c for c in components if c.appliedTo != 0 ]
            if c11nType == CustomizationType.PROJECTION_DECAL:
                for projectionDecal in self.projection_decals:
                    toMove[(CustomizationType.PROJECTION_DECAL, projectionDecal.id)] += 1

                self.projection_decals = []
            if c11nType == CustomizationType.MODIFICATION:
                for modification in self.modifications:
                    toMove[(CustomizationType.MODIFICATION, modification)] += 1

                self.modifications = []

        return dict(toMove)

    def dismountUnsuitableComponents(self, vehDescr, oldVehDescr):
        toMove = NamedVector()
        projectionDecals = self.projection_decals
        differPartNames = getDifferVehiclePartNames(vehDescr, oldVehDescr)
        if differPartNames:
            newProjectionDecals = []
            for projectionDecal in projectionDecals:
                if not cn.getVehicleProjectionDecalSlotParams(oldVehDescr, projectionDecal.slotId, differPartNames):
                    newProjectionDecals.append(projectionDecal)
                    continue
                toMove[(CustomizationType.PROJECTION_DECAL, projectionDecal.id)] += 1

            if toMove:
                self.projection_decals = newProjectionDecals
        for regionValue, vehiclePart in ((ApplyArea.HULL_REGIONS_VALUE, vehDescr.hull),
         (ApplyArea.CHASSIS_REGIONS_VALUE, vehDescr.chassis),
         (ApplyArea.TURRET_REGIONS_VALUE, vehDescr.turret),
         (ApplyArea.GUN_REGIONS_VALUE, vehDescr.gun)):
            for componentName, (area, _) in vehiclePart.customizableVehicleAreas.iteritems():
                components = getattr(self, '{}s'.format(lower(componentName)))
                componentType = getattr(CustomizationType, upper(componentName))
                for component in components:
                    if componentType == CustomizationType.CAMOUFLAGE and component.id == HIDDEN_CAMOUFLAGE_ID:
                        continue
                    appliedTo = regionValue & component.appliedTo
                    if not appliedTo:
                        continue
                    dismountArea = appliedTo & ~(area & appliedTo)
                    if not dismountArea:
                        continue
                    toMove += self.dismountComponents(dismountArea, (componentType,))

        return dict(toMove)

    def countComponents(self, componentId, typeId):
        result = 0
        if typeId in CustomizationType.APPLIED_TO_TYPES:
            outfitComponents = getattr(self, '{}s'.format(lower(CustomizationTypeNames[typeId])))
            for component in outfitComponents:
                if componentId == component.id:
                    result += ApplyArea.getAppliedCount(component.appliedTo)

        elif typeId in CustomizationType.SIMPLE_TYPES:
            if typeId == CustomizationType.STYLE and self.styleId == componentId:
                result += 1
            elif typeId == CustomizationType.PROJECTION_DECAL:
                result += len([ component for component in self.projection_decals if componentId == component.id ])
            elif typeId == CustomizationType.PERSONAL_NUMBER:
                result += len([ component for component in self.personal_numbers if componentId == component.id ])
            elif typeId == CustomizationType.MODIFICATION and componentId in self.modifications:
                result += 1
        return result

    def removeComponent(self, componentId, typeId, count):
        countBefore = count
        if count > 0:
            if typeId in CustomizationType.APPLIED_TO_TYPES:
                attr = '{}s'.format(lower(CustomizationTypeNames[typeId]))
                outfitComponents = getattr(self, attr)
                for component in outfitComponents:
                    if componentId == component.id:
                        for area in ApplyArea.RANGE:
                            if area & component.appliedTo:
                                component.appliedTo &= ~area
                                count -= 1
                                if not count:
                                    break

                    if not count:
                        break

                if count != countBefore:
                    setattr(self, attr, [ component for component in outfitComponents if component.appliedTo ])
            elif typeId in CustomizationType.SIMPLE_TYPES:
                if typeId == CustomizationType.STYLE and self.styleId == componentId:
                    self.styleId = 0
                    self.styleProgressionLevel = 0
                    self.serial_number = ''
                    count -= 1
                elif typeId == CustomizationType.PROJECTION_DECAL:
                    projection_decals = []
                    for component in self.projection_decals:
                        if componentId != component.id or count == 0:
                            projection_decals.append(component)
                            continue
                        count -= 1

                    self.projection_decals = projection_decals
                elif typeId == CustomizationType.MODIFICATION and componentId in self.modifications:
                    self.modifications.remove(componentId)
                    count -= 1
        return countBefore - count

    def wipe(self, gameParams, cache, getGroupedComponentPrice, vehType=None):
        outfitItems = getAllItemsFromOutfit(cache, self)
        for itemDescr, count in outfitItems.items():
            cid, itemId = cn.splitIntDescr(itemDescr)
            isNeedRemove = False
            item = cache.itemTypes[cid][itemId]
            if cid == CustomizationType.STYLE and item.isRent or item.isProgressive():
                isNeedRemove = True
            elif not (vehType is not None and cid == CustomizationType.DECAL and itemId == vehType.defaultPlayerEmblemID):
                try:
                    getGroupedComponentPrice(gameParams, itemDescr, True)
                except SoftException:
                    if not self.styleId or 'styleOnly' not in item.tags:
                        isNeedRemove = True

            if isNeedRemove:
                self.removeComponent(itemId, cid, count)
            outfitItems.pop(itemDescr)

        return outfitItems

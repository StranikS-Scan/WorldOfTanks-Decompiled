# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/packers.py
from itertools import product
from debug_utils import LOG_WARNING
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items import makeIntCompactDescrByID
from items.components.c11n_constants import CustomizationType
from items.customizations import PaintComponent, CamouflageComponent, DecalComponent, ProjectionDecalComponent
from skeletons.gui.shared.gui_items import IGuiItemsFactory

def pickPacker(itemTypeID):
    if itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
        return CamouflagePacker
    if itemTypeID == GUI_ITEM_TYPE.PAINT:
        return PaintPacker
    if itemTypeID == GUI_ITEM_TYPE.EMBLEM:
        return DecalPacker
    if itemTypeID == GUI_ITEM_TYPE.INSCRIPTION:
        return DecalPacker
    if itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
        return ModificationPacker
    if itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
        return ProjectionDecalPacker
    LOG_WARNING('Unsupported packer for the given type', itemTypeID)
    return CustomizationPacker


def isComponentComplex(component):
    return True if component and not isinstance(component, int) else False


class CustomizationPacker(object):
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    @staticmethod
    def pack(slot, component):
        raise NotImplementedError

    @classmethod
    def unpack(cls, slot, component, proxy=None):
        raise NotImplementedError

    @classmethod
    def invalidate(cls, slot):
        raise NotImplementedError

    @classmethod
    def create(cls, component, cType, proxy=None):
        if isComponentComplex(component):
            componentID = component.id
        else:
            componentID = component
        intCD = makeIntCompactDescrByID('customizationItem', cType, componentID)
        return cls.itemsFactory.createCustomization(intCD, proxy)

    @staticmethod
    def getRawComponent():
        raise NotImplementedError


class PaintPacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        for region, paint, _ in slot.items():
            component.paints.append(PaintComponent(id=paint.id, appliedTo=region))

    @classmethod
    def unpack(cls, slot, component, proxy=None):
        regions = slot.getRegions()
        for region, subcomp in product(regions, component.paints):
            appliedTo = subcomp.appliedTo & region
            if appliedTo:
                slotIdx = regions.index(appliedTo)
                item = cls.create(subcomp, CustomizationType.PAINT, proxy)
                slot.set(item, slotIdx, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, paint, comp in slot.items():
            comp.id = paint.id
            comp.appliedTo = region

    @staticmethod
    def getRawComponent():
        return PaintComponent


class CamouflagePacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        for region, camo, subcomp in slot.items():
            component.camouflages.append(CamouflageComponent(id=camo.id, patternSize=subcomp.patternSize, palette=subcomp.palette, appliedTo=region))

    @classmethod
    def unpack(cls, slot, component, proxy=None):
        regions = slot.getRegions()
        for region, subcomp in product(regions, component.camouflages):
            appliedTo = subcomp.appliedTo & region
            if appliedTo:
                item = cls.create(subcomp, CustomizationType.CAMOUFLAGE, proxy)
                slot.set(item, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, camo, comp in slot.items():
            comp.id = camo.id
            comp.appliedTo = region

    @staticmethod
    def getRawComponent():
        return CamouflageComponent


class DecalPacker(CustomizationPacker):
    _LOCK_SUBCOMP_ID = 0

    @staticmethod
    def pack(slot, component):
        for region, decal, _ in slot.items():
            component.decals.append(DecalComponent(id=decal.id, appliedTo=region))

    @classmethod
    def unpack(cls, slot, component, proxy=None):
        regions = slot.getRegions()
        for region, subcomp in product(regions, component.decals):
            appliedTo = subcomp.appliedTo & region
            if appliedTo:
                slotIdx = regions.index(appliedTo)
                if subcomp.id == DecalPacker._LOCK_SUBCOMP_ID:
                    slot.lock(slotIdx)
                else:
                    item = cls.create(subcomp, CustomizationType.DECAL, proxy)
                    slot.set(item, slotIdx, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, decal, comp in slot.items():
            comp.id = decal.id
            comp.appliedTo = region

    @staticmethod
    def getRawComponent():
        return DecalComponent


class ModificationPacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        if not slot.isEmpty():
            mod = slot.getItem()
            component.modifications.append(mod.id)

    @classmethod
    def unpack(cls, slot, component, proxy=None):
        for subcomp in component.modifications:
            item = cls.create(subcomp, CustomizationType.MODIFICATION, proxy)
            slot.set(item, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        if not slot.isEmpty():
            mod = slot.getItem()
            slot.set(mod, component=mod.id)

    @staticmethod
    def getRawComponent():
        return None


class ProjectionDecalPacker(CustomizationPacker):
    _LOCK_SUBCOMP_ID = 0

    @staticmethod
    def pack(slot, component):
        for _, decal, subcomp in slot.items():
            component.projection_decals.append(ProjectionDecalComponent(id=decal.id, showOn=subcomp.showOn, slotId=subcomp.slotId, scaleFactorId=subcomp.scaleFactorId, position=subcomp.position, scale=subcomp.scale, rotation=subcomp.rotation))

    @classmethod
    def unpack(cls, slot, component, proxy=None):
        for slotIdx, subcomp in enumerate(component.projection_decals):
            if subcomp.id == ProjectionDecalPacker._LOCK_SUBCOMP_ID:
                slot.lock(slotIdx)
            item = cls.create(subcomp, CustomizationType.PROJECTION_DECAL, proxy)
            slot.set(item, slotIdx, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for _, decal, comp in slot.items():
            comp.id = decal.id

    @staticmethod
    def getRawComponent():
        return ProjectionDecalComponent

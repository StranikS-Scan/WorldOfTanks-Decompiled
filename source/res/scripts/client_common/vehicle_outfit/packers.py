# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/vehicle_outfit/packers.py
from itertools import product
from debug_utils import LOG_WARNING
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_constants import CustomizationType
from items.customizations import PaintComponent, CamouflageComponent, DecalComponent, ProjectionDecalComponent, InsigniaComponent, PersonalNumberComponent, SequenceComponent, AttachmentComponent
from items.vehicles import makeIntCompactDescrByID, getItemByCompactDescr
from soft_exception import SoftException

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
    if itemTypeID == GUI_ITEM_TYPE.INSIGNIA:
        return InsigniaPacker
    if itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
        return PersonalNumberPacker
    if itemTypeID == GUI_ITEM_TYPE.SEQUENCE:
        return SequencePacker
    if itemTypeID == GUI_ITEM_TYPE.ATTACHMENT:
        return AttachmentPacker
    LOG_WARNING('Unsupported packer for the given type', itemTypeID)
    return CustomizationPacker


def pickPackers(itemTypes):
    packers = tuple((pickPacker(itemType) for itemType in itemTypes))
    return packers


def isComponentComplex(component):
    return True if component and not isinstance(component, int) else False


class CustomizationPacker(object):

    @staticmethod
    def pack(slot, component):
        raise NotImplementedError

    @classmethod
    def unpack(cls, slot, component):
        raise NotImplementedError

    @classmethod
    def invalidate(cls, slot):
        raise NotImplementedError

    @staticmethod
    def create(component, cType):
        if isComponentComplex(component):
            componentID = component.id
        else:
            componentID = component
        return makeIntCompactDescrByID('customizationItem', cType, componentID)

    @staticmethod
    def getRawComponent():
        raise NotImplementedError


class PaintPacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        for region, intCD, _ in slot.items():
            item = getItemByCompactDescr(intCD)
            component.paints.append(PaintComponent(id=item.id, appliedTo=region))

    @classmethod
    def unpack(cls, slot, component):
        regions = slot.getRegions()
        for region, subcomp in product(regions, component.paints):
            appliedTo = subcomp.appliedTo & region
            if appliedTo:
                slotIdx = regions.index(appliedTo)
                intCD = cls.create(subcomp, CustomizationType.PAINT)
                slot.set(intCD, slotIdx, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, intCD, comp in slot.items():
            item = getItemByCompactDescr(intCD)
            comp.id = item.id
            comp.appliedTo = region

    @staticmethod
    def getRawComponent():
        return PaintComponent


class CamouflagePacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        for region, intCD, subcomp in slot.items():
            item = getItemByCompactDescr(intCD)
            component.camouflages.append(CamouflageComponent(id=item.id, patternSize=subcomp.patternSize, palette=subcomp.palette, appliedTo=region))

    @classmethod
    def unpack(cls, slot, component):
        regions = slot.getRegions()
        for region, subcomp in product(regions, component.camouflages):
            appliedTo = subcomp.appliedTo & region
            if appliedTo:
                intCD = cls.create(subcomp, CustomizationType.CAMOUFLAGE)
                slot.set(intCD, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, intCD, comp in slot.items():
            item = getItemByCompactDescr(intCD)
            comp.id = item.id
            comp.appliedTo = region

    @staticmethod
    def getRawComponent():
        return CamouflageComponent


class DecalPacker(CustomizationPacker):
    _LOCK_SUBCOMP_ID = 0

    @staticmethod
    def pack(slot, component):
        for region, intCD, _ in slot.items((CustomizationType.DECAL,)):
            item = getItemByCompactDescr(intCD)
            component.decals.append(DecalComponent(id=item.id, appliedTo=region))

    @classmethod
    def unpack(cls, slot, component):
        regions = slot.getRegions()
        for region, subcomp in product(regions, component.decals):
            appliedTo = subcomp.appliedTo & region
            if appliedTo:
                slotIdx = regions.index(appliedTo)
                if subcomp.id == DecalPacker._LOCK_SUBCOMP_ID:
                    slot.lock(slotIdx)
                else:
                    intCD = cls.create(subcomp, CustomizationType.DECAL)
                    slot.set(intCD, slotIdx, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, intCD, comp in slot.items((CustomizationType.DECAL,)):
            item = getItemByCompactDescr(intCD)
            comp.id = item.id
            comp.appliedTo = region

    @staticmethod
    def getRawComponent():
        return DecalComponent


class ModificationPacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        if not slot.isEmpty():
            intCD = slot.getItemCD()
            item = getItemByCompactDescr(intCD)
            component.modifications.append(item.id)

    @classmethod
    def unpack(cls, slot, component):
        for subcomp in component.modifications:
            intCD = cls.create(subcomp, CustomizationType.MODIFICATION)
            slot.set(intCD, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        if not slot.isEmpty():
            intCD = slot.getItemCD()
            item = getItemByCompactDescr(intCD)
            slot.set(intCD, component=item.id)

    @staticmethod
    def getRawComponent():
        return None


class ProjectionDecalPacker(CustomizationPacker):
    STYLED_SLOT_ID = 0

    @staticmethod
    def pack(slot, component):
        for regionIdx in slot.order():
            subcomp = slot.getComponent(regionIdx)
            intCD = slot.getItemCD(regionIdx)
            item = getItemByCompactDescr(intCD)
            component.projection_decals.append(ProjectionDecalComponent(id=item.id, options=subcomp.options, slotId=subcomp.slotId, scaleFactorId=subcomp.scaleFactorId, showOn=subcomp.showOn, scale=subcomp.scale, rotation=subcomp.rotation, position=subcomp.position, tintColor=subcomp.tintColor, doubleSided=subcomp.doubleSided, tags=subcomp.tags, preview=subcomp.preview, progressionLevel=subcomp.progressionLevel))

    @classmethod
    def unpack(cls, slot, component):
        regions = slot.getRegions()
        for subcomp in component.projection_decals:
            intCD = cls.create(subcomp, CustomizationType.PROJECTION_DECAL)
            if subcomp.slotId == cls.STYLED_SLOT_ID:
                slot.add(intCD, subcomp.slotId, subcomp)
            if subcomp.slotId in regions:
                slotIdx = regions.index(subcomp.slotId)
                slot.set(intCD, slotIdx, component=subcomp)
            raise SoftException('Wrong slotId for current outfit')

    @classmethod
    def invalidate(cls, slot):
        for region, intCD, comp in slot.items():
            item = getItemByCompactDescr(intCD)
            comp.id = item.id
            comp.slotId = region

    @staticmethod
    def getRawComponent():
        return ProjectionDecalComponent


class InsigniaPacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        for region, intCD, _ in slot.items():
            item = getItemByCompactDescr(intCD)
            component.insignias.append(InsigniaComponent(id=item.id, appliedTo=region))

    @classmethod
    def unpack(cls, slot, component):
        regions = slot.getRegions()
        for region, subcomp in product(regions, component.insignias):
            appliedTo = subcomp.appliedTo & region
            if appliedTo:
                slotIdx = regions.index(appliedTo)
                intCD = cls.create(subcomp, CustomizationType.INSIGNIA)
                slot.set(intCD, slotIdx, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, intCD, comp in slot.items():
            item = getItemByCompactDescr(intCD)
            comp.id = item.id
            comp.appliedTo = region

    @staticmethod
    def getRawComponent():
        return InsigniaComponent


class PersonalNumberPacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        for region, intCD, subcomp in slot.items((CustomizationType.PERSONAL_NUMBER,)):
            item = getItemByCompactDescr(intCD)
            component.personal_numbers.append(PersonalNumberComponent(id=item.id, number=subcomp.number, appliedTo=region))

    @classmethod
    def unpack(cls, slot, component):
        regions = slot.getRegions()
        for region, subcomp in product(regions, component.personal_numbers):
            appliedTo = subcomp.appliedTo & region
            if appliedTo:
                slotIdx = regions.index(appliedTo)
                intCD = cls.create(subcomp, CustomizationType.PERSONAL_NUMBER)
                slot.set(intCD, slotIdx, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, intCD, comp in slot.items((CustomizationType.PERSONAL_NUMBER,)):
            item = getItemByCompactDescr(intCD)
            comp.id = item.id
            comp.appliedTo = region

    @staticmethod
    def getRawComponent():
        return PersonalNumberComponent


class SequencePacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        for _, intCD, subcomp in slot.items():
            item = getItemByCompactDescr(intCD)
            component.sequences.append(SequenceComponent(id=item.id, slotId=subcomp.slotId, position=subcomp.position, rotation=subcomp.rotation))

    @classmethod
    def unpack(cls, slot, component):
        for _, subcomp in enumerate(component.sequences):
            intCD = cls.create(subcomp, CustomizationType.SEQUENCE)
            slot.append(intCD, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for _, intCD, comp in slot.items():
            item = getItemByCompactDescr(intCD)
            comp.id = item.id

    @staticmethod
    def getRawComponent():
        return SequenceComponent


class AttachmentPacker(CustomizationPacker):

    @staticmethod
    def pack(slot, component):
        for _, intCD, subcomp in slot.items():
            item = getItemByCompactDescr(intCD)
            component.attachments.append(AttachmentComponent(id=item.id, slotId=subcomp.slotId, position=subcomp.position, rotation=subcomp.rotation))

    @classmethod
    def unpack(cls, slot, component):
        for _, subcomp in enumerate(component.attachments):
            intCD = cls.create(subcomp, CustomizationType.ATTACHMENT)
            slot.append(intCD, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for _, intCD, comp in slot.items():
            item = getItemByCompactDescr(intCD)
            comp.id = item.id

    @staticmethod
    def getRawComponent():
        return AttachmentComponent

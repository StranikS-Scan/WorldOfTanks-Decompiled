# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/packers.py
from itertools import product
from debug_utils import LOG_WARNING
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items import makeIntCompactDescrByID
from items.components.c11n_constants import CustomizationType
from items.customizations import PaintComponent, CamouflageComponent, DecalComponent
from skeletons.gui.shared.gui_items import IGuiItemsFactory

def pickPacker(itemTypeID):
    """ Get a packer capable of packing/unpacking the given itemTypes.
    
    :param itemTypeID: int, one of GUI_ITEM_TYPE.
    :return: an instance of CustomizationPacker.
    """
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
    LOG_WARNING('Unsupported packer for the given type', itemTypeID)
    return CustomizationPacker


def isComponentComplex(component):
    """ Check if component is complex object
    
    Some components are stored in a form of id only if they have
    no configurable properties (e.g. modifications work that way)
    """
    return True if component and not isinstance(component, int) else False


class CustomizationPacker(object):
    """ Packer can create gui customization items from serializable components
    and pack these items back.
    
    Packer holds the knowledge:
      - of unpacking:
        - where items are stored in an outfit component;
        - what items should be created.
      - of packing:
        - where items should be put in the outfit component.
    """
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    @staticmethod
    def pack(slot, component):
        """ Fill the given component with the subcomponents stored in the given slot.
        
        :param slot: an instance of MultiSlot.
        :param component: an instance of CustomizationOutfit.
        """
        raise NotImplementedError

    @classmethod
    def unpack(cls, slot, component, proxy=None):
        """ Carve up items applicable for the slot from the given component.
        
        :param slot: an instance of MultiSlot.
        :param component: an instance of CustomizationOutfit.
        :param proxy: an instance of ItemRequester.
        """
        raise NotImplementedError

    @classmethod
    def invalidate(cls, slot):
        """ Populate slot's components with proper data.
        
        :param slot: an instance of MultiSlot.
        """
        raise NotImplementedError

    @classmethod
    def create(cls, component, cType, proxy=None):
        """ Create a customization item from the given component.
        
        :param component: an instance of SerializableComponent or int.
        :param cType: type of customization (one of CustomizationType).
        :param proxy: an instance of ItemRequester.
        :return: an instance of Customization.
        """
        if isComponentComplex(component):
            componentID = component.id
        else:
            componentID = component
        intCD = makeIntCompactDescrByID('customizationItem', cType, componentID)
        return cls.itemsFactory.createCustomization(intCD, proxy)


class PaintPacker(CustomizationPacker):
    """ Packer/unpacker for Paint items.
    """

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


class CamouflagePacker(CustomizationPacker):
    """ Packer/unpacker for Camouflage items.
    """

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


class DecalPacker(CustomizationPacker):
    """ Packer/unpacker for Decal items (both Emblems and Inscriptions).
    """

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
                item = cls.create(subcomp, CustomizationType.DECAL, proxy)
                slot.set(item, slotIdx, component=subcomp)

    @classmethod
    def invalidate(cls, slot):
        for region, decal, comp in slot.items():
            comp.id = decal.id
            comp.appliedTo = region


class ModificationPacker(CustomizationPacker):
    """ Packer/unpacker for Modification items.
    """

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

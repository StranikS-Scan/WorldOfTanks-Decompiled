# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/containers.py
from collections import namedtuple
from functools import partial
from debug_utils import LOG_WARNING
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import packers
from skeletons.gui.shared.utils import IItemsRequester
from items.customizations import SerializableComponent, PaintComponent, CamouflageComponent, DecalComponent
Pair = namedtuple('Pair', 'item component')
Pair = partial(Pair, item=None, component=None)

def emptyComponent(itemTypeID):
    """ Create an empty component to store item's dynamic configuration.
    
    Empty components are needed when item is not applied but we need to
    store its configuration somewhere.
    """
    if itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
        return CamouflageComponent()
    elif itemTypeID == GUI_ITEM_TYPE.PAINT:
        return PaintComponent()
    else:
        return DecalComponent() if itemTypeID in (GUI_ITEM_TYPE.DECAL, GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION) else None


class OutfitContainer(object):
    """ Container class for a single vehicle area.
    
    Container is a part of outfit where customization items are actually stored
    in slots.
    
    Container encapsulates all information about some area of a vehicle
    (e.g. chassis, hull, turret, gun, etc.).
    
    Container consists of slots where items can be put. Some item types require
    to be single in the slot (e.g. only one camo is possible), while the others
    support multiple instances by dividing a container into parts, or regions
    (e.g. few decals on turret). This restrictions are represented by the list
    of regions provided to the slot.
    
    Container is also capable of constructing itself from the components and
    creating components back.
    """
    __slots__ = ('_areaID', '_slots')

    def __init__(self, areaID, slots):
        super(OutfitContainer, self).__init__()
        self._areaID = areaID
        self._slots = {}
        for slot in slots:
            self._slots[slot.getType()] = slot

    def pack(self, component):
        """ Fill the given component with the subcomponents.
        Subcomponents will be created from items stored inside container.
        
        :param component: an instance of CustomizationOutfit.
        """
        for slot in self.slots():
            packer = packers.pickPacker(slot.getType())
            packer.pack(slot, component)

    def unpack(self, component, proxy):
        """ Carve up items applicable for the container from the outfit component.
        
        :param component: an instance of CustomizationOutfit.
        :param proxy: an instance of ItemRequester.
        """
        for slot in self.slots():
            packer = packers.pickPacker(slot.getType())
            packer.unpack(slot, component, proxy)

    def getAreaID(self):
        """ Get area id anchored to this container.
        """
        return self._areaID

    def slotFor(self, itemTypeID):
        """ Get slot anchored to the given type.
        
        :param itemTypeID: int, type of the item (one of GUI_ITEM_TYPE).
        """
        return self._slots.get(itemTypeID)

    def setSlotFor(self, itemTypeID, slot):
        """ Set new MultiSlot to the container.
        
        :param itemTypeID: int, type of the item (one of GUI_ITEM_TYPE).
        :param slot: MultiSlot.
        """
        self._slots[itemTypeID] = slot

    def slots(self):
        """ Iterate over slots of the container.
        
        :yield: an instance of MultiSlot
        """
        for slot in self._slots.itervalues():
            yield slot

    def diff(self, other):
        """ Get difference between two containers of same area.
        """
        result = OutfitContainer(self.getAreaID(), slots=())
        for slotType in self._slots.iterkeys():
            aslot = self.slotFor(slotType)
            bslot = other.slotFor(slotType)
            result.setSlotFor(slotType, aslot.diff(bslot))

        return result

    def clear(self):
        """ Clear slots in container.
        """
        for slot in self._slots.itervalues():
            slot.clear()

    def invalidate(self):
        """ Use packers to populate components with proper data.
        """
        for slot in self.slots():
            packer = packers.pickPacker(slot.getType())
            packer.invalidate(slot)


class MultiSlot(object):
    """ Slot for multiple items inside container.
    
    Number of items inside of slot is limited by the number of regions anchored
    to the slot (e.g. we can put up to C11N_MAX_REGION_NUM paints into slot).
    """
    __slots__ = ('_regions', '_slotType', '_items', '_components')

    def __init__(self, slotType, regions):
        super(MultiSlot, self).__init__()
        self._regions = regions
        self._slotType = slotType
        self._items = {}
        self._components = {}

    def getType(self):
        """ Get a type of items that can be put into slot.
        """
        return self._slotType

    def getRegions(self):
        """ Get regions anchored to this slot.
        """
        return self._regions

    def capacity(self):
        """ Get the max capacity of the slot, i.e. how many items of configured type
        (through the constructor) can be put into it.
        """
        return len(self._regions)

    def getItem(self, idx=0):
        """ Get customization item applied to the given region.
        
        :param idx: integer, idx of a region.
        :return: an instance of Customization.
        """
        return self._items.get(idx, Pair()).item

    def getComponent(self, idx=0):
        """ Get component tied with the item.
        
        :param idx: integer, idx of a region.
        :return: an instance of SerializableComponent.
        """
        return self._items.get(idx, Pair()).component

    def set(self, item, idx=0, component=None):
        """ Set customization item to the region.
        
        :param item: instance of Customization.
        :param idx: integer, idx of a region.
        :param component: instance of SerializableComponent
        """
        if self._slotType != item.itemTypeID:
            LOG_WARNING('Slot type mismatch', self._slotType, item.itemTypeID)
            return
        if idx >= len(self._regions):
            LOG_WARNING('Invalid slot idx', idx)
            return
        if component and packers.isComponentComplex(component):
            component = component.copy()
        else:
            component = emptyComponent(self._slotType)
        self._items[idx] = Pair(item=item, component=component)

    def remove(self, idx):
        """ Remove customization item from a region.
        
        :param idx: integer, idx if a region.
        """
        self._items.pop(idx)

    def clear(self):
        """ Remove all customization items from slot.
        """
        self._items.clear()

    def isEmpty(self):
        """ Check if slot is empty (i.e. all regions are empty).
        """
        return not self._items

    def items(self):
        """ Iterate over the items yielding region id and item.
        
        :yield: tuple (region, Customization, SerializableComponent)
        """
        for idx, pair in self._items.iteritems():
            yield (self._regions[idx], pair.item, pair.component)

    def values(self):
        """ Iterate over the items in order of their region ids.
        """
        for idx in sorted(self._items):
            yield self._items[idx].item

    def diff(self, other):
        """ Get difference between two slots of same type.
        """
        result = MultiSlot(self.getType(), self.getRegions())
        for idx in range(self.capacity()):
            aitem, acomp = self.getItem(idx), self.getComponent(idx)
            bitem, bcomp = other.getItem(idx), other.getComponent(idx)
            citem, ccomp = (None, None)
            if not aitem:
                citem, ccomp = bitem, bcomp
            elif bitem and aitem.id != bitem.id:
                citem, ccomp = bitem, bcomp
            elif bitem and acomp != bcomp:
                citem, ccomp = bitem, bcomp
            if citem:
                result.set(citem, idx=idx, component=ccomp)

        return result

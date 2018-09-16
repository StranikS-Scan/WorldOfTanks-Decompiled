# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/containers.py
from collections import namedtuple
from functools import partial
from debug_utils import LOG_WARNING
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import packers
from items.customizations import PaintComponent, CamouflageComponent, DecalComponent
Pair = namedtuple('Pair', 'item component')
Pair = partial(Pair, item=None, component=None)

def emptyComponent(itemTypeID):
    if itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
        return CamouflageComponent()
    elif itemTypeID == GUI_ITEM_TYPE.PAINT:
        return PaintComponent()
    else:
        return DecalComponent() if itemTypeID in (GUI_ITEM_TYPE.DECAL, GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION) else None


class OutfitContainer(object):
    __slots__ = ('_areaID', '_slots')

    def __init__(self, areaID, slots):
        super(OutfitContainer, self).__init__()
        self._areaID = areaID
        self._slots = {}
        for slot in slots:
            self._slots[slot.getType()] = slot

    def pack(self, component):
        for slot in self.slots():
            packer = packers.pickPacker(slot.getType())
            packer.pack(slot, component)

    def unpack(self, component, proxy):
        for slot in self.slots():
            packer = packers.pickPacker(slot.getType())
            packer.unpack(slot, component, proxy)

    def getAreaID(self):
        return self._areaID

    def slotFor(self, itemTypeID):
        return self._slots.get(itemTypeID)

    def setSlotFor(self, itemTypeID, slot):
        self._slots[itemTypeID] = slot

    def slots(self):
        for slot in self._slots.itervalues():
            yield slot

    def diff(self, other):
        result = OutfitContainer(self.getAreaID(), slots=())
        for slotType in self._slots.iterkeys():
            aslot = self.slotFor(slotType)
            bslot = other.slotFor(slotType)
            result.setSlotFor(slotType, aslot.diff(bslot))

        return result

    def clear(self):
        for slot in self._slots.itervalues():
            slot.clear()

    def invalidate(self):
        for slot in self.slots():
            packer = packers.pickPacker(slot.getType())
            packer.invalidate(slot)


class MultiSlot(object):
    __slots__ = ('_regions', '_slotType', '_items', '_components')

    def __init__(self, slotType, regions):
        super(MultiSlot, self).__init__()
        self._regions = regions
        self._slotType = slotType
        self._items = {}
        self._components = {}

    def getType(self):
        return self._slotType

    def getRegions(self):
        return self._regions

    def capacity(self):
        return len(self._regions)

    def getItem(self, idx=0):
        return self._items.get(idx, Pair()).item

    def getComponent(self, idx=0):
        return self._items.get(idx, Pair()).component

    def set(self, item, idx=0, component=None):
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
        self._items.pop(idx)

    def clear(self):
        self._items.clear()

    def isEmpty(self):
        return not self._items

    def items(self):
        for idx, pair in self._items.iteritems():
            yield (self._regions[idx], pair.item, pair.component)

    def values(self):
        for idx in sorted(self._items):
            yield self._items[idx].item

    def diff(self, other):
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

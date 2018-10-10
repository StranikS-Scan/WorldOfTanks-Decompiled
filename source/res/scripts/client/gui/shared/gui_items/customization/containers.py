# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/containers.py
from debug_utils import LOG_WARNING
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import packers
from items.customizations import EmptyComponent, PaintComponent, CamouflageComponent, DecalComponent, ProjectionDecalComponent

class SlotData(object):
    __slots__ = ('item', 'component')

    def __init__(self, item=None, component=None):
        self.item = item
        self.component = component

    def diff(self, other):
        aitem, acomp = self.item, self.component
        bitem, bcomp = other.item, other.component
        citem, ccomp = (None, None)
        if not aitem:
            citem, ccomp = bitem, bcomp
        elif bitem and aitem.id != bitem.id:
            citem, ccomp = bitem, bcomp
        elif bitem and acomp != bcomp:
            citem, ccomp = bitem, bcomp
        return SlotData(item=citem, component=ccomp)

    def weakDiff(self, other):
        aitem, acomp = self.item, self.component
        bitem, bcomp = other.item, other.component
        citem, ccomp = (None, None)
        if not aitem:
            citem, ccomp = bitem, bcomp
        elif bitem and aitem.id != bitem.id:
            citem, ccomp = bitem, bcomp
        elif bitem and not acomp.weak_eq(bcomp):
            citem, ccomp = bitem, bcomp
        return SlotData(item=citem, component=ccomp)

    def isEmpty(self):
        return not (self.item or self.component)


def emptyComponent(itemTypeID):
    if itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
        return CamouflageComponent()
    if itemTypeID == GUI_ITEM_TYPE.PAINT:
        return PaintComponent()
    if itemTypeID in (GUI_ITEM_TYPE.DECAL, GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
        return DecalComponent()
    return ProjectionDecalComponent() if itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL else EmptyComponent()


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
    __slots__ = ('_regions', '_slotType', '_items', '_locks')

    def __init__(self, slotType, regions):
        super(MultiSlot, self).__init__()
        self._regions = regions
        self._slotType = slotType
        self._items = {}
        self._locks = {}

    def getType(self):
        return self._slotType

    def getRegions(self):
        return self._regions

    def capacity(self):
        return len(self._regions)

    def getSlotData(self, idx=0):
        return self._items.get(idx, SlotData())

    def getItem(self, idx=0):
        return self._items.get(idx, SlotData()).item

    def getComponent(self, idx=0):
        return self._items.get(idx, SlotData()).component

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
        self._items[idx] = SlotData(item=item, component=component)

    def lock(self, idx=0):
        self._locks[idx] = True

    def remove(self, idx):
        self._items.pop(idx)

    def clear(self):
        self._items.clear()

    def isEmpty(self):
        return not self._items

    def isLocked(self, idx=0):
        return self._locks.get(idx, False)

    def items(self):
        for idx, pair in self._items.iteritems():
            yield (self._regions[idx], pair.item, pair.component)

    def values(self):
        for idx in sorted(self._items):
            yield self._items[idx].item

    def diff(self, other):
        result = MultiSlot(self.getType(), self.getRegions())
        for idx in range(self.capacity()):
            df = self.getSlotData(idx).diff(other.getSlotData(idx))
            if df.item:
                result.set(df.item, idx=idx, component=df.component)

        return result

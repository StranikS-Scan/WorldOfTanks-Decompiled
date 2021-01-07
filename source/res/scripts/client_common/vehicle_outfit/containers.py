# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/vehicle_outfit/containers.py
import logging
import typing
from shared_utils import first
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_components import CustomizationType, DecalType
from items.customizations import EmptyComponent, PaintComponent, CamouflageComponent, DecalComponent, ProjectionDecalComponent, PersonalNumberComponent, SequenceComponent, AttachmentComponent
from items.vehicles import getItemByCompactDescr
from soft_exception import SoftException
from vehicle_outfit import packers
if typing.TYPE_CHECKING:
    from items.customizations import SerializableComponent
    from items.components.c11n_components import BaseCustomizationItem
_logger = logging.getLogger(__name__)

class SlotData(object):
    __slots__ = ('intCD', 'component')

    def __init__(self, intCD=0, component=None):
        self.intCD = intCD
        self.component = component

    def isEqual(self, other):
        return self.intCD == other.intCD and self.component == other.component

    def diff(self, other):
        aintCD, acomp = self.intCD, self.component
        bintCD, bcomp = other.intCD, other.component
        cintCD, ccomp = (None, None)
        if not aintCD:
            cintCD, ccomp = bintCD, bcomp
        elif bintCD and aintCD != bintCD:
            cintCD, ccomp = bintCD, bcomp
        elif bintCD and acomp != bcomp:
            cintCD, ccomp = bintCD, bcomp
        return SlotData(intCD=cintCD, component=ccomp)

    def weakDiff(self, other):
        aintCD, acomp = self.intCD, self.component
        bintCD, bcomp = other.intCD, other.component
        cintCD, ccomp = (None, None)
        if not aintCD:
            cintCD, ccomp = bintCD, bcomp
        elif bintCD and aintCD != bintCD:
            cintCD, ccomp = bintCD, bcomp
        elif bintCD and not acomp.weak_eq(bcomp):
            cintCD, ccomp = bintCD, bcomp
        return SlotData(intCD=cintCD, component=ccomp)

    def isEmpty(self):
        return not (self.intCD or self.component)


def emptyComponent(itemTypeID):
    if itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
        return CamouflageComponent()
    if itemTypeID == GUI_ITEM_TYPE.PAINT:
        return PaintComponent()
    if itemTypeID in (GUI_ITEM_TYPE.DECAL, GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
        return DecalComponent()
    if itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
        return PersonalNumberComponent()
    if itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
        return ProjectionDecalComponent()
    if itemTypeID == GUI_ITEM_TYPE.SEQUENCE:
        return SequenceComponent()
    return AttachmentComponent() if itemTypeID == GUI_ITEM_TYPE.ATTACHMENT else EmptyComponent()


def getItemType(itemDescriptor):
    if itemDescriptor.itemType == CustomizationType.PAINT:
        return GUI_ITEM_TYPE.PAINT
    if itemDescriptor.itemType == CustomizationType.CAMOUFLAGE:
        return GUI_ITEM_TYPE.CAMOUFLAGE
    if itemDescriptor.itemType == CustomizationType.DECAL:
        if itemDescriptor.type == DecalType.EMBLEM:
            return GUI_ITEM_TYPE.EMBLEM
        return GUI_ITEM_TYPE.INSCRIPTION
    if itemDescriptor.itemType == CustomizationType.INSIGNIA:
        return GUI_ITEM_TYPE.INSIGNIA
    if itemDescriptor.itemType == CustomizationType.MODIFICATION:
        return GUI_ITEM_TYPE.MODIFICATION
    if itemDescriptor.itemType == CustomizationType.PROJECTION_DECAL:
        return GUI_ITEM_TYPE.PROJECTION_DECAL
    if itemDescriptor.itemType == CustomizationType.PERSONAL_NUMBER:
        return GUI_ITEM_TYPE.PERSONAL_NUMBER
    if itemDescriptor.itemType == CustomizationType.SEQUENCE:
        return GUI_ITEM_TYPE.SEQUENCE
    return GUI_ITEM_TYPE.ATTACHMENT if itemDescriptor.itemType == CustomizationType.ATTACHMENT else GUI_ITEM_TYPE.CUSTOMIZATION


class OutfitContainer(object):
    __slots__ = ('_areaID', '_slots')

    def __init__(self, areaID, slots):
        super(OutfitContainer, self).__init__()
        self._areaID = areaID
        self._slots = {}
        for slot in slots:
            for slotType in slot.getTypes():
                self._slots[slotType] = slot

    def __str__(self):
        result = 'OutfitContainer (areaID={}):'.format(self._areaID)
        slots = '\n'.join(map(str, self.slots()))
        if slots:
            result += '\n' + slots
        return result

    def pack(self, component):
        for slot in self._slots.itervalues():
            packersList = packers.pickPackers(slot.getTypes())
            for packer in packersList:
                packer.pack(slot, component)

    def unpack(self, component):
        for slot in self._slots.itervalues():
            packersList = packers.pickPackers(slot.getTypes())
            for packer in packersList:
                packer.unpack(slot, component)

    def getAreaID(self):
        return self._areaID

    def slotFor(self, itemTypeID):
        return self._slots.get(itemTypeID)

    def setSlotFor(self, itemTypeID, slot):
        self._slots[itemTypeID] = slot

    def slots(self):
        for slot in set(self._slots.itervalues()):
            yield slot

    def diff(self, other):
        result = OutfitContainer(self.getAreaID(), slots=())
        for aslot in self.slots():
            slotTypes = aslot.getTypes()
            bslot = other.slotFor(first(slotTypes))
            diff = aslot.diff(bslot)
            for slotType in slotTypes:
                result.setSlotFor(slotType, diff)

        return result

    def discard(self, other):
        result = OutfitContainer(self.getAreaID(), slots=())
        for aslot in self.slots():
            slotTypes = aslot.getTypes()
            bslot = other.slotFor(first(slotTypes))
            for slotType in slotTypes:
                result.setSlotFor(slotType, aslot.discard(bslot))

        return result

    def adjust(self, other):
        result = OutfitContainer(self.getAreaID(), slots=())
        for aslot in self.slots():
            slotTypes = aslot.getTypes()
            bslot = other.slotFor(first(slotTypes))
            for slotType in slotTypes:
                result.setSlotFor(slotType, aslot.adjust(bslot))

        return result

    def clear(self):
        for slot in self.slots():
            slot.clear()

    def invalidate(self):
        for slot in self.slots():
            packersList = packers.pickPackers(slot.getTypes())
            for packer in packersList:
                packer.invalidate(slot)

    def removePreview(self):
        for slot in self.slots():
            packersList = packers.pickPackers(slot.getTypes())
            for packer in packersList:
                packer.removePreview(slot)


class MultiSlot(object):
    __slots__ = ('_regions', '_slotTypes', '_items', '_locks')

    def __init__(self, slotTypes, regions):
        super(MultiSlot, self).__init__()
        self._regions = regions
        self._slotTypes = slotTypes
        self._items = {}
        self._locks = {}

    def __str__(self):
        result = 'MultiSlot (slotType={}):'.format(self._slotTypes)
        items = '\n'.join(map(str, self.items()))
        if items:
            result += '\n' + items
        return result

    def getTypes(self):
        return self._slotTypes

    def getRegions(self):
        return self._regions

    def capacity(self):
        return len(self._regions)

    def getSlotData(self, idx=0):
        return self._items.get(idx, SlotData())

    def getItemCD(self, idx=0):
        return self._items.get(idx, SlotData()).intCD

    def getComponent(self, idx=0):
        return self._items.get(idx, SlotData()).component

    def set(self, intCD, idx=0, component=None):
        itemDescriptor = getItemByCompactDescr(intCD)
        itemType = getItemType(itemDescriptor)
        if itemType not in self._slotTypes:
            _logger.warning('item type %s does not correspond to allowed slot types %s', itemType, self._slotTypes)
            return False
        if idx >= len(self._regions):
            _logger.warning('Invalid slot idx %s', idx)
            return False
        if component and packers.isComponentComplex(component):
            component = component.copy()
        else:
            component = emptyComponent(itemType)
        self._items[idx] = SlotData(intCD=intCD, component=component)
        return True

    def lock(self, idx=0):
        self._locks[idx] = True

    def remove(self, idx):
        if idx in self._items:
            self._items.pop(idx)

    def clear(self):
        self._items.clear()

    def isEmpty(self):
        return not self._items

    def isLocked(self, idx=0):
        return self._locks.get(idx, False)

    def items(self, customizationTypes=None):
        if customizationTypes:
            for idx, pair in self._items.iteritems():
                item = getItemByCompactDescr(pair.intCD)
                if item.itemType in customizationTypes:
                    yield (self._regions[idx], pair.intCD, pair.component)

        else:
            for idx, pair in self._items.iteritems():
                yield (self._regions[idx], pair.intCD, pair.component)

    def values(self):
        for idx in sorted(self._items):
            yield self._items[idx].intCD

    def diff(self, other):
        self._validateType(other)
        result = self._cloneEmpty()
        for idx in range(self.capacity()):
            df = self.getSlotData(idx).diff(other.getSlotData(idx))
            if df.intCD:
                result.set(df.intCD, idx=idx, component=df.component)

        return result

    def discard(self, other):
        self._validateType(other)
        result = self._cloneEmpty()
        for idx in range(self.capacity()):
            adata = self.getSlotData(idx)
            bdata = other.getSlotData(idx)
            if not adata.isEqual(bdata) and not adata.isEmpty():
                result.set(adata.intCD, idx=idx, component=adata.component)

        return result

    def adjust(self, other):
        self._validateType(other)
        result = self._cloneEmpty()
        for idx in range(self.capacity()):
            adata = self.getSlotData(idx)
            bdata = other.getSlotData(idx)
            if not bdata.isEmpty():
                result.set(bdata.intCD, idx=idx, component=bdata.component)
            if not adata.isEmpty():
                result.set(adata.intCD, idx=idx, component=adata.component)

        return result

    def isEqual(self, other):
        self._validateType(other)
        if self.capacity() != other.capacity():
            return False
        for idx in range(self.capacity()):
            if not self.getSlotData(idx).isEqual(other.getSlotData(idx)):
                return False

        return True

    def _validateType(self, other):
        if type(self) is not type(other):
            raise SoftException('Comparable MultiSlots has different types', self, other)

    def _cloneEmpty(self):
        return MultiSlot(self.getTypes(), self.getRegions())


class SizableMultiSlot(MultiSlot):
    __slots__ = ()

    def append(self, intCD, component=None):
        newRegion = self.capacity()
        self._regions.append(newRegion)
        super(SizableMultiSlot, self).set(intCD, newRegion, component)

    def clear(self):
        super(SizableMultiSlot, self).clear()
        self._regions = []

    def _cloneEmpty(self):
        return SizableMultiSlot(self.getTypes(), self.getRegions())


class ProjectionDecalsMultiSlot(MultiSlot):
    __slots__ = ('_limit', '_order')

    def __init__(self, slotTypes, regions, limit):
        super(ProjectionDecalsMultiSlot, self).__init__(slotTypes, regions)
        self._limit = limit
        self._order = []

    def order(self):
        return self._order

    def set(self, intCD, idx=0, component=None):
        if len(self._items) + (idx not in self._items) > self._limit:
            _logger.warning('MultiSlot is filled %s', self._slotTypes)
            return False
        if idx in self._order:
            self._order.remove(idx)
        self._order.append(idx)
        return super(ProjectionDecalsMultiSlot, self).set(intCD, idx, component)

    def add(self, intCD, region=0, component=None):
        idx = self.capacity()
        self._regions.append(region)
        self.set(intCD, idx, component)

    def clear(self):
        self._order = []
        super(ProjectionDecalsMultiSlot, self).clear()

    def remove(self, idx):
        if idx in self._order:
            self._order.remove(idx)
        super(ProjectionDecalsMultiSlot, self).remove(idx)

    def _cloneEmpty(self):
        return ProjectionDecalsMultiSlot(self.getTypes(), self.getRegions(), limit=self._limit)

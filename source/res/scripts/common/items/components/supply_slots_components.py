# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/supply_slots_components.py
from typing import *
import ResMgr
from ResMgr import DataSection
from WeakMixin import WeakMixin
from items import ITEM_TYPES, parseIntCompactDescr, makeIntCompactDescrByID, EQUIPMENT_TYPES, vehicles
from items.basic_item import BasicItem
from items.vehicles import getItemByCompactDescr
from nations import NONE_INDEX
from soft_exception import SoftException
from supply_slot_categories import CategoriesHolder, SlotCategories
if TYPE_CHECKING:
    from items.artefacts import Equipment

class SupplySlot(CategoriesHolder):
    __slots__ = ('slotID', 'tags', '__weakref__')
    itemType = None

    def __init__(self):
        super(SupplySlot, self).__init__()
        self.slotID = None
        self.categories = set()
        self.tags = set()
        return

    def __eq__(self, other):
        return False if other is None or not isinstance(other, SupplySlot) else self.slotID == other.slotID

    def __ne__(self, other):
        return not self == other

    def readFromSection(self, section):
        self.slotID = section.readInt('id')
        categories = section.readString('categories')
        if categories:
            self.categories = set(categories.split(' '))
        self.tags = set(section.readString('tags').split(' '))
        self._readMeta(section['meta'])

    def checkSlotCompatibility(self, compDescr=None, descr=None):
        if compDescr is None and descr is None:
            raise SoftException("One of 'compDescr' or 'descr' arguments must be specified.")
        if compDescr is None:
            compDescr = descr.compactDescr
        itemTypeID, nationID, itemID = parseIntCompactDescr(compDescr)
        return (False, 'Item type of slot ({}) does not match type of item ({})'.format(self.itemType, itemTypeID)) if itemTypeID != self.itemType else self._checkSlotCompatibility((itemTypeID, nationID, itemID), descr)

    def _checkSlotCompatibility(self, parsedCompDescr=None, descr=None):
        return (True, None)

    def getSubType(self):
        return None

    @staticmethod
    def initSlot(slotSection):
        slotType = slotSection.readString('type')
        slotObj = getSlotByItemTypeName(slotType)()
        slotObj.readFromSection(slotSection)
        return slotObj

    @staticmethod
    def makeCompactDescr(itemTypeID, idxWithinItemType):
        return makeIntCompactDescrByID(itemTypeID, NONE_INDEX, idxWithinItemType)

    @staticmethod
    def parseCompactDescr(compDescr):
        itemTypeId, _, idxWithinItemType = parseIntCompactDescr(compDescr)
        return (itemTypeId, idxWithinItemType)

    def _readMeta(self, metaSection):
        pass


class OptionalDeviceSlot(SupplySlot):
    itemType = ITEM_TYPES.optionalDevice


class EquipmentSlot(SupplySlot):
    __slots__ = ('equipmentType',)
    itemType = ITEM_TYPES.equipment

    def _checkSlotCompatibility(self, parsedCompDescr=None, descr=None):
        if descr is None:
            _, _, itemID = parsedCompDescr
            descr = vehicles.g_cache.equipments()[itemID]
        return (False, 'Equipment type of slot ({}) does not match type of item ({})'.format(self.equipmentType, descr.equipmentType)) if descr.equipmentType != self.equipmentType else (True, None)

    def _readMeta(self, metaSection):
        equipmentType = metaSection.readString('equipmentType')
        self.equipmentType = EQUIPMENT_TYPES[equipmentType]

    def getSubType(self):
        return self.equipmentType


class EpicEquipmentSlot(WeakMixin):
    FL_AVATAR_TAGS = frozenset(('avatar', 'fl'))
    JOINING_TAGS = frozenset(('reconnaissance', 'tactics', 'firesupport'))

    @classmethod
    def fromEquipmentSlot(cls, equipmentSlot):
        return EpicEquipmentSlot(equipmentSlot) if isinstance(equipmentSlot, EquipmentSlot) and cls.FL_AVATAR_TAGS.issubset(equipmentSlot.tags) else None

    def _checkSlotCompatibility(self, parsedCompDescr=None, descr=None):
        res, _ = super(EpicEquipmentSlot, self)._checkSlotCompatibility(parsedCompDescr, descr)
        if not res:
            return (res, _)
        item = descr or getItemByCompactDescr(parsedCompDescr)
        return (self.tags.intersection(self.JOINING_TAGS).issubset(getattr(item, 'tags', ())), '')


class ShellSlot(SupplySlot):
    itemType = ITEM_TYPES.shell


class SupplySlotsCache(object):
    __slots__ = ('__slotDescrs', '__categories')

    def __init__(self, xmlPath=None):
        self.__slotDescrs = None
        self.__categories = None
        if xmlPath is not None:
            self.readCacheFromFile(xmlPath)
        return

    def readCacheFromFile(self, xmlPath):
        slotsSection = ResMgr.openSection(xmlPath)['slots']
        cache = {}
        for name, section in slotsSection.items():
            slotDescr = SupplySlot.initSlot(section)
            cache[slotDescr.slotID] = slotDescr

        self.__slotDescrs = cache
        self.__categories = SlotCategories.ALL

    @property
    def slotDescrs(self):
        return self.__slotDescrs

    def getSlotDescr(self, slotID):
        return self.slotDescrs[slotID]

    def getSlotDescrsByTags(self, itags=(), etags=()):
        itags, etags = set(itags), etags
        return {} if not itags.isdisjoint(etags) else {i:sd for i, sd in self.__slotDescrs.iteritems() if sd.tags.isdisjoint(etags) and bool(itags) ^ sd.tags.isdisjoint(itags)}

    @property
    def categories(self):
        return self.__categories


_ITEM_TYPE_TO_SLOT_TYPE = {t.itemType:t for t in SupplySlot.__subclasses__()}

def getSlotByItemTypeName(itemType):
    global _ITEM_TYPE_TO_SLOT_TYPE
    itemTypeID = ITEM_TYPES[itemType]
    slotType = _ITEM_TYPE_TO_SLOT_TYPE.get(itemTypeID, None)
    if slotType is not None:
        return slotType
    else:
        raise SoftException("No supplySlot for type '{}'".format(itemType))
        return

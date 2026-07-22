# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/preferred_maps.py
import itertools
import time
from abc import ABCMeta, abstractproperty
from collections import namedtuple
from enum import Enum, IntEnum, unique
from typing import TYPE_CHECKING
from constants import EMPTY_GEOMETRY_ID
from soft_exception import SoftException
if TYPE_CHECKING:
    from typing import List, Dict, Tuple, Optional, Any, Union, Iterator
BLACKLIST = 'blackList'

@unique
class SlotTypeId(IntEnum):
    DEFAULT = 1
    PREMIUM = 2
    SUBSCRB = 3
    REWARDS = 4


@unique
class SlotTypeName(str, Enum):
    DEFAULT = 'defaultSlots'
    PREMIUM = 'premiumSlots'
    SUBSCRB = 'subscrbSlots'
    REWARDS = 'rewardsSlots'


SLOT_TYPE_ID = {SlotTypeName.DEFAULT: SlotTypeId.DEFAULT,
 SlotTypeName.PREMIUM: SlotTypeId.PREMIUM,
 SlotTypeName.SUBSCRB: SlotTypeId.SUBSCRB,
 SlotTypeName.REWARDS: SlotTypeId.REWARDS}
SLOT_TYPE_NAME = {typeID:typeName for typeName, typeID in SLOT_TYPE_ID.iteritems()}

def getSlotTypeID(typeName):
    return SLOT_TYPE_ID[typeName]


def getSlotTypeName(typeID):
    if not isinstance(typeID, SlotTypeId):
        typeID = SlotTypeId(typeID)
    return SLOT_TYPE_NAME[typeID]


ALL_SLOT_TYPES = tuple(sorted((tn for tn in SlotTypeName), key=getSlotTypeID))

def getSlotsLayout(slotTypesCount, allowedTypeNames):
    layout = []
    for slotTypeName in sorted(allowedTypeNames, key=getSlotTypeID):
        count = slotTypesCount.get(SlotTypeName(slotTypeName), 0)
        if count < 1:
            continue
        while count:
            layout.append((EMPTY_GEOMETRY_ID, 0, getSlotTypeID(slotTypeName).value))
            count -= 1

    return layout


def getConfiguredSlotLayout(config):
    layout = {}
    for configuredSlotType in LayoutSlotTypeIterator(config['slots']):
        slot = configuredSlotType.makeSlot()
        layout[slot.id] = slot

    return layout


class SlotType(object):
    __metaclass__ = ABCMeta
    kind = abstractproperty(lambda *_: None)
    expire = abstractproperty(lambda *_: None)

    def __init__(self, sid, expire):
        self.__sid = sid
        self.__expire = expire

    @staticmethod
    def fromTuple(sid, kind, expire, *_):
        for klass in SlotType.__subclasses__():
            if kind == klass.kind or kind == klass.__name__:
                return klass(sid, expire)

        raise SoftException('Unknown slot type {}'.format(kind))

    @classmethod
    def isActive(cls, slot):
        raise NotImplemented

    @classmethod
    def enable(cls, slot, isEnabled=True):
        raise NotImplemented

    def makeSlot(self):
        return Slot(self.__sid, self.kind.value, EMPTY_GEOMETRY_ID, self.expire, 0)


_Slot = namedtuple('Slot', ['id',
 'type',
 'mapID',
 'expire',
 'modified'])

class DefaultSlot(SlotType):
    kind = SlotTypeId.DEFAULT
    expire = float('inf')

    @classmethod
    def isActive(cls, slot):
        return slot.mapID != EMPTY_GEOMETRY_ID

    @classmethod
    def enable(cls, slot, isEnabled=True):
        return slot if isEnabled else slot.dropMap()


class PremiumSlot(SlotType):
    kind = SlotTypeId.PREMIUM
    expire = 0

    @classmethod
    def isActive(cls, slot):
        return slot.mapID != EMPTY_GEOMETRY_ID and time.time() < slot.expire

    @classmethod
    def enable(cls, slot, isEnabled=True):
        return slot._replace(expire=float('inf') if isEnabled else 0, mapID=EMPTY_GEOMETRY_ID, modified=0)


class SubscrbSlot(SlotType):
    kind = SlotTypeId.SUBSCRB
    expire = 0

    @classmethod
    def isActive(cls, slot):
        return slot.mapID != EMPTY_GEOMETRY_ID and time.time() < slot.expire

    @classmethod
    def enable(cls, slot, isEnabled=True):
        return slot._replace(expire=float('inf') if isEnabled else 0, mapID=EMPTY_GEOMETRY_ID, modified=0)


class RewardSlot(SlotType):
    kind = SlotTypeId.REWARDS
    expire = 0

    @classmethod
    def isActive(cls, slot):
        return slot.mapID != EMPTY_GEOMETRY_ID and time.time() < slot.expire

    @classmethod
    def enable(cls, slot, isEnabled=True):
        return slot if isEnabled else slot.dropMap()


class LayoutSlotTypeIterator(object):

    def __init__(self, configuredLayoutData):
        self._data = configuredLayoutData

    def __iter__(self):
        return (SlotType.fromTuple(*d) for d in self._data.itervalues())


class Slot(_Slot):

    def isActive(self):
        return self.slotType.isActive(self) and self.isEnabled()

    def isEnabled(self):
        return time.time() < self.expire

    def isEmpty(self):
        return self.mapID == EMPTY_GEOMETRY_ID

    @property
    def slotType(self):
        for k in SlotType.__subclasses__():
            if k.kind.value == self.type:
                return k

    def enable(self, isEnabled=True):
        return self.slotType.enable(self, isEnabled) if self.isEnabled() != isEnabled else self

    def dropMap(self):
        return self._replace(mapID=EMPTY_GEOMETRY_ID, modified=0)

    def as_tuple(self):
        return tuple(self)


class BlacklistSlotIterator(object):

    def __init__(self, blacklistData):
        self._data = blacklistData

    def __iter__(self):
        return (Slot(*i) for i in self._data.itervalues())


class BlacklistSlotUpdateIterator(object):

    def __init__(self, blacklistUpdateData):
        self._data = blacklistUpdateData

    def __iter__(self):
        data = self._data
        return (Slot(slotID, kind, mapID, 0, 0) for slotID, kind, mapID in itertools.izip(itertools.islice(data, 0, None, 3), itertools.islice(data, 1, None, 3), itertools.islice(data, 2, None, 3)))


class BlacklistWrapper(object):

    @property
    def isChanged(self):
        return bool(self.__changed)

    def __init__(self, blacklist):
        self.__blacklistData = blacklist
        self.__changed = {}

    def getMapList(self):
        return [ self[slotId].mapID for slotId in self.iterkeys() if self[slotId].isActive() ]

    def __getitem__(self, key):
        return Slot(*(self.__changed.get(key) or self.__blacklistData[key]))

    def __setitem__(self, key, value):
        if not isinstance(value, Slot):
            raise ValueError
        if value != self.get(key):
            self.__changed[key] = tuple(value)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def get_key_diff(self, key):
        return (self.__blacklistData.get(key), self.__changed.get(key))

    def iterkeys(self):
        seen = set()
        for k in itertools.chain(self.__changed, self.__blacklistData):
            if k not in seen:
                seen.add(k)
                yield k

    def as_dict(self):
        return {k:self.__changed.get(k) or self.__blacklistData[k] for k in self.iterkeys()}

    def diff(self):
        return {k:Slot(*v) for k, v in self.__changed.iteritems()}

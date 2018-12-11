# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/ny_readers.py
import typing
import ResMgr
import contextlib
from constants import IS_CLIENT
from soft_exception import SoftException
from items.components.ny_components import VariadicDiscount, LevelDescriptor, SlotDescriptor
from items.components.ny_constants import MAX_ATMOSPHERE_LEVEL, MIN_ATMOSPHERE_LEVEL, TOY_TYPES, TOY_OBJECTS_IDS_BY_NAME, TOY_SETTING_IDS_BY_NAME

@contextlib.contextmanager
def openSection(path):
    try:
        yield ResMgr.openSection(path)
    finally:
        ResMgr.purge(path)


def _readLevelRewardSection(section):
    cfg = {'id': section.readString('id')}
    cfg['level'] = level = section.readInt('level')
    if not MIN_ATMOSPHERE_LEVEL <= level <= MAX_ATMOSPHERE_LEVEL:
        raise SoftException("Wrong reward level '%d'" % level)
    return cfg


def readLevelRewards(xmlPath):
    cache = {}
    with openSection(xmlPath) as section:
        if section is None:
            raise SoftException("Can't open '%s'" % xmlPath)
        for levelSec in section.values():
            cfg = _readLevelRewardSection(levelSec)
            rewardID = cfg['id']
            if rewardID in cache:
                raise SoftException("Repeated boxID '%s'" % rewardID)
            cache[rewardID] = LevelDescriptor(cfg)

    return cache


def readCollectionRewards(xmlPath):
    cache = {}
    with openSection(xmlPath) as section:
        if section is None:
            raise SoftException("Can't open '%s'" % xmlPath)
        for reward in section.values():
            rewardID = reward.readString('id')
            collName = reward.readString('collection')
            collID = TOY_SETTING_IDS_BY_NAME.get(collName, -1)
            if rewardID in cache:
                raise SoftException("Repeated boxID '%s'" % rewardID)
            cache[rewardID] = collID
            cache[collID] = rewardID
            cache[collName] = rewardID

    return cache


def _readVariadicDiscountSection(section):
    cfg = {}
    cfg['id'] = section.readString('id')
    startRange = section['goodiesRange'].readInt('start')
    endRange = section['goodiesRange'].readInt('end')
    cfg['goodiesRange'] = (startRange, endRange)
    cfg['level'] = level = section.readInt('level')
    if not MIN_ATMOSPHERE_LEVEL <= level <= MAX_ATMOSPHERE_LEVEL:
        raise SoftException("Wrong reward level '%d'" % level)
    return cfg


def readVariadicDiscounts(xmlPath):
    cache = {}
    with openSection(xmlPath) as section:
        if section is None:
            raise SoftException("Can't open '%s'" % xmlPath)
        for vdSec in section.values():
            cfg = _readVariadicDiscountSection(vdSec)
            vdID = cfg['id']
            if vdID in cache:
                raise SoftException("Repeated variadic discount ID '%s'" % vdID)
            cache[vdID] = VariadicDiscount(**cfg)

    return cache


def _readSlotSection(section):
    cfg = {'id': section.readInt('id')}
    cfg['type'] = slotType = section.readString('type')
    if slotType not in TOY_TYPES:
        raise SoftException("Wrong slot type '%s'" % slotType)
    if IS_CLIENT:
        cfg['object'] = section.readString('object')
        cfg['nodes'] = section.readString('nodes')
        cfg['direction'] = section.readString('direction')
        cfg['selectable'] = section.readBool('selectable')
        cfg['defaultToy'] = section.readInt('defaultToy', -1)
    return cfg


def readSlots(xmlPath):
    cache = None
    with openSection(xmlPath) as section:
        if section is None:
            raise SoftException("Can't open '%s'" % xmlPath)
        subsections = section['slots'].values()
        numSlots = len(subsections)
        cache = [None] * numSlots
        for slotSec in subsections:
            cfg = _readSlotSection(slotSec)
            slotID = cfg['id']
            if not 0 <= slotID < numSlots:
                raise SoftException("Wrong slotID '%d'" % slotID)
            if cache[slotID] is not None:
                raise SoftException("Repeated slotID '%d'" % slotID)
            cache[slotID] = SlotDescriptor(cfg)

    return cache

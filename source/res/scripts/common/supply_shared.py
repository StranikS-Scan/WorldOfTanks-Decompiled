# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/supply_shared.py
import typing
if typing.TYPE_CHECKING:
    from typing import Iterable

class Supply(object):
    PILLBOX = 1
    MORTAR = 2
    FLAMER = 3
    AIRSHIP = 4
    ALL = (PILLBOX,
     MORTAR,
     FLAMER,
     AIRSHIP)
    SELF_REPAIRABLE = {MORTAR, PILLBOX, FLAMER}
    NAME_TO_SUPPLY = {'pillbox': PILLBOX,
     'mortar': MORTAR,
     'flamer': FLAMER,
     'airship': AIRSHIP}
    SUPPLY_ID_TO_NAME = dict(((supplyID, name) for name, supplyID in NAME_TO_SUPPLY.iteritems()))
    TAG_TO_SUPPLY = {'supply_Pillbox': PILLBOX,
     'supply_Mortar': MORTAR,
     'supply_Flamer': FLAMER,
     'supply_Airship': AIRSHIP}
    SUPPLY_ID_TO_TAG = dict(((supplyID, classTag) for classTag, supplyID in TAG_TO_SUPPLY.iteritems()))
    SUPPLY_TAG_LIST = frozenset(TAG_TO_SUPPLY.keys())

    @classmethod
    def getID(cls, vehicleType):
        for tag in vehicleType.tags:
            supplyID = cls.TAG_TO_SUPPLY.get(tag)
            if supplyID is not None and supplyID in cls.ALL:
                return supplyID

        return

    @classmethod
    def getSupplyTag(cls, vehicleType):
        for tag in vehicleType.tags:
            supplyID = cls.TAG_TO_SUPPLY.get(tag)
            if supplyID is not None and supplyID in cls.ALL:
                return tag

        return

    @classmethod
    def isPillbox(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.PILLBOX] in tags

    @classmethod
    def isMortar(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.MORTAR] in tags

    @classmethod
    def isFlamer(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.FLAMER] in tags

    @classmethod
    def isAirShip(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.AIRSHIP] in tags

    @classmethod
    def isSupply(cls, tags):
        return 'supply' in tags

    @classmethod
    def getSupplyType(cls, tags):
        for tag in tags:
            if tag in cls.TAG_TO_SUPPLY:
                return cls.TAG_TO_SUPPLY[tag]

        return None

    @classmethod
    def isSelfRepair(cls, vehicleType):
        supplyID = cls.getID(vehicleType)
        return supplyID in cls.SELF_REPAIRABLE if supplyID is not None else False

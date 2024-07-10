# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bonus_caps_overrides.py
from typing import TYPE_CHECKING, Optional, Dict, Set
from BonusCaps import BonusCapsConst
from arena_bonus_type_caps import ALLOWED_ARENA_BONUS_TYPE_CAPS
from constants import ARENA_BONUS_TYPE_NAMES
from soft_exception import SoftException
if TYPE_CHECKING:
    from ResMgr import DataSection

def readBonusCapsOverrides(section):
    overrides = dict()
    if section is None:
        return overrides
    else:
        for name, data in section.items():
            if ARENA_BONUS_TYPE_NAMES.get(name, None) is None:
                raise SoftException('Invalid arena type {}'.format(name))
            nameID = ARENA_BONUS_TYPE_NAMES.get(name, None)
            if nameID is None:
                raise SoftException('Incorrect arena type name: {}'.format(name))
            if nameID in overrides:
                raise SoftException('Duplicate arena type: {}'.format(name))
            overrides[nameID] = _readOperations(data)

        return overrides


def _readOperations(section):
    operations = dict()
    if section is None:
        return operations
    else:
        for operation in (BonusCapsConst.REMOVE, BonusCapsConst.ADD, BonusCapsConst.OVERRIDE):
            options = set(section.readString(operation, '').split())
            if options:
                operations[operation] = options

        if operations.get(BonusCapsConst.REMOVE, set()) and operations.get(BonusCapsConst.ADD, set()):
            if operations[BonusCapsConst.REMOVE] & operations[BonusCapsConst.ADD]:
                raise SoftException('Same bonus types in add and remove sections: {}'.format(operations[BonusCapsConst.REMOVE] & operations[BonusCapsConst.ADD]))
        if operations.get(BonusCapsConst.OVERRIDE, None) and (operations.get(BonusCapsConst.REMOVE, None) or operations.get(BonusCapsConst.ADD, None)):
            raise SoftException('Invalid params to apply to arena bonus types: may use remove and add or override operations')
        for category, bonusTypes in operations.iteritems():
            for bonusType in bonusTypes:
                if bonusType not in ALLOWED_ARENA_BONUS_TYPE_CAPS:
                    raise SoftException('Invalid bonus type: bonusType={} is not in allowed list, category={}'.format(bonusType, category))

        return operations

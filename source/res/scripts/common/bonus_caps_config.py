# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bonus_caps_config.py
from arena_bonus_type_caps import ALLOWED_ARENA_BONUS_TYPE_CAPS
from constants import ARENA_BONUS_TYPE_NAMES
from soft_exception import SoftException
import ResMgr
from typing import Dict, Optional, FrozenSet
_CONFIG_FILE = 'scripts/item_defs/bonus_caps_config.xml'

def readConfig(verbose=False):
    section = ResMgr.openSection(_CONFIG_FILE)['']
    return _readArenaTypes(section)


def _readArenaTypes(section):
    config = dict()
    if section is None:
        return config
    else:
        for name, data in section.items():
            if ARENA_BONUS_TYPE_NAMES.get(name, None) is None:
                raise SoftException('Unknown arena type {}'.format(name))
            nameID = ARENA_BONUS_TYPE_NAMES.get(name, None)
            if nameID is None:
                raise SoftException('Incorrect arena type name: {}'.format(name))
            if nameID in config:
                raise SoftException('Duplicate arena type: {}'.format(name))
            config[nameID] = _readBonuses(data)

        missedArenaTypes = []
        for arenaType, arenaTypeID in ARENA_BONUS_TYPE_NAMES.iteritems():
            if arenaTypeID not in config and isinstance(arenaTypeID, int):
                missedArenaTypes.append(arenaType)

        if missedArenaTypes:
            raise SoftException('Some arena types was missed: {}'.format(missedArenaTypes))
        return config


def _readBonuses(data):
    caps = frozenset()
    if data is None:
        return caps
    else:
        caps = frozenset(data.readString('').split())
        for bonusType in caps:
            if bonusType not in ALLOWED_ARENA_BONUS_TYPE_CAPS:
                raise SoftException("Invalid bonus type: bonusType='{}' is not in allowed list".format(bonusType))

        return caps

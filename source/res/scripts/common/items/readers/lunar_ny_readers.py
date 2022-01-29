# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/lunar_ny_readers.py
import contextlib
import items._xml as ix
from constants import IS_CLIENT, IS_EDITOR
from soft_exception import SoftException
from items.components.lunar_ny_constants import CharmType, CharmBonusMsk, CharmBonuses
from items.components.lunar_ny_components import CharmDescriptor
if IS_CLIENT or IS_EDITOR:
    import ResMgr
else:
    from realm_utils import ResMgr

@contextlib.contextmanager
def openSection(path):
    try:
        yield ResMgr.openSection(path)
    finally:
        ResMgr.purge(path)


def _readCharmSections(section):
    for sectionName, subsection in section.items():
        if 'xmlns:xmlref' == sectionName or 0 == len(subsection):
            continue
        cfg = {}
        charm = CharmDescriptor(cfg)
        cfg['id'] = ix.readNonNegativeInt(None, subsection, 'id')
        cfg['type'] = charmType = ix.readString(None, subsection, 'type')
        if charmType not in CharmType.ALL:
            raise SoftException("Wrong charm type '%s'" % charmType)
        if not subsection.has_key('bonuses'):
            raise SoftException('Charm does not contain bonuses section')
        bonuses = subsection['bonuses']
        for bonus in list(CharmBonuses):
            name, value = bonus.name, bonus.value
            if bonuses.has_key(value):
                cfg['bonuses'][value] = round(ix.readNonNegativeFloat(None, bonuses, value), 4)
                cfg['bonusMsk'] |= CharmBonusMsk.getMskByName(name)

        if not 0 < charm.numBonuses() < 3:
            raise SoftException('Bonuses must contain at least one but no more than two sections of the bonus factor')
        if charmType == CharmType.RARE:
            cfg['decalId'] = ix.readIntOrNone(None, subsection, 'decalId')
        yield charm

    return


def readCharm(xmlPath):
    cache = {}
    with openSection(xmlPath) as section:
        if section is None:
            raise SoftException("Can't open '%s'" % xmlPath)
        for charm in _readCharmSections(section):
            id = charm.id
            if id in cache:
                raise SoftException("Repeated charm id '%s'" % id)
            cache[id] = charm

    return cache

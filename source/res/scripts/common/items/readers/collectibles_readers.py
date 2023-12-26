# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/collectibles_readers.py
import BigWorld
from items.components.ny_constants import MIN_TOY_RANK, YEARS_INFO, YEARS, ToyDropSources
from ny_common.ny_exception import NYSoftException

def _readCollections(section):
    cfg = {}
    for name, subsection in section.items():
        cfg[name] = _readCollection(subsection)

    return cfg


def _readCollection(section):
    cfg = {intern('isEnabled'): False,
     intern('toys'): {}}
    domains = section.readString('domains', '')
    if not domains:
        return cfg
    domainList = domains.split()
    if BigWorld.component not in domainList:
        return cfg
    isEnabled = cfg['isEnabled'] = section.readBool('isEnabled', False)
    if not isEnabled:
        return cfg
    cfg['toys'] = _readToys(section['toys'], section.name)
    return cfg


def _readToys(section, collectionName=None):
    cfg = {}
    for name, subsection in section.items():
        toy = _readToy(subsection, collectionName)
        cfg[toy['id']] = toy

    return cfg


def _readToy(section, collectionName=None):
    cfg = {intern('collection'): collectionName} if collectionName else {}
    toyData = {intern(name):(section.readInt(name) if name in ('id', 'rank') else intern(section.readString(name))) for name, subsection in section.items()}
    if collectionName and collectionName != 'defaultToys':
        if not MIN_TOY_RANK <= toyData['rank'] <= YEARS_INFO.getMaxToyRankByYear(collectionName):
            raise NYSoftException('Invalid toy rank, toy collection:{}, toy id: {}'.format(collectionName, toyData['id']))
        if toyData['setting'] not in YEARS_INFO.getCollectionTypesByYear(collectionName):
            raise NYSoftException('Invalid setting, toy collection:{}, toy id: {}'.format(collectionName, toyData['id']))
        if collectionName == YEARS_INFO.CURRENT_YEAR_STR:
            if toyData['dropSource'] not in ToyDropSources.ALL:
                raise NYSoftException('Invalid dropSource {}'.format(toyData['dropSource']))
    cfg.update(toyData)
    return cfg

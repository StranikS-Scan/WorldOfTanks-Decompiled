# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/common/new_year_common/items/readers/collectibles_readers.py
import BigWorld
from new_year_common.items.components.ny_constants import MIN_TOY_RANK, YEARS_INFO
from new_year_common.ny_exception import NYSoftException
TOY_PRICE_CURRENCY = ('gold',)

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
    for subsection in section.values():
        toy = _readToy(subsection, collectionName)
        cfg[toy['id']] = toy

    return cfg


def _readToy(section, collectionName=None):
    cfg = {intern('collection'): collectionName} if collectionName else {}
    toyData = {intern(name):(section.readInt(name) if name in ('id', 'rank') else intern(section.readString(name))) for name, subsection in section.items()}
    if section.has_key('price'):
        price = _readToyPrice(section['price'])
        toyData.update(price)
    if collectionName and collectionName != 'defaultToys':
        if not MIN_TOY_RANK <= toyData['rank'] <= YEARS_INFO.getMaxToyRankByYear(collectionName):
            raise NYSoftException('Invalid toy rank, toy collection:{}, toy id: {}'.format(collectionName, toyData['id']))
        if toyData['setting'] not in YEARS_INFO.getCollectionTypesByYear(collectionName):
            raise NYSoftException('Invalid setting, toy collection:{}, toy id: {}'.format(collectionName, toyData['id']))
    cfg.update(toyData)
    return cfg


def _readToyPrice(section):
    result = {}
    for name in section.keys():
        if name not in TOY_PRICE_CURRENCY:
            raise NYSoftException('Invalid toy currency: {}'.format(name))
        if name in result:
            raise NYSoftException('Duplicated currency: {}'.format(name))
        value = section.readInt(name)
        if value <= 0:
            raise NYSoftException('Invalid price value: {}'.format(value))
        result[intern(name)] = value

    return {intern('price'): result}

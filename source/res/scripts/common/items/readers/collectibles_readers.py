# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/collectibles_readers.py
import BigWorld

def _readCollections(section):
    cfg = {}
    for name, subsection in section.items():
        cfg[name] = _readCollection(subsection)

    return cfg


def _readCollection(section):
    cfg = {'isEnabled': False,
     'toys': {}}
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
    cfg = {'collection': collectionName} if collectionName else {}
    cfg.update(((name, section.readInt(name) if str(name) in ('id', 'rank') else section.readString(name)) for name, subsection in section.items()))
    return cfg

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/perks_readers.py
import ResMgr
import os
from items import _xml
from items.components import perks_constants
from items.components.perks_components import Perk, PerksBranch

def _readPerkItem(xmlCtx, section, storage):
    perkID = _xml.readInt(xmlCtx, section, 'id', 1)
    name = _xml.readStringOrEmpty(xmlCtx, section, 'name')
    description = _xml.readNonEmptyString(xmlCtx, section, 'description')
    icon = _xml.readNonEmptyString(xmlCtx, section, 'icon')
    branchID = _xml.readInt(xmlCtx, section, 'branchID', 0)
    ultimative = section.readBool('ultimative', False)
    maxCount = _xml.readInt(xmlCtx, section, 'maxCount', 1)
    situational = _xml.readBool(xmlCtx, section, 'situational', False)
    perkItem = Perk(perkID, name, description, icon, branchID, ultimative, maxCount, situational)
    storage[perkID] = perkItem


def _readBranchItem(xmlCtx, section, storage):
    perkID = _xml.readInt(xmlCtx, section, 'id', 1)
    name = _xml.readStringOrEmpty(xmlCtx, section, 'name')
    needPoints = section.readInt('needPoints', 0)
    perkItem = PerksBranch(perkID, name, needPoints)
    storage[perkID] = perkItem


def _readPerksCacheFromXMLSection(xmlCtx, section, sectionName, storage):
    if sectionName not in PERKS_READERS:
        _xml.raiseWrongXml(xmlCtx, sectionName, 'unknown section')
    reader = PERKS_READERS[sectionName]
    for i, (gname, gsection) in enumerate(section.items()):
        if gname != sectionName:
            continue
        reader(xmlCtx, gsection, storage)


PERKS_READERS = {'perk': _readPerkItem,
 'branch': _readBranchItem}

def readPerksCacheFromXML(cache, folder):
    xmlCtx = (None, perks_constants.PERKS_XML_FILE)
    pgFile = os.path.join(folder, perks_constants.PERKS_XML_FILE)
    _readPerksCacheFromXMLSection(xmlCtx, ResMgr.openSection(pgFile), 'perk', cache.perks)
    _readPerksCacheFromXMLSection(xmlCtx, ResMgr.openSection(pgFile), 'branch', cache.branches)
    cache.attachPerksToBranches()
    ResMgr.purge(pgFile)
    return

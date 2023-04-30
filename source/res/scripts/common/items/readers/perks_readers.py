# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/perks_readers.py
import os
from collections import OrderedDict
import typing
import ResMgr
from items import _xml
from items.components import perks_constants
from items.components.perks_components import Perk, PerkArgument
from items.components.perks_constants import PerkTags

def _readPerkArguments(xmlCtx, section):
    argsDict = OrderedDict()
    argsSection = _xml.getSubsection(xmlCtx, section, 'defaultBlockSettings', throwIfMissing=False)
    if argsSection:
        for _, argSection in argsSection.items():
            argId = _xml.readString(xmlCtx, argSection, 'argId')
            value = argSection.readFloat('value', 0.0)
            postValues = map(float, _xml.readStringOrEmpty(xmlCtx, argSection, 'postValues').split())
            argsDict[argId] = PerkArgument(value, postValues)

    return argsDict


def _readPerkItem(xmlCtx, section, storage):
    perkID = _xml.readInt(xmlCtx, section, 'id', 1)
    flags = PerkTags.pack(_xml.readStringOrEmpty(xmlCtx, section, 'tags').split())
    args = _readPerkArguments(xmlCtx, section)
    storage[perkID] = Perk(perkID, flags, args)


def _readPerksCacheFromXMLSection(xmlCtx, section, sectionName, storage):
    if sectionName not in PERKS_READERS:
        _xml.raiseWrongXml(xmlCtx, sectionName, 'unknown section')
    reader = PERKS_READERS[sectionName]
    for i, (gname, gsection) in enumerate(section.items()):
        if gname != sectionName:
            continue
        reader(xmlCtx, gsection, storage)


PERKS_READERS = {'perk': _readPerkItem}

def readPerksCacheFromXML(cache, folder):
    xmlCtx = (None, perks_constants.PERKS_XML_FILE)
    pgFile = os.path.join(folder, perks_constants.PERKS_XML_FILE)
    _readPerksCacheFromXMLSection(xmlCtx, ResMgr.openSection(pgFile), 'perk', cache)
    ResMgr.purge(pgFile)
    return

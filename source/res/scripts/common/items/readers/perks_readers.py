# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/perks_readers.py
import os
import typing
from collections import OrderedDict
import ResMgr
from items import _xml
from items.components import perks_constants
from items.components.perks_components import Perk, PerkArgument, PerkArgumentUISettings
from items.components.perks_constants import PerkTags
from constants import IS_CLIENT, IS_WEB
if typing.TYPE_CHECKING:
    from items.components.perks_components import PerksCache

def _readPerkArguments(xmlCtx, section):
    argsSection = _xml.getSubsection(xmlCtx, section, 'defaultBlockSettings', throwIfMissing=False)
    if not argsSection:
        return {}
    else:
        argsDict = OrderedDict()
        argTypesMapping = perks_constants.PerksValueType.CONFIGURATION_MAPPING
        for _, argSection in argsSection.items():
            argId = _xml.readString(xmlCtx, argSection, 'argId')
            value = argSection.readFloat('value', 0.0)
            postValues = map(float, _xml.readStringOrEmpty(xmlCtx, argSection, 'postValues').split())
            maxStacks = argSection.readInt('maxStacks', 1)
            diminishingStartsAfter = argSection.readInt('diminishing_starts_after', 10)
            perkArgUISettings = None
            if IS_CLIENT or IS_WEB:
                argUISettingsSection = _xml.getSubsection(xmlCtx, argSection, 'UISettings', throwIfMissing=False)
                if argUISettingsSection:
                    valueTypeName = _xml.readStringOrEmpty(xmlCtx, argUISettingsSection, 'type')
                    argType = argTypesMapping[valueTypeName]
                    revert = _xml.readBool(xmlCtx, argUISettingsSection, 'revert', default=False)
                    situationalArg = _xml.readBool(xmlCtx, argUISettingsSection, 'situationalArg', False)
                    equipmentCooldown = _xml.readStringOrNone(xmlCtx, argUISettingsSection, 'equipmentCooldown')
                    localeFormatting = _xml.readStringOrEmpty(xmlCtx, argUISettingsSection, 'localeFormatting')
                    perkTooltipBonus = _xml.readBool(xmlCtx, argUISettingsSection, 'perkTooltipBonus', False)
                    icon = _xml.readStringOrNone(xmlCtx, argUISettingsSection, 'icon')
                    perkArgUISettings = PerkArgumentUISettings(argType, revert, situationalArg, equipmentCooldown, localeFormatting, perkTooltipBonus, icon)
            argsDict[argId] = PerkArgument(value, postValues, diminishingStartsAfter, maxStacks, perkArgUISettings)

        return argsDict


def _readPerkItem(xmlCtx, section, storage):
    perkID = _xml.readInt(xmlCtx, section, 'id', 1)
    flags = PerkTags.pack(_xml.readStringOrEmpty(xmlCtx, section, 'tags').split())
    ultimative = section.readBool('ultimative', False)
    situational = _xml.readBool(xmlCtx, section, 'situational', False)
    args = _readPerkArguments(xmlCtx, section)
    storage[perkID] = Perk(perkID, flags, ultimative, situational, args)


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
    _readPerksCacheFromXMLSection(xmlCtx, ResMgr.openSection(pgFile), 'perk', cache.perks)
    ResMgr.purge(pgFile)
    return

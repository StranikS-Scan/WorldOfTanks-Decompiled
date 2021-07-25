# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/crewSkins_readers.py
import ResMgr
import nations
import os
from constants import REGIONAL_REALMS
from items import _xml
from items import vehicles
from items.components import skills_constants, crew_skins_constants
from items.components import tankmen_components
import items.components.crew_skins_components as cc

def _readPriceForItem(pricesDest, xmlCtx, section, compactDescr):
    if pricesDest is not None:
        pricesDest['itemPrices'][compactDescr] = _xml.readPrice(xmlCtx, section, 'price')
        if section.readBool('notInShop', False):
            pricesDest['notInShopItems'].add(compactDescr)
    return


def _copyPriceForItem(pricesDest, sourceCompactDescr, destCompactDescr, itemNotInShop):
    if pricesDest is not None:
        pricesDest['itemPrices'][destCompactDescr] = pricesDest['itemPrices'].getPrices(sourceCompactDescr)
        if itemNotInShop or sourceCompactDescr in pricesDest['notInShopItems']:
            pricesDest['notInShopItems'].add(destCompactDescr)
    return


def _readPriceGroups(pricesCache, cache, xmlCtx, section, sectionName):
    for tag, iSection in section.items():
        if tag != sectionName:
            continue
        priceGroup = cc.PriceGroup()
        priceGroup.id = _xml.readInt(xmlCtx, iSection, 'id', 1)
        iCtx = (xmlCtx, 'id %s' % priceGroup.id)
        if priceGroup.id in cache.priceGroups:
            _xml.raiseWrongXml(iCtx, 'id', 'duplicate price group id')
        priceGroup.name = intern(_xml.readString(iCtx, iSection, 'name'))
        if priceGroup.name in cache.priceGroupNames:
            _xml.raiseWrongXml(iCtx, 'id', 'duplicate price group name "%s"' % priceGroup.name)
        priceGroup.notInShop = iSection.readBool('notInShop', False)
        _readPriceForItem(pricesCache, iCtx, iSection, priceGroup.compactDescr)
        if iSection.has_key('tags'):
            tags = iSection.readString('tags').split()
            priceGroup.tags = frozenset(map(intern, tags))
            for tag in priceGroup.tags:
                cache.priceGroupTags.setdefault(tag, []).append(priceGroup)

        cache.priceGroupNames[priceGroup.name] = priceGroup.id
        cache.priceGroups[priceGroup.id] = priceGroup


def _readGroupTags(xmlCtx, section, subsectionName):
    source = _xml.readStringOrNone(xmlCtx, section, subsectionName)
    if source is not None:
        tags = source.split()
        restrictions = []
        for tag in tags:
            if not (tag in tankmen_components.GROUP_TAG.RANGE or vehicles.g_list.isVehicleExisting(tag)):
                _xml.raiseWrongXml(xmlCtx, subsectionName, 'unknown tag "{}"'.format(tag))
            if tag in tankmen_components.GROUP_TAG.RESTRICTIONS:
                restrictions.append(tag)

        if restrictions and tankmen_components.GROUP_TAG.PASSPORT_REPLACEMENT_FORBIDDEN not in restrictions:
            _xml.raiseWrongXml(xmlCtx, subsectionName, 'Group contains tags of restrictions {}, so tag "{}" is mandatory'.format(restrictions, tankmen_components.GROUP_TAG.PASSPORT_REPLACEMENT_FORBIDDEN))
    else:
        tags = []
    return frozenset(tags)


def _readSkinItem(pricesCache, cache, xmlCtx, section, storage):
    skinID = _xml.readInt(xmlCtx, section, 'id', 1)
    if skinID in storage:
        _xml.raiseWrongXml(xmlCtx, 'id', "duplicate id '%s'" % skinID)
    priceGroup = section.readString('priceGroup')
    tags = _readGroupTags((xmlCtx, 'tags'), section, 'tags')
    firstNameID = _xml.readStringOrEmpty(xmlCtx, section, 'firstName')
    lastNameID = _xml.readNonEmptyString(xmlCtx, section, 'lastName')
    description = _xml.readNonEmptyString(xmlCtx, section, 'description')
    iconID = _xml.readNonEmptyString(xmlCtx, section, 'icon')
    rarity = _xml.readInt(xmlCtx, section, 'rarity', 1)
    maxCount = _xml.readInt(xmlCtx, section, 'maxCount')
    soundSetID = section.readString('soundSet', crew_skins_constants.NO_CREW_SKIN_SOUND_SET)
    historical = _xml.readInt(xmlCtx, section, 'historical') == 0
    realmsStr = section.readString('realms', '')
    realms = realmsStr.split()
    unexpectedRealms = set(realms) - REGIONAL_REALMS
    if unexpectedRealms:
        _xml.raiseWrongXml(xmlCtx, 'realms', "unknown realms '%s'" % unexpectedRealms)
    crewSkinItem = cc.CrewSkin(skinID, priceGroup, firstNameID, lastNameID, iconID, description, rarity, maxCount, tags, historical, soundSetID, realms)
    if section.has_key('filters'):
        filterSection = _xml.getSubsection(xmlCtx, section, 'filters')
        if filterSection.has_key('role'):
            roleName = filterSection.readString('role')
            if roleName not in skills_constants.ROLES:
                _xml.raiseWrongXml(xmlCtx, 'role', "unknown tankmanRole '%s'" % roleName)
            crewSkinItem.roleID = roleName if roleName else None
        if filterSection.has_key('nation'):
            nation = filterSection.readString('nation', '')
            if nation and nation not in nations.NAMES:
                _xml.raiseWrongXml(xmlCtx, 'nation', "unknown nation '%s'" % nation)
            crewSkinItem.nation = nation if nation else None
        if filterSection.has_key('sex'):
            sex = filterSection.readString('sex', '')
            if sex not in crew_skins_constants.TANKMAN_SEX.AVAILABLE:
                _xml.raiseWrongXml(xmlCtx, 'sex', "unknown tankman sex '%s'" % sex)
            crewSkinItem.sex = sex
    storage[skinID] = crewSkinItem
    groupsDict = cache.priceGroups
    itemToGroup = cache.itemToPriceGroup
    if crewSkinItem.priceGroup:
        if crewSkinItem.priceGroup not in cache.priceGroupNames:
            _xml.raiseWrongXml(xmlCtx, 'priceGroup', 'unknown price group %s for item %s' % (crewSkinItem.priceGroup, crewSkinItem.id))
        priceGroupId = cache.priceGroupNames[crewSkinItem.priceGroup]
        crewSkinItem.priceGroupTags = groupsDict[priceGroupId].tags
        itemToGroup[crewSkinItem.compactDescr] = groupsDict[priceGroupId].compactDescr
        itemNotInShop = section.readBool('notInShop', False)
        _copyPriceForItem(pricesCache, groupsDict[priceGroupId].compactDescr, crewSkinItem.compactDescr, itemNotInShop)
    else:
        _xml.raiseWrongXml(xmlCtx, 'priceGroup', 'no price for item %s' % crewSkinItem.id)
    return


def _readCrewSkinsCacheFromXMLSection(pricesCache, cache, xmlCtx, section, sectionName, storage):
    for i, (gname, gsection) in enumerate(section.items()):
        if gname != sectionName:
            continue
        _readSkinItem(pricesCache, cache, xmlCtx, gsection, storage)


def readCrewSkinsCacheFromXML(pricesCache, cache, folder):
    pgFile = os.path.join(folder, crew_skins_constants.CREW_SKINS_PRICE_GROUPS_XML_FILE)
    _readPriceGroups(pricesCache, cache, (None, crew_skins_constants.CREW_SKINS_PRICE_GROUPS_XML_FILE), ResMgr.openSection(pgFile), 'priceGroup')
    ResMgr.purge(pgFile)
    pgFile = os.path.join(folder, crew_skins_constants.CREW_SKINS_XML_FILE)
    _readCrewSkinsCacheFromXMLSection(pricesCache, cache, (None, crew_skins_constants.CREW_SKINS_XML_FILE), ResMgr.openSection(pgFile), 'crewSkin', cache.skins)
    ResMgr.purge(pgFile)
    return

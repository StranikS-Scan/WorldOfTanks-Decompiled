# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/crewBooks_readers.py
import ResMgr
import nations
import os
from items import _xml
from items import vehicles
from items.components import crew_books_constants
from items.components import tankmen_components
import items.components.crew_books_components as cb

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
        priceGroup = cb.PriceGroup()
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


def _readBookItem(pricesCache, cache, xmlCtx, section, storage):
    bookID = _xml.readInt(xmlCtx, section, 'id', 1)
    priceGroup = section.readString('priceGroup')
    tags = _readGroupTags((xmlCtx, 'tags'), section, 'tags')
    nameID = _xml.readStringOrEmpty(xmlCtx, section, 'name')
    descriptionID = _xml.readStringOrEmpty(xmlCtx, section, 'description')
    iconID = _xml.readNonEmptyString(xmlCtx, section, 'icon')
    type = _xml.readNonEmptyString(xmlCtx, section, 'type')
    if type not in crew_books_constants.CREW_BOOK_RARITY.ALL_TYPES:
        _xml.raiseWrongXml(xmlCtx, 'type', "unknown crew book rarity type '%s'" % type)
    crewBookItem = cb.CrewBook(bookID, priceGroup, nameID, descriptionID, iconID, type, tags)
    if section.has_key('filters'):
        filterSection = _xml.getSubsection(xmlCtx, section, 'filters')
        if filterSection.has_key('nation'):
            nation = filterSection.readString('nation', '')
            if nation and nation not in nations.NAMES:
                _xml.raiseWrongXml(xmlCtx, 'nation', "unknown nation '%s'" % nation)
            crewBookItem.nation = nation if nation else None
    if not crewBookItem.nation and type != crew_books_constants.CREW_BOOK_RARITY.PERSONAL:
        _xml.raiseWrongXml(xmlCtx, 'nation', "crew book with rarity type '%s' should have nation" % type)
    storage[bookID] = crewBookItem
    groupsDict = cache.priceGroups
    itemToGroup = cache.itemToPriceGroup
    if crewBookItem.priceGroup:
        if crewBookItem.priceGroup not in cache.priceGroupNames:
            _xml.raiseWrongXml(xmlCtx, 'priceGroup', 'unknown price group %s for item %s' % (crewBookItem.priceGroup, crewBookItem.id))
        priceGroupId = cache.priceGroupNames[crewBookItem.priceGroup]
        crewBookItem.priceGroupTags = groupsDict[priceGroupId].tags
        itemToGroup[crewBookItem.compactDescr] = groupsDict[priceGroupId].compactDescr
        itemNotInShop = section.readBool('notInShop', False)
        _copyPriceForItem(pricesCache, groupsDict[priceGroupId].compactDescr, crewBookItem.compactDescr, itemNotInShop)
    else:
        _xml.raiseWrongXml(xmlCtx, 'priceGroup', 'no price for item %s' % crewBookItem.id)
    return


def _readBookTypeItem(pricesCache, cache, xmlCtx, section, storage):
    type = _xml.readStringOrEmpty(xmlCtx, section, 'type')
    if type not in crew_books_constants.CREW_BOOK_RARITY.ALL_TYPES:
        _xml.raiseWrongXml(xmlCtx, 'type', "unknown crew book rarity type '%s'" % type)
    exp = _xml.readInt(xmlCtx, section, 'exp', 0)
    storage[type] = exp


def _readCrewBooksCacheFromXMLSection(pricesCache, cache, xmlCtx, section, sectionName, storage):
    for i, (gname, gsection) in enumerate(section.items()):
        if gname != sectionName:
            continue
        reader = __xmlReaders[sectionName]
        reader(pricesCache, cache, xmlCtx, gsection, storage)


def readCrewBooksCacheFromXML(pricesCache, cache, folder):
    pgFile = os.path.join(folder, crew_books_constants.CREW_BOOKS_PRICE_GROUPS_XML_FILE)
    _readPriceGroups(pricesCache, cache, (None, crew_books_constants.CREW_BOOKS_PRICE_GROUPS_XML_FILE), ResMgr.openSection(pgFile), 'priceGroup')
    ResMgr.purge(pgFile)
    pgFile = os.path.join(folder, crew_books_constants.CREW_BOOKS_XML_FILE)
    _readCrewBooksCacheFromXMLSection(pricesCache, cache, (None, crew_books_constants.CREW_BOOKS_XML_FILE), ResMgr.openSection(pgFile), 'crewBook', cache.books)
    ResMgr.purge(pgFile)
    pgFile = os.path.join(folder, crew_books_constants.CREW_BOOK_TYPES_XML_FILE)
    _readCrewBooksCacheFromXMLSection(pricesCache, cache, (None, crew_books_constants.CREW_BOOK_TYPES_XML_FILE), ResMgr.openSection(pgFile), 'crewBookType', cache.rarityGroups)
    ResMgr.purge(pgFile)
    return


__xmlReaders = {'crewBook': _readBookItem,
 'crewBookType': _readBookTypeItem}

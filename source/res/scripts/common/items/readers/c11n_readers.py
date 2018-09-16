# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/c11n_readers.py
import nations
import os
from items.components import shared_components
from realm_utils import ResMgr
import items.vehicles as iv
import items._xml as ix
import items.components.c11n_components as cc
import items.customizations as c11n
from constants import IS_CLIENT, IS_WEB
from items.components.c11n_constants import SeasonType, ApplyArea, DecalType, ModificationType, RENT_DEFAULT_BATTLES, ItemTags
from typing import Dict, Type, Tuple, Any, TypeVar
_itemType = TypeVar('_itemType', bound=cc.BaseCustomizationItem)

class BaseCustomizationItemXmlReader(object):
    __slots__ = ()

    def __init__(self):
        super(BaseCustomizationItemXmlReader, self).__init__()

    def _readFromXml(self, target, xmlCtx, section):
        if section.has_key('id'):
            target.id = ix.readInt(xmlCtx, section, 'id', 1)
        if section.has_key('tags'):
            target.tags = iv._readTags(xmlCtx, section, 'tags', 'customizationItem')
        if section.has_key('vehicleFilter'):
            target.filter = self.readVehicleFilterFromXml((xmlCtx, 'vehicleFilter'), section['vehicleFilter'])
        target.season = readEnum(xmlCtx, section, 'season', SeasonType, target.season)
        target.historical = section.readBool('historical', target.historical)
        if section.has_key('priceGroup'):
            target.priceGroup = section.readString('priceGroup')
        if section.has_key('requiredToken'):
            target.requiredToken = section.readString('requiredToken')
        if section.has_key('maxNumber'):
            target.maxNumber = ix.readPositiveInt(xmlCtx, section, 'maxNumber')
            if target.maxNumber <= 0:
                ix.raiseWrongXml(xmlCtx, 'maxNumber', 'should not be less then 1')
        if IS_CLIENT or IS_WEB:
            self._readClientOnlyFromXml(target, xmlCtx, section)

    def _readClientOnlyFromXml(self, target, xmlCtx, section):
        target.i18n = shared_components.I18nExposedComponent(section.readString('userString'), section.readString('description'))

    @staticmethod
    def readVehicleFilterFromXml(xmlCtx, section):
        vc = cc.VehicleFilter()
        readNode = BaseCustomizationItemXmlReader.__readFilterNodeFromXml
        for subsection in section.values():
            if subsection.name == 'include':
                vc.include.append(readNode((xmlCtx, 'include'), subsection))
            if subsection.name == 'exclude':
                vc.exclude.append(readNode((xmlCtx, 'exclude'), subsection))
            ix.raiseWrongXml(xmlCtx, subsection.name, 'should be <include> or <exclude>')

        return vc

    @staticmethod
    def __readFilterNodeFromXml(xmlCtx, section):
        fn = cc.VehicleFilter.FilterNode()
        strNations = ix.readStringOrNone(xmlCtx, section, 'nations')
        if strNations:
            r = []
            for nation in strNations.split():
                nationId = nations.INDICES.get(nation)
                if nationId is None:
                    ix.raiseWrongXml(xmlCtx, 'nations', "unknown nation '%s'" % nation)
                r.append(nationId)

            fn.nations = r
        if section.has_key('levels'):
            fn.levels = ix.readTupleOfPositiveInts(xmlCtx, section, 'levels')
        if section.has_key('vehicles'):
            fn.vehicles = iv._readNationVehiclesByNames(xmlCtx, section, 'vehicles', None)
        if section.has_key('tags'):
            fn.tags = iv._readTags(xmlCtx, section, 'tags', 'vehicle')
        return fn


class PaintXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section):
        super(PaintXmlReader, self)._readFromXml(target, xmlCtx, section)
        if section.has_key('color'):
            target.color = iv._readColor(xmlCtx, section, 'color')
        if section.has_key('gloss'):
            target.gloss = ix.readFloat(xmlCtx, section, 'gloss', 0.0)
        if section.has_key('metallic'):
            target.metallic = ix.readFloat(xmlCtx, section, 'metallic', 0.0)
        if section.has_key('usages'):
            xmlSubCtx = (xmlCtx, 'usages')
            for name, sub in ix.getChildren(xmlCtx, section, 'usages'):
                ctype, cost = self._readUsage(xmlSubCtx, sub)
                for i in ApplyArea.RANGE:
                    if ctype & i:
                        target.usageCosts[i] = cost

    def _readClientOnlyFromXml(self, target, xmlCtx, section):
        super(PaintXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')

    @staticmethod
    def _readUsage(xmlCtx, section):
        componentType = readFlagEnum(xmlCtx, section, 'componentType', ApplyArea)
        cost = section.readInt('cost', 1)
        return (componentType, cost)


class DecalXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section):
        super(DecalXmlReader, self)._readFromXml(target, xmlCtx, section)
        if section.has_key('type'):
            target.type = readEnum(xmlCtx, section, 'type', DecalType)

    def _readClientOnlyFromXml(self, target, xmlCtx, section):
        super(DecalXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('mirror'):
            target.isMirrored = ix.readBool(xmlCtx, section, 'mirror')


class ModificationXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section):
        super(ModificationXmlReader, self)._readFromXml(target, xmlCtx, section)

    def _readClientOnlyFromXml(self, target, xmlCtx, section):
        super(ModificationXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('effects'):
            xmlSubCtx = (xmlCtx, 'effects')
            i = 0
            result = {}
            for name, sub in ix.getChildren(xmlCtx, section, 'effects'):
                itemCtx = (xmlSubCtx, '{}[{}]'.format(name, i))
                mtype = readEnum(itemCtx, sub, 'type', ModificationType)
                result[mtype] = ix.readFloat(itemCtx, sub, 'value', 0.0)
                i += 1

            target.effects = result


class CamouflageXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section):
        super(CamouflageXmlReader, self)._readFromXml(target, xmlCtx, section)
        target.compatibleParts = readFlagEnum(xmlCtx, section, 'compatibleParts', ApplyArea, target.compatibleParts)
        target.componentsCovering = readFlagEnum(xmlCtx, section, 'componentsCovering', ApplyArea, target.componentsCovering)
        target.invisibilityFactor = section.readFloat('invisibilityFactor', 1.0)
        if section.has_key('palettes'):
            palettes = []
            spalettes = section['palettes']
            for pname, psection in spalettes.items():
                res = []
                pctx = (xmlCtx, 'palettes')
                for j, (cname, csection) in enumerate(psection.items()):
                    res.append(iv._readColor((pctx, 'palette %s' % (j,)), psection, cname))

                palettes.append(res)
                target.palettes = tuple(palettes)

    def _readClientOnlyFromXml(self, target, xmlCtx, section):
        super(CamouflageXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('tiling'):
            target.tiling = iv._readCamouflageTilings(xmlCtx, section, 'tiling', self.getDefaultNationId(target))
        if section.has_key('scales'):
            target.scales = ix.readTupleOfFloats(xmlCtx, section, 'scales')

    @staticmethod
    def getDefaultNationId(target):
        return target.filter.include[0].nations[0] if target.filter and target.filter.include and target.filter.include[0].nations else nations.NONE_INDEX


class StyleXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()
    __outfitDeserializer = c11n.ComponentXmlDeserializer(c11n._CUSTOMIZATION_CLASSES)

    def _readFromXml(self, target, xmlCtx, section):
        super(StyleXmlReader, self)._readFromXml(target, xmlCtx, section)
        prototype = True
        if section.has_key('outfits'):
            prototype = False
            outfits = {}
            for i, (_, oSection) in enumerate(section['outfits'].items()):
                oCtx = ((xmlCtx, 'outfits'), 'outfit {}'.format(i))
                season = readEnum(oCtx, oSection, 'season', SeasonType)
                outfit = self.__outfitDeserializer.decode(c11n.CustomizationOutfit.customType, oCtx, oSection)
                for s in SeasonType.SEASONS:
                    if s & season:
                        outfits[s] = outfit

                outfit.styleId = target.id

            target.outfits = outfits
        if section.has_key('isRent'):
            target.isRent = section.readBool('isRent')
        if target.isRent:
            target.rentCount = section.readInt('rentCount', RENT_DEFAULT_BATTLES)
            target.tags = target.tags.union(frozenset((ItemTags.VEHICLE_BOUND,)))
        totalSeason = sum(target.outfits)
        if totalSeason != target.season and not prototype:
            ix.raiseWrongXml(xmlCtx, 'outfits', 'style season must correspond to declared outfits')

    def _readClientOnlyFromXml(self, target, xmlCtx, section):
        super(StyleXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('modelsSet'):
            target.modelsSet = section.readString('modelsSet')


def readCustomizationCacheFromXml(cache, folder):

    def __readItemFolder(itemCls, folder, itemName, storage):
        itemsFileName = os.path.join(folder, itemName + 's', 'list.xml')
        dataSection = ResMgr.openSection(itemsFileName)
        try:
            _readItems(cache, itemCls, (None, itemName + 's/list.xml'), dataSection, itemName, storage)
        finally:
            ResMgr.purge(itemsFileName)

        return

    pgFile = os.path.join(folder, 'priceGroups', 'list.xml')
    _readPriceGroups(cache, (None, 'priceGroups/list.xml'), ResMgr.openSection(pgFile), 'priceGroup')
    ResMgr.purge(pgFile)
    pgFile = os.path.join(folder, 'default_colors.xml')
    _readDefaultColors(cache, (None, 'default_colors.xml'), ResMgr.openSection(pgFile), 'default_color')
    ResMgr.purge(pgFile)
    __readItemFolder(cc.PaintItem, folder, 'paint', cache.paints)
    __readItemFolder(cc.CamouflageItem, folder, 'camouflage', cache.camouflages)
    __readItemFolder(cc.ModificationItem, folder, 'modification', cache.modifications)
    __readItemFolder(cc.DecalItem, folder, 'decal', cache.decals)
    __readItemFolder(cc.StyleItem, folder, 'style', cache.styles)
    return None


def _readItems(cache, itemCls, xmlCtx, section, itemSectionName, storage):
    reader = __xmlReaders[itemCls]
    groupsDict = cache.priceGroups
    itemToGroup = cache.itemToPriceGroup
    for i, (gname, gsection) in enumerate(section.items()):
        if gname != 'itemGroup' and 'xmlns:' not in gname:
            ix.raiseWrongSection(xmlCtx, gname)
        if gname != 'itemGroup':
            continue
        group = cc.ItemGroup(itemCls)
        gCtx = (xmlCtx, 'itemGroup {0}'.format(i))
        itemPrototype = itemCls()
        reader._readFromXml(itemPrototype, gCtx, gsection)
        group.itemPrototype = itemPrototype
        j = 0
        for iname, isection in gsection.items():
            if iname != itemSectionName:
                continue
            iCtx = (gCtx, '{0} {1}'.format(iname, j))
            j += 1
            item = itemCls(group)
            reader._readFromXml(item, iCtx, isection)
            if item.compactDescr in itemToGroup:
                ix.raiseWrongXml(iCtx, 'id', 'duplicate item. id: %s found in group %s' % (item.id, itemToGroup[item.compactDescr]))
            storage[item.id] = item
            if isection.has_key('price'):
                iv._readPriceForItem(iCtx, isection, item.compactDescr)
            if item.priceGroup:
                if item.priceGroup not in cache.priceGroupNames:
                    ix.raiseWrongXml(iCtx, 'priceGroup', 'unknown price group %s for item %s' % (item.priceGroup, item.id))
                priceGroupId = cache.priceGroupNames[item.priceGroup]
                item.priceGroupTags = groupsDict[priceGroupId].tags
                itemToGroup[item.compactDescr] = groupsDict[priceGroupId].compactDescr
                itemNotInShop = isection.readBool('notInShop', False)
                iv._copyPriceForItem(groupsDict[priceGroupId].compactDescr, item.compactDescr, itemNotInShop)
            ix.raiseWrongXml(iCtx, 'priceGroup', 'no price for item %s' % item.id)


def _readPriceGroups(cache, xmlCtx, section, sectionName):
    for tag, iSection in section.items():
        if tag != sectionName:
            continue
        priceGroup = cc.PriceGroup()
        priceGroup.id = ix.readInt(xmlCtx, iSection, 'id', 1)
        iCtx = (xmlCtx, 'id %s' % priceGroup.id)
        if priceGroup.id in cache.priceGroups:
            ix.raiseWrongXml(iCtx, 'id', 'duplicate price group id')
        priceGroup.name = intern(ix.readString(iCtx, iSection, 'name'))
        if priceGroup.name in cache.priceGroupNames:
            ix.raiseWrongXml(iCtx, 'id', 'duplicate price group name "%s"' % priceGroup.name)
        priceGroup.notInShop = iSection.readBool('notInShop', False)
        iv._readPriceForItem(iCtx, iSection, priceGroup.compactDescr)
        if iSection.has_key('tags'):
            tags = iSection.readString('tags').split()
            priceGroup.tags = frozenset(map(intern, tags))
            for tag in priceGroup.tags:
                cache.priceGroupTags.setdefault(tag, []).append(priceGroup)

        cache.priceGroupNames[priceGroup.name] = priceGroup.id
        cache.priceGroups[priceGroup.id] = priceGroup


def _readDefaultColors(cache, xmlCtx, section, sectionName):
    for tag, iSection in section.items():
        if tag != sectionName:
            continue
        nation = ix.readString(xmlCtx, iSection, 'nation')
        color = iv._readColor(xmlCtx, iSection, 'color')
        cache.defaultColors[nations.INDICES[nation]] = color


def readFlagEnum(xmlCtx, section, subsectionName, enumClass, defaultValue=None):
    result = 0
    if not section.has_key(subsectionName) and defaultValue is not None:
        return defaultValue
    else:
        for value in ix.readNonEmptyString(xmlCtx, section, subsectionName).split():
            valueInt = getattr(enumClass, value, None)
            if valueInt is None:
                ix.raiseWrongSection(xmlCtx, subsectionName)
            result |= valueInt

        return result


def readEnum(xmlCtx, section, subsectionName, enumClass, defaultValue=None):
    if not section.has_key(subsectionName) and defaultValue is not None:
        return defaultValue
    else:
        value = ix.readNonEmptyString(xmlCtx, section, subsectionName).upper()
        valueInt = getattr(enumClass, value, None)
        if valueInt is None:
            ix.raiseWrongXml(xmlCtx, subsectionName, 'Invalid enum value %s in class %s' % (value, enumClass))
        return valueInt


__xmlReaders = {cc.PaintItem: PaintXmlReader(),
 cc.DecalItem: DecalXmlReader(),
 cc.CamouflageItem: CamouflageXmlReader(),
 cc.ModificationItem: ModificationXmlReader(),
 cc.StyleItem: StyleXmlReader()}

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/c11n_readers.py
import nations
import os
from items.components import shared_components
from items.components.c11n_constants import CustomizationType, ProjectionDecalFormTags
from realm_utils import ResMgr
import items.vehicles as iv
import items._xml as ix
import items.components.c11n_components as cc
import items.customizations as c11n
from constants import IS_CLIENT, IS_EDITOR, IS_WEB
from items.components.c11n_constants import SeasonType, ApplyArea, DecalType, ModificationType, RENT_DEFAULT_BATTLES, ItemTags
from typing import Dict, Type, Tuple, Any, TypeVar
from contextlib import contextmanager
if IS_EDITOR:
    from reflection_framework import EditorSharedPropertiesInfo, EditorSharedPropertiesConnector
    from meta_objects.items.components.c11n_components_meta import I18nExposedComponentMeta

    @contextmanager
    def storeChangedProperties(obj, props):

        def storeCallback(changedObject, propertyName, flags):
            props.add(propertyName)

        obj.onChanged += storeCallback
        yield
        obj.onChanged -= storeCallback
        return


else:

    @contextmanager
    def storeChangedProperties(obj, props):
        yield
        return


_itemType = TypeVar('_itemType', bound=cc.BaseCustomizationItem)

class BaseCustomizationItemXmlReader(object):
    __slots__ = ()

    def __init__(self):
        super(BaseCustomizationItemXmlReader, self).__init__()

    def _readFromXml(self, target, xmlCtx, section, cache=None):
        if section.has_key('id'):
            target.id = ix.readInt(xmlCtx, section, 'id', 1)
        if section.has_key('tags'):
            target.tags = iv._readTags(xmlCtx, section, 'tags', 'customizationItem')
            if target.itemType == CustomizationType.PROJECTION_DECAL:
                formTags = [ tag for tag in target.tags if tag in ProjectionDecalFormTags.ALL ]
                if len(formTags) > 1:
                    ix.raiseWrongXml(xmlCtx, 'tags', 'wrong formfactor for prjection decal ID%i' % target.id)
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
        if IS_EDITOR:
            refs = section.references
            if len(refs) == 1:
                target.editorData.reference = refs[0]
        if IS_CLIENT or IS_EDITOR or IS_WEB:
            self._readClientOnlyFromXml(target, xmlCtx, section, cache)

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        if IS_EDITOR:
            target.i18n = I18nExposedComponentMeta(section.readString('name'), section.readString('userString'), section.readString('description'), section.readString('longDescriptionSpecial'))
        else:
            target.i18n = shared_components.I18nExposedComponent(section.readString('userString'), section.readString('description'), section.readString('longDescriptionSpecial'))

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

    def _readFromXml(self, target, xmlCtx, section, cache=None):
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

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
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

    def _readFromXml(self, target, xmlCtx, section, cache=None):
        super(DecalXmlReader, self)._readFromXml(target, xmlCtx, section)
        if section.has_key('type'):
            target.type = readEnum(xmlCtx, section, 'type', DecalType)

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(DecalXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('mirror'):
            target.canBeMirrored = ix.readBool(xmlCtx, section, 'mirror')


class ProjectionDecalXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section, cache=None):
        super(ProjectionDecalXmlReader, self)._readFromXml(target, xmlCtx, section)
        if section.has_key('mirror'):
            target.canBeMirrored = ix.readBool(xmlCtx, section, 'mirror')

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(ProjectionDecalXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')


class PersonalNumberXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section, cache):
        if section.has_key('digitsCount'):
            target.digitsCount = section.readInt('digitsCount')
        super(PersonalNumberXmlReader, self)._readFromXml(target, xmlCtx, section, cache)

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache):
        super(PersonalNumberXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section, cache)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('preview_texture'):
            target.previewTexture = section.readString('preview_texture')
        if section.has_key('fontId'):
            target.fontInfo = cache.fonts[section.readInt('fontId')]


class SequenceXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section, cache=None):
        super(SequenceXmlReader, self)._readFromXml(target, xmlCtx, section)
        target.sequenceName = ix.readStringOrNone(xmlCtx, section, 'sequenceName')

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(SequenceXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        target.sequenceName = ix.readStringOrNone(xmlCtx, section, 'sequenceName')


class AttachmentXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section, cache=None):
        super(AttachmentXmlReader, self)._readFromXml(target, xmlCtx, section)
        target.modelName = ix.readStringOrNone(xmlCtx, section, 'modelName')

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(AttachmentXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        target.modelName = ix.readStringOrNone(xmlCtx, section, 'modelName')
        target.sequenceId = ix.readIntOrNone(xmlCtx, section, 'sequenceId')
        target.attachmentLogic = ix.readStringOrNone(xmlCtx, section, 'attachmentLogic')
        target.initialVisibility = ix.readBool(xmlCtx, section, 'initialVisibility', True)


class ModificationXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section, cache=None):
        super(ModificationXmlReader, self)._readFromXml(target, xmlCtx, section)

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
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

    def _readFromXml(self, target, xmlCtx, section, cache=None):
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

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(CamouflageXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('tiling'):
            if IS_EDITOR:
                target.tiling, target.editorData.tilingName = iv._readCamouflageTilings(xmlCtx, section, 'tiling', self.getDefaultNationId(target))
            else:
                target.tiling = iv._readCamouflageTilings(xmlCtx, section, 'tiling', self.getDefaultNationId(target))
        if section.has_key('tilingSettings'):
            target.tilingSettings = iv._readCamouflageTilingSettings(xmlCtx, section)
        if section.has_key('scales'):
            target.scales = ix.readTupleOfFloats(xmlCtx, section, 'scales')
        if section.has_key('rotation'):
            rotation = section['rotation']
            target.rotation = {'hull': rotation.readFloat('HULL', 0.0),
             'turret': rotation.readFloat('TURRET', 0.0),
             'gun': rotation.readFloat('GUN', 0.0)}

    @staticmethod
    def getDefaultNationId(target):
        return target.filter.include[0].nations[0] if target.filter and target.filter.include and target.filter.include[0].nations else nations.NONE_INDEX


class StyleXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()
    __outfitDeserializer = c11n.ComponentXmlDeserializer(c11n._CUSTOMIZATION_CLASSES)

    def _readFromXml(self, target, xmlCtx, section, cache=None):
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

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(StyleXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('modelsSet'):
            target.modelsSet = section.readString('modelsSet')


class InsigniaXmlReader(BaseCustomizationItemXmlReader):
    __slots__ = ()

    def _readFromXml(self, target, xmlCtx, section, cache=None):
        super(InsigniaXmlReader, self)._readFromXml(target, xmlCtx, section)

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(InsigniaXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('atlas'):
            target.atlas = section.readString('atlas')
        if section.has_key('alphabet'):
            target.alphabet = section.readString('alphabet')
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        target.canBeMirrored = section.readBool('canBeMirrored', False)


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
    pgFile = os.path.join(folder, 'default.xml')
    _readDefault(cache, (None, 'default.xml'), ResMgr.openSection(pgFile), 'default')
    ResMgr.purge(pgFile)
    pgFile = os.path.join(folder, 'fonts', 'list.xml')
    _readFonts(cache, (None, 'fonts/list.xml'), ResMgr.openSection(pgFile), 'font')
    ResMgr.purge(pgFile)
    pgFile = os.path.join(folder, 'personal_numbers', 'prohibitedNumbers.xml')
    _readProhibitedNumbers((None, 'personal_numbers/prohibitedNumbers.xml'), ResMgr.openSection(pgFile))
    ResMgr.purge(pgFile)
    __readItemFolder(cc.PaintItem, folder, 'paint', cache.paints)
    __readItemFolder(cc.CamouflageItem, folder, 'camouflage', cache.camouflages)
    __readItemFolder(cc.ModificationItem, folder, 'modification', cache.modifications)
    __readItemFolder(cc.DecalItem, folder, 'decal', cache.decals)
    __readItemFolder(cc.ProjectionDecalItem, folder, 'projection_decal', cache.projection_decals)
    __readItemFolder(cc.StyleItem, folder, 'style', cache.styles)
    __readItemFolder(cc.InsigniaItem, folder, 'insignia', cache.insignias)
    __readItemFolder(cc.PersonalNumberItem, folder, 'personal_number', cache.personal_numbers)
    __readItemFolder(cc.SequenceItem, folder, 'sequence', cache.sequences)
    __readItemFolder(cc.AttachmentItem, folder, 'attachment', cache.attachments)
    return None


def _readProhibitedNumbers(xmlCtx, section):
    prohibitedNumbers = ix.readTupleOfStrings(xmlCtx, section, 'ProhibitedNumbers')
    for prohibitedNumber in prohibitedNumbers:
        if not prohibitedNumber.isdigit():
            ix.raiseWrongXml(xmlCtx, 'ProhibitedNumbers', '%s is not a number' % prohibitedNumber)

    cc.PersonalNumberItem.setProhibitedNumbers(prohibitedNumbers)


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
        sharedProps = set()
        with storeChangedProperties(itemPrototype, sharedProps):
            reader._readFromXml(itemPrototype, gCtx, gsection, cache)
        group.itemPrototype = itemPrototype
        groupItems = []
        j = 0
        for iname, isection in gsection.items():
            if iname != itemSectionName:
                continue
            iCtx = (gCtx, '{0} {1}'.format(iname, j))
            j += 1
            item = itemCls(group)
            overrideProps = set()
            with storeChangedProperties(item, overrideProps):
                reader._readFromXml(item, iCtx, isection, cache)
            if IS_EDITOR:
                item.editorData.sharedPropertiesInfo = EditorSharedPropertiesInfo()
                item.editorData.sharedPropertiesInfo.markAsOverride(*overrideProps)
            groupItems.append(item)
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

        if IS_EDITOR:
            if len(groupItems) > 1 and len(sharedProps) > 0:
                for item in groupItems:
                    for p in sharedProps:
                        if not item.editorData.sharedPropertiesInfo.isOverriden(p):
                            item.editorData.sharedPropertiesInfo.markAsShared(p)

                EditorSharedPropertiesConnector(groupItems).connect()


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


def _readFonts(cache, xmlCtx, section, sectionName):
    for tag, iSection in section.items():
        if tag != sectionName:
            continue
        font = cc.Font()
        font.id = ix.readInt(xmlCtx, iSection, 'id', 1)
        iCtx = (xmlCtx, 'id %s' % font.id)
        if font.id in cache.fonts:
            ix.raiseWrongXml(iCtx, 'id', 'duplicate price group id')
        font.texture = ix.readString(xmlCtx, iSection, 'texture')
        font.alphabet = ix.readString(xmlCtx, iSection, 'alphabet')
        if iSection.has_key('mask'):
            font.mask = ix.readString(xmlCtx, iSection, 'mask')
        if IS_EDITOR:
            refs = iSection.references
            if len(refs) == 1:
                font.editorData.reference = refs[0]
        cache.fonts[font.id] = font


def _readDefault(cache, xmlCtx, section, sectionName):
    for tag, iSection in section.items():
        if tag != sectionName:
            continue
        nation = ix.readString(xmlCtx, iSection, 'nation')
        colors = []
        scolors = iSection['colors']
        for idx, (ctag, csection) in enumerate(scolors.items()):
            colors.append(iv._readColor((xmlCtx, 'color {}'.format(idx)), scolors, ctag))

        cache.defaultColors[nations.INDICES[nation]] = tuple(colors)
        itemId = ix.readInt(xmlCtx, iSection, 'insignia_id')
        cache.defaultInsignias[nations.INDICES[nation]] = itemId


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
 cc.ProjectionDecalItem: ProjectionDecalXmlReader(),
 cc.CamouflageItem: CamouflageXmlReader(),
 cc.ModificationItem: ModificationXmlReader(),
 cc.StyleItem: StyleXmlReader(),
 cc.InsigniaItem: InsigniaXmlReader(),
 cc.PersonalNumberItem: PersonalNumberXmlReader(),
 cc.SequenceItem: SequenceXmlReader(),
 cc.AttachmentItem: AttachmentXmlReader()}

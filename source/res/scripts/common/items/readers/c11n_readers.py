# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/c11n_readers.py
import os
import Math
from string import lower, upper
import re
import items._xml as ix
import items.components.c11n_components as cc
import items.customizations as c11n
import items.vehicles as iv
import nations
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS, parseArenaBonusType
from constants import IS_CLIENT, IS_EDITOR, IS_WEB, DEFAULT_QUEST_FINISH_TIME
from items.components import shared_components
from items.components.c11n_constants import CustomizationType, CustomizationTypeNames, ProjectionDecalFormTags, CustomizationNamesToTypes, CustomizationDisplayType, EMPTY_ITEM_ID, SeasonType, ApplyArea, DecalType, ModificationType, RENT_DEFAULT_BATTLES, ItemTags, ProjectionDecalType, DEFAULT_GLOSS, DEFAULT_METALLIC
from realm_utils import ResMgr
from typing import Dict, Type, Tuple, Any, TypeVar
from contextlib import contextmanager
from customization_quests_common import serelizeToken, PREFIX
from bonus_readers import readUTC
from soft_exception import SoftException
if IS_EDITOR:
    from reflection_framework.unintrusive_weakref import ref as UnintrusiveWeakRef
    from meta_objects.items.components.c11n_components_meta import I18nExposedComponentMeta
    from items.components.c11n_components import CUSTOMIZATION_CLASSES

    @contextmanager
    def storeChangedProperties(obj, props):

        def storeCallback(event):
            props.add(event.propertyName)

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
        target.season = readFlagEnum(xmlCtx, section, 'season', SeasonType, target.season)
        target.customizationDisplayType = section.readInt('historical', target.customizationDisplayType)
        if section.has_key('priceGroup'):
            target.priceGroup = section.readString('priceGroup')
        if section.has_key('requiredToken'):
            target.requiredToken = section.readString('requiredToken')
            target.requiredTokenCount = 1
        if section.has_key('maxNumber'):
            target.maxNumber = ix.readPositiveInt(xmlCtx, section, 'maxNumber')
            if target.maxNumber <= 0:
                ix.raiseWrongXml(xmlCtx, 'maxNumber', 'should not be less then 1')
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
                    ix.raiseWrongXml(xmlCtx, 'nations', 'unknown nation "%s"' % nation)
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
        if 'mirror' in section.keys():
            target.canBeMirroredHorizontally = ix.readBool(xmlCtx, section, 'mirror')
        if 'onlyVerticalMirror' in target.tags:
            if target.canBeMirroredHorizontally:
                ix.raiseWrongXml(xmlCtx, 'tags', 'mirror must be false when onlyVerticalMirror set')
            if 'disableVerticalMirror' in target.tags:
                ix.raiseWrongXml(xmlCtx, 'tags', 'disableVerticalMirror and onlyVerticalMirror cannot be set at the same time')

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(ProjectionDecalXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('glossTexture'):
            target.glossTexture = section.readString('glossTexture')
        if section.has_key('scaleFactorId'):
            target.scaleFactorId = section.readInt('scaleFactorId')


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
        if IS_EDITOR:
            target.name = ix.readStringOrNone(xmlCtx, section, 'name')


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
        if IS_EDITOR:
            target.name = ix.readStringOrNone(xmlCtx, section, 'name')


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
        target.glossMetallicSettings = {'glossMetallicMap': section.readString('glossMetallicMap', ''),
         'gloss': section.readVector4('gloss', Math.Vector4(DEFAULT_GLOSS)),
         'metallic': section.readVector4('metallic', Math.Vector4(DEFAULT_METALLIC))}
        if IS_EDITOR:
            target.editorData.glossMetallicSettingsType = 0
            if target.glossMetallicSettings['glossMetallicMap'] != '':
                target.editorData.glossMetallicSettingsType = 1
            editorOnlySection = c11n.getEditorOnlySection(section)
            if editorOnlySection is not None:
                target.editorData.paletteIndex = editorOnlySection.readInt('paletteIndex', 0)
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

        return

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

    def __readOutfitSection(self, targetId, section, xmlCtx):
        outfits = {}
        for i, (_, oSection) in enumerate(section['outfits'].items()):
            oCtx = ((xmlCtx, 'outfits'), 'outfit {}'.format(i))
            season = readFlagEnum(oCtx, oSection, 'season', SeasonType)
            outfit = self.__outfitDeserializer.decode(c11n.CustomizationOutfit.customType, oCtx, oSection)
            for s in SeasonType.SEASONS:
                if s & season:
                    outfits[s] = outfit

            if IS_EDITOR:
                for projectionDecal in outfit.projection_decals:
                    if projectionDecal.tags is not None and len(projectionDecal.tags) > 0:
                        projectionDecal.editorData.decalType = ProjectionDecalType.TAGS

            outfit.styleId = targetId

        return outfits

    def _readFromXml(self, target, xmlCtx, section, cache=None):
        super(StyleXmlReader, self)._readFromXml(target, xmlCtx, section)
        prototype = True
        if section.has_key('modelsSet'):
            target.modelsSet = section.readString('modelsSet')
            if IS_EDITOR:
                target.editorData.modelsSet = target.modelsSet
        if section.has_key('itemFilters'):
            target.isEditable = True
            itemsFilters = {}
            for sectionName, oSection in section['itemFilters'].items():
                c11nType = CustomizationNamesToTypes[upper(sectionName)]
                itemsFilters[c11nType] = self._readItemsFilterFromXml(c11nType, xmlCtx, oSection)

            target.itemsFilters = itemsFilters
        if section.has_key('alternateItems'):
            target.isEditable = True
            alternateItems = {}
            for sectionName, oSection in section['alternateItems'].items():
                c11nType = CustomizationNamesToTypes[upper(sectionName)]
                if oSection.has_key('id'):
                    alternateItems[c11nType] = ix.readTupleOfPositiveInts(xmlCtx, oSection, 'id')

            target.alternateItems = alternateItems
        if section.has_key('dependencies'):
            target.isEditable = True
            dependencies = {}
            dependenciesAncestors = {}
            for _, camouflageSection in section['dependencies'].items():
                camouflageDependencies = {}
                for sectionName in camouflageSection.keys():
                    if sectionName == 'id':
                        camouflageIDs = ix.readTupleOfPositiveInts(xmlCtx, camouflageSection, 'id')
                    c11nType = CustomizationNamesToTypes[upper(sectionName)]
                    camouflageDependencies[c11nType] = ix.readTupleOfPositiveInts(xmlCtx, camouflageSection, sectionName)

                for camouflageID in camouflageIDs:
                    dependencies[camouflageID] = camouflageDependencies
                    for itemType, itemIDs in camouflageDependencies.iteritems():
                        itemTypeAncestors = dependenciesAncestors.setdefault(itemType, {})
                        for customizationItemID in itemIDs:
                            itemTypeAncestors.setdefault(customizationItemID, []).append(camouflageID)

            target.dependencies = dependencies
            target.dependenciesAncestors = dependenciesAncestors
        if section.has_key('outfits'):
            prototype = False
            outfits = self.__readOutfitSection(target.id, section, xmlCtx)
            target.outfits = outfits
        if section.has_key('isRent'):
            target.isRent = section.readBool('isRent')
        if target.isRent:
            target.rentCount = section.readInt('rentCount', RENT_DEFAULT_BATTLES)
            target.tags = target.tags.union(frozenset((ItemTags.VEHICLE_BOUND,)))
        totalSeason = sum(target.outfits)
        if totalSeason != target.season and not prototype:
            ix.raiseWrongXml(xmlCtx, 'outfits', 'style season must correspond to declared outfits')

    @staticmethod
    def _readItemsFilterFromXml(itemType, xmlCtx, section):
        f = cc.ItemsFilter()
        readNode = StyleXmlReader.__readItemFilterNodeFromXml
        for subsection in section.values():
            if subsection.name == 'include':
                f.include.append(readNode(itemType, (xmlCtx, 'include'), subsection))
            if subsection.name == 'exclude':
                f.exclude.append(readNode(itemType, (xmlCtx, 'exclude'), subsection))

        return f

    @staticmethod
    def __readItemFilterNodeFromXml(itemType, xmlCtx, section):
        fn = cc.ItemsFilter.FilterNode()
        if section.has_key('id'):
            fn.ids = ix.readTupleOfPositiveInts(xmlCtx, section, 'id')
        if section.has_key('itemGroupName'):
            fn.itemGroupNames = ix.readTupleOfStrings(xmlCtx, section, 'itemGroupName', separator=';')
        if section.has_key('tags'):
            fn.tags = iv._readTags(xmlCtx, section, 'tags', 'customizationItem')
        if section.has_key('type'):
            if itemType is not CustomizationType.DECAL:
                ix.raiseWrongXml(xmlCtx, 'type', 'type can be used only with decals')
            types = set((getattr(DecalType, typeName) for typeName in ix.readTupleOfStrings(xmlCtx, section, 'type')))
            if not types.issubset(DecalType.ALL):
                ix.raiseWrongXml(xmlCtx, 'type', 'unsupported type is used')
            fn.types = types
        if section.has_key('historical'):
            fn.customizationDisplayType = ix.readInt(xmlCtx, section, 'historical', CustomizationDisplayType.NON_HISTORICAL)
        return fn

    def _readClientOnlyFromXml(self, target, xmlCtx, section, cache=None):
        super(StyleXmlReader, self)._readClientOnlyFromXml(target, xmlCtx, section)
        if section.has_key('texture'):
            target.texture = section.readString('texture')
        if section.has_key('styleProgressions'):
            styleProgressions = {}
            for i, (spSectionName, spSection) in enumerate(section['styleProgressions'].items()):
                stageId = i + 1
                styleProgressions[stageId] = {}
                if spSection.has_key('materials'):
                    styleProgressions[stageId]['materials'] = spSection['materials'].asString.split()
                if spSection.has_key('outfits'):
                    outfits = self.__readOutfitSection(target.id, spSection, xmlCtx)
                    styleProgressions[stageId]['additionalOutfit'] = outfits

            target.styleProgressions = styleProgressions


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
        progressionFileName = os.path.join(folder, itemName + 's', 'progression.xml')
        dataSection = ResMgr.openSection(progressionFileName)
        progression = {}
        if dataSection:
            try:
                _readProgression(cache, (None, itemName + 's/progression.xml'), dataSection, progression)
            finally:
                ResMgr.purge(progressionFileName)

        itemsFileName = os.path.join(folder, itemName + 's', 'list.xml')
        dataSection = ResMgr.openSection(itemsFileName)
        try:
            _readItems(cache, itemCls, (None, itemName + 's/list.xml'), dataSection, itemName, storage, progression)
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
    pgFile = os.path.join(folder, 'progression', 'list.xml')
    for style, questProgression in readQuestProgression(cache, (None, 'progression/list.xml'), ResMgr.openSection(pgFile), 'styleProgress'):
        style.questsProgression = questProgression

    ResMgr.purge(pgFile)
    _validateStyles(cache)
    return None


def _validateStyles(cache):

    def customizationItemInOutfits(style, itemID, itemType):
        for season in SeasonType.RANGE:
            outfit = style.outfits.get(season)
            if outfit:
                customizationItems = getattr(outfit, '{}s'.format(lower(CustomizationTypeNames[itemType])))
                for customizationItem in customizationItems:
                    if itemID == customizationItem.id:
                        return True

        return False

    styleOnlyItemsFromStyles = set()
    for style in cache.styles.itervalues():
        if style.isEditable:
            alternateItemsIDs = {}
            if style.alternateItems:
                for itemType, ids in style.alternateItems.iteritems():
                    alternateItemsIDs[itemType] = ids
                    items = map(cache.itemTypes[itemType].get, ids)
                    styleOnlyItemsFromStyles.update(items)

            if style.dependencies:
                for camouflageID, camouflageDependencies in style.dependencies.iteritems():
                    if camouflageID not in alternateItemsIDs.get(CustomizationType.CAMOUFLAGE, {}) and not customizationItemInOutfits(style, camouflageID, CustomizationType.CAMOUFLAGE):
                        raise SoftException('Items {} itemType {} from dependencies must be included in alternateItems or outfits'.format(camouflageID, 2))
                    for itemType, ids in camouflageDependencies.iteritems():
                        inStyle = False
                        idsDiff = set(ids).difference(set(alternateItemsIDs.get(itemType, {})))
                        for itemID in idsDiff:
                            if not customizationItemInOutfits(style, itemID, itemType):
                                break
                        else:
                            inStyle = True

                        if not inStyle:
                            raise SoftException('Items {} itemType {} from dependencies must be included in alternateItems or outfits'.format(ids, itemType))

    if any((item is None or not item.isStyleOnly for item in styleOnlyItemsFromStyles)):
        raise SoftException('Items shall contain styleOnly tag in tags to be used in alternateItems')


def _readProhibitedNumbers(xmlCtx, section):
    prohibitedNumbers = ix.readTupleOfStrings(xmlCtx, section, 'ProhibitedNumbers')
    for prohibitedNumber in prohibitedNumbers:
        if not prohibitedNumber.isdigit():
            ix.raiseWrongXml(xmlCtx, 'ProhibitedNumbers', '%s is not a number' % prohibitedNumber)

    cc.PersonalNumberItem.setProhibitedNumbers(prohibitedNumbers)


def __readProgressLevel(xmlCtx, section):
    level = {}
    for sectionName, subSections in section.items():
        if sectionName == 'price':
            level.update({'price': ix.readPrice(xmlCtx, section, 'price'),
             'notInShop': section.readBool('notInShop', False)})
        if sectionName == 'condition':
            conditions = level.setdefault('conditions', list())
            condition = {}
            for subSection in subSections.values():
                sectionName = subSection.name
                if sectionName == 'description':
                    condition.update({'description': ix.readNonEmptyString(xmlCtx, subSection, '')})
                condition.update(__readCondition((xmlCtx, subSection.name), subSection, [sectionName]))

            if not condition:
                ix.raiseWrongXml(xmlCtx, 'progression', "Customization don't have conditions")
            conditions.append(condition)

    return level


def __readCondition(xmlCtx, section, path):
    subSections = section.values()
    if subSections:
        path.append(subSections[0].name)
        return __readCondition((xmlCtx, subSections[0].name), subSections[0], path)
    else:
        return {'path': tuple(path),
         'value': ix.readNonEmptyString(xmlCtx, section, '')}


def __readProgress(xmlCtx, section):
    progress = cc.ProgressForCustomization()
    itemId = ix.readInt(xmlCtx, section, 'id')
    if section.has_key('autobound'):
        progress.autobound = True
    for sectionName, subSection in section.items():
        if sectionName == 'levels':
            for levelSectionName, levelSection in subSection.items():
                level = int(re.findall('\\d+', levelSectionName)[0])
                if levelSection['default'] is not None:
                    progress.defaultLvl = level if level > progress.defaultLvl else progress.defaultLvl
                progress.levels[level] = __readProgressLevel((xmlCtx, levelSectionName), levelSection)

        if sectionName == 'autoGrantCount':
            progress.autoGrantCount = ix.readPositiveInt(xmlCtx, subSection, '')
        if sectionName == 'bonusType':
            bonusTypes = ix.readStringOrEmpty(xmlCtx, subSection, '').split()
            parseArenaBonusType(progress.bonusTypes, bonusTypes, ARENA_BONUS_TYPE_CAPS.CUSTOMIZATION_PROGRESSION)
        if sectionName == 'priceGroup':
            progress.priceGroup = ix.readStringOrEmpty(xmlCtx, subSection, '')

    if len(progress.levels) < 2:
        ix.raiseWrongXml(xmlCtx, 'tags', 'wrong progression. Minimum count progression = 2. Current count progression %i' % len(progress.levels))
    for i in range(1, len(progress.levels) + 1):
        if i not in progress.levels:
            ix.raiseWrongXml(xmlCtx, 'tags', 'wrong progression. Skipped level %i' % i)

    if progress.levels[1].get('notInShop'):
        ix.raiseWrongXml(xmlCtx, 'tags', 'wrong progression. First level should always be available for purchase.')
    return (itemId, progress)


def _readProgression(cache, xmlCtx, section, progression):
    for gname, gsection in section.items():
        if gname != 'progress':
            ix.raiseWrongSection(xmlCtx, gname)
        itemId, progress = __readProgress((xmlCtx, 'progress'), gsection)
        if progress.priceGroup:
            if progress.priceGroup not in cache.priceGroupNames:
                if IS_EDITOR:
                    continue
                ix.raiseWrongXml(xmlCtx, 'priceGroup', 'unknown price group %s for item %s' % (progress.priceGroup, itemId))
            priceGroupId = cache.priceGroupNames[progress.priceGroup]
            pgDescr = cache.priceGroups[priceGroupId].compactDescr
            for num, level in progress.levels.iteritems():
                if 'price' not in level and progress.defaultLvl != num:
                    priceInfo = iv.getPriceForItemDescr(pgDescr)
                    if priceInfo:
                        level.update({'price': priceInfo[0],
                         'notInShop': priceInfo[1]})

        progression[itemId] = progress


def _readItems(cache, itemCls, xmlCtx, section, itemSectionName, storage, progression):
    reader = __xmlReaders[itemCls]
    priceGroupsDict = cache.priceGroups
    itemToPriceGroup = cache.itemToPriceGroup
    if IS_EDITOR:
        itemType = CUSTOMIZATION_CLASSES[itemCls]
        cache.editorData.groups[itemType] = []
        sourceFiles = set()
        if section is None:
            return
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
        if gsection.has_key('name'):
            group.name = gsection.readString('name')
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
                item.editorData.sharedPropertiesInfo.markAsOverride(*overrideProps)
            groupItems.append(item)
            if item.compactDescr in itemToPriceGroup:
                ix.raiseWrongXml(iCtx, 'id', 'duplicate item. id: %s found in group %s' % (item.id, itemToPriceGroup[item.compactDescr]))
            storage[item.id] = item
            item.progression = progression.get(item.id, None)
            if item.progression is not None:
                cache.customizationWithProgression[item.compactDescr] = item
                iv._readPriceForProgressionLvl(item.compactDescr, item.progression.levels)
                for arenaTypeID, items in cache.itemGroupByProgressionBonusType.iteritems():
                    if arenaTypeID in item.progression.bonusTypes:
                        items.append(item)

            if isection.has_key('price'):
                iv._readPriceForItem(iCtx, isection, item.compactDescr)
            if item.priceGroup:
                if item.priceGroup not in cache.priceGroupNames:
                    if IS_EDITOR:
                        continue
                    ix.raiseWrongXml(iCtx, 'priceGroup', 'unknown price group %s for item %s' % (item.priceGroup, item.id))
                priceGroupId = cache.priceGroupNames[item.priceGroup]
                item.priceGroupTags = priceGroupsDict[priceGroupId].tags
                itemToPriceGroup[item.compactDescr] = priceGroupsDict[priceGroupId].compactDescr
                itemNotInShop = isection.readBool('notInShop', False)
                iv._copyPriceForItem(priceGroupsDict[priceGroupId].compactDescr, item.compactDescr, itemNotInShop)
            ix.raiseWrongXml(iCtx, 'priceGroup', 'no price for item %s' % item.id)

        if IS_EDITOR:
            refs = gsection.references
            if len(refs) == 1:
                group.editorData.sourceXml = refs[0]
                sourceFiles.add(refs[0])
            itemPrototype.edIsPrototype = True
            group.editorData.itemRefs = [ UnintrusiveWeakRef(item) for item in groupItems ]
            cache.editorData.groups[itemType].append(group)

    if IS_EDITOR:
        cache.editorData.sourceFiles[itemType] = list(sourceFiles)
    _addEmptyItem(itemCls, storage, itemSectionName)
    return


def _addEmptyItem(itemCls, storage, itemSectionName):
    if IS_EDITOR and itemSectionName != 'style':
        return
    item = itemCls()
    item.id = EMPTY_ITEM_ID
    storage[EMPTY_ITEM_ID] = item


def _readPriceGroups(cache, xmlCtx, section, sectionName):
    if IS_EDITOR and section is None:
        return
    else:
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

        return


def _readFonts(cache, xmlCtx, section, sectionName):
    if IS_EDITOR:
        itemType = CUSTOMIZATION_CLASSES[cc.Font]
        sourceFiles = set()
        if section is None:
            return
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
        cache.fonts[font.id] = font
        if IS_EDITOR:
            refs = iSection.references
            if len(refs) == 1:
                font.editorData.sourceXml = refs[0]
                sourceFiles.add(refs[0])

    if IS_EDITOR:
        cache.editorData.sourceFiles[itemType] = list(sourceFiles)
    return


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
        itemId = ix.readInt(xmlCtx, iSection, 'emblem_id')
        cache.defaultPlayerEmblems[nations.INDICES[nation]] = itemId
        if iSection.has_key('top_vehicle'):
            topVehicle = ix.readString(xmlCtx, iSection, 'top_vehicle')
            cache.topVehiclesByNation[nation] = topVehicle


def readQuestProgression(cache, xmlCtx, section, sectionName):
    cls = cc.QuestProgressForCustomization
    for gname, gsection in section.items():
        if gname != sectionName:
            continue
        styleId = ix.readInt(xmlCtx, gsection, 'id')
        if styleId not in cache.styles:
            ix.raiseWrongXml(xmlCtx, 'id', 'Style id {} not found '.format(styleId))
        style = cache.styles[styleId]
        finishTime = readUTC(gsection, 'finishTime', DEFAULT_QUEST_FINISH_TIME)
        unlockChains = {}
        for tname, psection in gsection['unlockChains'].items():
            groupId = 0
            try:
                groupId = int(tname[len(PREFIX):])
            except:
                ix.raiseWrongXml(xmlCtx, tname, 'Wrong section format use: {}'.format('cust_progress_{groupID}'))

            token = serelizeToken(styleId, groupId)
            if token in unlockChains:
                ix.raiseWrongXml(xmlCtx, tname, 'GroupId dublicate id {}'.format(groupId))
            concurrent = ix.readBool(xmlCtx, psection, 'concurrent', False)
            items = {}
            unlockChains[token] = (items, concurrent)
            for lname, lsection in psection.items():
                if lname != 'item':
                    continue
                count = ix.readInt(xmlCtx, lsection, 'level')
                levelFinishTime = readUTC(lsection, 'finishTime', finishTime)
                unlockItems = {}
                for subSectionName, oSection in lsection.items():
                    if oSection.has_key('id'):
                        c11nType = CustomizationNamesToTypes[upper(subSectionName)]
                        unlockItems[c11nType] = ix.readTupleOfPositiveInts(xmlCtx, oSection, 'id')
                        if not all([ False for id in unlockItems[c11nType] if id not in cache.itemTypes[c11nType] ]):
                            ix.raiseWrongXml(xmlCtx, tname, 'id for {} not in cache'.format(subSectionName))

                if count < 0:
                    ix.raiseWrongXml(xmlCtx, tname, 'level < 0')
                for c11nType, ids in unlockItems.iteritems():
                    for id in ids:
                        item = cache.itemTypes[c11nType][id]
                        if count > 0:
                            item.requiredToken = token
                            item.requiredTokenCount = count
                        item.tags = item.tags.union(frozenset((ItemTags.QUESTS_PROGRESSION,)))
                        cache.itemToQuestProgressionStyle[item.compactDescr] = style

                items.update({count: (unlockItems, levelFinishTime)})

        yield (style, cls(styleId, unlockChains))


def readFlagEnum(xmlCtx, section, subsectionName, enumClass, defaultValue=None):
    result = 0
    if not section.has_key(subsectionName) and defaultValue is not None:
        return defaultValue
    else:
        for value in ix.readNonEmptyString(xmlCtx, section, subsectionName).split():
            valueInt = getattr(enumClass, value.upper(), None)
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

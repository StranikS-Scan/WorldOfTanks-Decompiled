# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/c11n_writers.py
import Math
import math
from items import _xml, parseIntCompactDescr
import os
from realm_utils import ResMgr
from soft_exception import SoftException
import items.vehicles as iv
from items.components.c11n_constants import SeasonType, DecalType
from nations import NAMES, INDICES

def findOrCreate(section, subsectionName):
    if not section.has_key(subsectionName):
        return section.createSection(subsectionName)
    else:
        return section[subsectionName]


def resizeSection(section, newSize, newName):
    if len(section) == newSize:
        return False
    while len(section) > newSize:
        lastSection = section.child(len(section) - 1)
        section.deleteSection(lastSection)

    while len(section) < newSize:
        section.createSection(newName(len(section)))

    return True


def saveCustomizationItems(cache, folder):
    writeItemType(PaintXmlWriter(), cache.paints, folder, 'paint')
    writeItemType(DecalXmlWriter(), cache.decals, folder, 'decal')
    writeItemType(ProjectionDecalXmlWriter(), cache.projection_decals, folder, 'projection_decal')
    writeItemType(CamouflageXmlWriter(), cache.camouflages, folder, 'camouflage')
    writeItemType(ModificationXmlWriter(), cache.modifications, folder, 'modification')
    writeItemType(StyleXmlWriter(), cache.styles, folder, 'style')
    writeItemType(PersonalNumberXmlWriter(), cache.personal_numbers, folder, 'personal_number')
    writeItemType(InsigniaXmlWriter(), cache.insignias, folder, 'insignia')
    writeFontType(FontXmlWriter(), cache.fonts, folder, 'font')


def writeItemType(writer, items, folder, itemName):
    refsections = {}
    gsections = {}
    isections = {}
    changedRefs = set()
    for id, item in items.items():
        if item.editorData.reference is None:
            SoftException('Item {} has no reference, data format has changed?'.format(itemName + str(id)))
        ref = item.editorData.reference
        parseReference(ref, itemName, refsections, gsections, isections)
        gsection = gsections[id]
        isection = isections[id]
        if gsection is None or isection is None:
            SoftException("Can't open section {}".format(ref))
        changed = writer.write(item, gsection, isection)
        if changed:
            changedRefs.add(ref)

    for ref, refsection in refsections.items():
        if ref in changedRefs:
            refsection.save()

    return


def writeFontType(writer, items, folder, itemName):
    refsections = {}
    isections = {}
    changedRefs = set()

    def parseRefSection(ref, isections, refsections):
        if ref not in refsections:
            section = ResMgr.openSection(ref)
            if section is None:
                _xml.raiseWrongXml(None, ref, "can't find datasection")
            refsections[ref] = section
            for name, isection in section.items():
                if isection.has_key('id'):
                    id = isection['id'].asInt
                    isections[id] = isection

        return

    for id, item in items.items():
        ref = item.editorData.reference
        if ref is None:
            SoftException('Item {} has no reference, data format has changed?'.format(itemName + str(id)))
        parseRefSection(ref, isections, refsections)
        isection = isections[id]
        if isection is None:
            SoftException("Can't open section {}".format(ref))
        changed = writer.write(item, isection)
        if changed:
            changedRefs.add(ref)

    for ref, refsection in refsections.items():
        if ref in changedRefs:
            refsection.save()

    return


def parseReference(reference, itemName, refsections, gsections, isections):
    if reference in refsections:
        return
    else:
        section = ResMgr.openSection(reference)
        if section is None:
            _xml.raiseWrongXml(None, reference, "can't find datasection")
        refsections[reference] = section
        for gname, gsection in section.items():
            if gname != 'itemGroup':
                continue
            for iname, isection in gsection.items():
                if iname != itemName or not isection.has_key('id'):
                    continue
                id = isection['id'].asInt
                gsections[id] = gsection
                isections[id] = isection

        return


class VehicleFilterTagsConvertor(object):

    def convertToString(self, valuesList):
        result = ' '.join(valuesList)
        return result


class VehicleFilterLevelConvertor(object):

    def convertToString(self, valuesList):
        result = ' '.join(map(str, valuesList))
        return result


class VehicleFilterNationConvertor(object):

    def convertToString(self, valuesList):
        result = ' '.join(map(lambda item: NAMES[item], valuesList))
        return result


class VehicleFilterVehicleConvertor(object):

    def convertToString(self, valuesList):
        from items.vehicles import g_cache, g_list

        def getTankName(vehCompactDesc):
            itemTypeID, nationId, vehId = parseIntCompactDescr(vehCompactDesc)
            tank = g_cache.vehicle(nationId, vehId)
            return tank.name

        result = ' '.join(map(lambda item: getTankName(item), valuesList))
        return result


def saveVehicleFilter(item, gsection, isection):
    changed = False
    section = selectSection(gsection, isection, 'vehicleFilter')
    vehicleFilterSection = findOrCreate(section, 'vehicleFilter')

    def countFilters(filterSection):
        includeCount = 0
        excludeCount = 0
        for iname, isection in filterSection.items():
            if iname == 'include':
                includeCount += 1
            if iname == 'exclude':
                excludeCount += 1

        return (includeCount, excludeCount)

    includeSectCnt, excludeSectCnt = countFilters(vehicleFilterSection)
    if includeSectCnt != len(item.filter.include) or excludeSectCnt != len(item.filter.exclude):
        changed = True
        while len(vehicleFilterSection) > 0:
            lastSection = section.child(len(vehicleFilterSection) - 1)
            section.deleteSection(lastSection)

        def createSections(parentSection, sectionName, count):
            while count > 0:
                parentSection.createSection(sectionName)
                count -= 1

        createSections(vehicleFilterSection, 'include', len(item.filter.include))
        createSections(vehicleFilterSection, 'exclude', len(item.filter.exclude))

    def saveFilter(filterSection, filterName, filters):
        if len(filters) == 0:
            return False
        changed = False
        index = 0

        def saveFilterValue(subFilterSection, valueSectionName, listOfValues, convertor):
            if len(listOfValues) == 0:
                if subFilterSection.has_key(valueSectionName):
                    subFilterSection.deleteSection(valueSectionName)
                    return True
            else:
                strValue = convertor.convertToString(listOfValues)
                if strValue is None:
                    return False
                return _xml.rewriteString(subFilterSection, valueSectionName, strValue)
            return False

        for iname, isection in filterSection.items():
            if iname == filterName:
                filterValue = filters[index]
                changed |= saveFilterValue(isection, 'nations', filterValue.nations, VehicleFilterNationConvertor())
                changed |= saveFilterValue(isection, 'levels', filterValue.levels, VehicleFilterLevelConvertor())
                changed |= saveFilterValue(isection, 'tags', filterValue.tags, VehicleFilterTagsConvertor())
                changed |= saveFilterValue(isection, 'vehicles', filterValue.vehicles, VehicleFilterVehicleConvertor())
                index += 1

        return changed

    changed |= saveFilter(vehicleFilterSection, 'include', item.filter.include)
    changed |= saveFilter(vehicleFilterSection, 'exclude', item.filter.exclude)
    return changed


class BaseCustomizationItemXmlWriter(object):

    def write(self, item, gsection, isection):
        changed = False
        changed |= rewriteBool(gsection, isection, 'historical', item.historical)
        changed |= rewriteString(gsection, isection, 'priceGroup', item.priceGroup, '')
        changed |= rewriteString(gsection, isection, 'requiredToken', item.requiredToken, '')
        changed |= rewriteString(gsection, isection, 'texture', item.texture, '')
        changed |= rewriteInt(gsection, isection, 'maxNumber', item.maxNumber, 0)
        changed |= rewriteTags(gsection, isection, item.tags)
        changed |= rewriteString(gsection, isection, 'season', encodeEnum(SeasonType, item.season), 'UNDEFINED')
        changed |= rewriteString(gsection, isection, 'userString', item.i18n.userKey)
        changed |= rewriteString(gsection, isection, 'description', item.i18n.descriptionKey)
        changed |= saveVehicleFilter(item, gsection, isection)
        return changed


class PaintXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(PaintXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteFloat(gsection, isection, 'gloss', item.gloss, 0.0)
        changed |= rewriteFloat(gsection, isection, 'metallic', item.metallic, 0.0)
        color = item.color
        c_a, c_r, c_g, c_b = (0, 0, 0, 0)
        if color > 0:
            c_a = color >> 24 & 255
            c_r = color >> 16 & 255
            c_g = color >> 8 & 255
            c_b = color & 255
        color = Math.Vector4(c_b, c_g, c_r, c_a)
        changed |= rewriteVector4(gsection, isection, 'color', color, 0.0)
        return changed


class DecalXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(DecalXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteBool(gsection, isection, 'mirror', item.canBeMirrored)
        changed |= rewriteString(gsection, isection, 'type', encodeEnum(DecalType, item.type))
        return changed


class ProjectionDecalXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(ProjectionDecalXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteBool(gsection, isection, 'mirror', item.canBeMirrored)
        return changed


class CamouflageXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(CamouflageXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteFloat(gsection, isection, 'invisibilityFactor', item.invisibilityFactor, 1.0)
        changed |= rewritePalettes(gsection, isection, item.palettes)
        changed |= rewriteCamouflageRotation(gsection, isection, item)
        changed |= rewriteCamouflageScales(gsection, isection, item)
        changed |= rewriteCamouflageTiling(gsection, isection, item)
        return changed


def rewriteEffects(item, gsection, isection):
    changed = False
    section = selectSection(gsection, isection, 'effects')
    effectsSection = findOrCreate(section, 'effects')
    changed |= resizeSection(effectsSection, 2, lambda id: 'effect')
    index = 0

    def writeEffectValue(effectSection, type, value):
        result = _xml.rewriteString(effectSection, 'type', type)
        result |= _xml.rewriteFloat(effectSection, 'value', value)
        return result

    while index < 2:
        effectSection = effectsSection.child(index)
        typeSection = findOrCreate(effectSection, 'type')
        effectType = typeSection.asString
        if effectType is None or effectType == '':
            if index == 0:
                effectType = 'paint_age'
            if index == 1:
                effectType = 'paint_fading'
        effectValue = 0
        if effectType == 'paint_age':
            effectValue = item.strength
        elif effectType == 'paint_fading':
            effectValue = item.fading
        changed |= writeEffectValue(effectSection, effectType, effectValue)
        index += 1

    return changed


class ModificationXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(ModificationXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteEffects(item, gsection, isection)
        return changed


class StyleXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(StyleXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteBool(gsection, isection, 'isRent', item.isRent, False)
        changed |= rewriteString(gsection, isection, 'modelsSet', item.modelsSet, '')
        changed |= rewriteInt(gsection, isection, 'rentCount', item.rentCount, 0)
        return changed


class PersonalNumberXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(PersonalNumberXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteInt(gsection, isection, 'digitsCount', item.digitsCount)
        changed |= rewriteString(gsection, isection, 'preview_texture', item.previewTexture)
        return changed


class InsigniaXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(InsigniaXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteString(gsection, isection, 'atlas', item.atlas, '')
        changed |= rewriteString(gsection, isection, 'alphabet', item.alphabet, '')
        changed |= rewriteBool(gsection, isection, 'canBeMirrored', item.canBeMirrored, False)
        return changed


def writeFintAlphabet(item):
    xmlPath = item.editorData.alphabet
    section = ResMgr.openSection(xmlPath)
    if section is None:
        return
    else:
        changed = False
        if len(section.items()) != len(item.editorData.alphabetList):
            changed |= resizeSection(section, len(item.editorData.alphabetList), lambda id: 'glyph')
        itemIndex = 0
        for name, isection in section.items():
            glyphItem = item.editorData.alphabetList[itemIndex]
            changed |= _xml.rewriteString(isection, 'name', glyphItem.name)
            vBegin = Math.Vector2(glyphItem.position[0], glyphItem.position[1])
            changed |= _xml.rewriteVector2(isection, 'begin', vBegin)
            vEnd = Math.Vector2(glyphItem.position[2], glyphItem.position[3])
            changed |= _xml.rewriteVector2(isection, 'end', vEnd)
            itemIndex += 1

        if changed:
            section.save()
        return


class FontXmlWriter(object):

    def write(self, item, isection):
        changed = _xml.rewriteString(isection, 'texture', item.texture)
        changed |= _xml.rewriteString(isection, 'alphabet', item.alphabet)
        writeFintAlphabet(item)
        return changed


def selectSection(gsection, isection, subsectionName):
    if isection.has_key(subsectionName) or not gsection.has_key(subsectionName):
        return isection
    else:
        return gsection


def rewriteInt(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteInt(selectSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteBool(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteBool(selectSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteString(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteString(selectSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteFloat(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteFloat(selectSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteVector2(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteVector2(selectSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteVector3(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteVector3(selectSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteVector4(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteVector4(selectSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteTags(gsection, isection, tags):
    section = selectSection(gsection, isection, 'tags')
    rewrite = len(tags) > 0
    if section.has_key('tags'):
        if not rewrite:
            section.deleteSection('tags')
            return True
        oldTags = iv._readTags(None, section, 'tags', 'customizationItem')
        rewrite = oldTags != tags
    if rewrite:
        tagsStr = ' '.join(tags)
        return _xml.rewriteFloat(section, 'tags', tagsStr)
    else:
        return False


def rewritePalettes(gsection, isection, items):
    changed = False
    section = selectSection(gsection, isection, 'palettes')
    if not items or len(items) == 0:
        return section.deleteSection('palettes')
    palettesSection = findOrCreate(section, 'palettes')
    changed |= resizeSection(palettesSection, len(items), lambda id: 'palette')
    for index, palette in enumerate(items):

        def sectName(id):
            return 'c' + str(id)

        paletteSection = palettesSection.child(index)
        changed |= resizeSection(paletteSection, len(palette), sectName)
        for i, iPalette in enumerate(palette):
            r = iPalette & 255
            g = iPalette >> 8 & 255
            b = iPalette >> 16 & 255
            a = iPalette >> 24 & 255
            colorStr = ' '.join([str(r),
             str(g),
             str(b),
             str(a)])
            changed |= _xml.rewriteString(paletteSection, sectName(i), colorStr)

    return changed


def rewriteCamouflageRotation(gsection, isection, camouflageItem):
    changed = False
    hullRotation = camouflageItem.rotation['hull']
    gunRotation = camouflageItem.rotation['gun']
    turretRotation = camouflageItem.rotation['turret']

    def rewritePartRotation(section, partName, value):
        return _xml.rewriteFloat(section, partName, value)

    if hullRotation > 0 or gunRotation > 0 or turretRotation > 0:
        section = selectSection(gsection, isection, 'rotation')
        rotationSection = findOrCreate(section, 'rotation')
        changed |= rewritePartRotation(rotationSection, 'HULL', hullRotation)
        changed |= rewritePartRotation(rotationSection, 'TURRET', turretRotation)
        changed |= rewritePartRotation(rotationSection, 'GUN', gunRotation)
    return changed


def rewriteCamouflageScales(gsection, isection, camouflageItem):
    scalesResult = Math.Vector3(camouflageItem.scales[0], camouflageItem.scales[1], camouflageItem.scales[2])
    return rewriteVector3(gsection, isection, 'scales', scalesResult)


def correctTankNameByCurrentSectionName(section, tankName):
    if section.has_key(tankName):
        return tankName
    index = tankName.find(':')
    if index > 0:
        tmpTankName = tankName[index + 1:len(tankName)]
        if section.has_key(tmpTankName):
            return tmpTankName
    return tankName


def rewriteCamouflageTiling(gsection, isection, camouflageItem):
    changed = False
    tilingSection = selectSection(gsection, isection, 'tiling')
    tilingSection = findOrCreate(tilingSection, 'tiling')
    for key, value in camouflageItem.tiling.items():
        if value is None:
            continue
        tankName = camouflageItem.editorData.tilingName[key]
        correctedTankName = correctTankNameByCurrentSectionName(tilingSection, tankName)
        tilingRes = Math.Vector4(value[0], value[1], value[2], value[3])
        changed |= _xml.rewriteVector4(tilingSection, correctedTankName, tilingRes)

    return changed


def encodeEnum(enumClass, intValue):
    for enum, value in enumClass.__dict__.iteritems():
        if enum.startswith('_'):
            continue
        if intValue == value:
            return enum.lower()

    return None

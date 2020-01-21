# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/c11n_writers.py
import Math
from items import _xml
import os
from realm_utils import ResMgr
from soft_exception import SoftException
import items.vehicles as iv
from items.components.c11n_constants import SeasonType, DecalType

def saveCustomizationItems(cache, folder):
    writeItemType(PaintXmlWriter(), cache.paints, folder, 'paint')
    writeItemType(DecalXmlWriter(), cache.decals, folder, 'decal')
    writeItemType(ProjectionDecalXmlWriter(), cache.projection_decals, folder, 'projection_decal')
    writeItemType(CamouflageXmlWriter(), cache.camouflages, folder, 'camouflage')
    writeItemType(ModificationXmlWriter(), cache.modifications, folder, 'modification')
    writeItemType(StyleXmlWriter(), cache.styles, folder, 'style')
    writeItemType(PersonalNumberXmlWriter(), cache.personal_numbers, folder, 'personal_number')
    writeItemType(InsigniaXmlWriter(), cache.insignias, folder, 'insignia')


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
        return changed


class PaintXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(PaintXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteFloat(gsection, isection, 'gloss', item.gloss, 0.0)
        changed |= rewriteFloat(gsection, isection, 'metallic', item.metallic, 0.0)
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
        return changed


class ModificationXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(ModificationXmlWriter, self).write(item, gsection, isection)
        return changed


class StyleXmlWriter(BaseCustomizationItemXmlWriter):

    def write(self, item, gsection, isection):
        changed = super(StyleXmlWriter, self).write(item, gsection, isection)
        changed |= rewriteBool(gsection, isection, 'isRent', item.isRent, False)
        changed |= rewriteString(gsection, isection, 'modelsSet', item.modelsSet, '')
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


def writeSection(gsection, isection, subsectionName):
    if isection.has_key(subsectionName) or not gsection.has_key(subsectionName):
        return isection
    else:
        return gsection


def rewriteInt(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteInt(writeSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteBool(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteBool(writeSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteString(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteString(writeSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteFloat(gsection, isection, subsectionName, value, defaultValue=None, createNew=True):
    return _xml.rewriteFloat(writeSection(gsection, isection, subsectionName), subsectionName, value, defaultValue, createNew)


def rewriteTags(gsection, isection, tags):
    section = writeSection(gsection, isection, 'tags')
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
    section = writeSection(gsection, isection, 'palettes')
    if not items or len(items) == 0:
        return section.deleteSection('palettes')

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


def encodeEnum(enumClass, intValue):
    for enum, value in enumClass.__dict__.iteritems():
        if enum.startswith('_'):
            continue
        if intValue == value:
            return enum.lower()

    return None

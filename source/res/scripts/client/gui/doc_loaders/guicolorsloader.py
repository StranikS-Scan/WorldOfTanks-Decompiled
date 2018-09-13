# Embedded file name: scripts/client/gui/doc_loaders/GuiColorsLoader.py
import Math
import ResMgr
from debug_utils import *
from items import _xml

class GuiColorsLoader(object):
    XML_PATH = 'gui/gui_colors.xml'
    DEFAULT_ALIAS_COLOR = None
    DEFAULT_RGBA_COLOR = Math.Vector4(255, 255, 255, 255)
    DEFAULT_COLOR_OFFSET = Math.Vector4(0, 0, 0, 0)
    DEFAULT_TRANSFORM_COLOR_MULT = Math.Vector4(1, 1, 1, 1)
    DEFAULT_TRANSFORM_COLOR_OFFSET = DEFAULT_COLOR_OFFSET
    DEFAULT_ADJUST_OFFSET = DEFAULT_COLOR_OFFSET
    ALIAS = 'alias_color'
    GROUP = 'schemeGroup'
    RGBA = 'rgba'
    MULT = 'mult'
    OFFSET = 'offset'
    TRANSFORM = 'transform'
    ADJUST = 'adjust'
    DEFAULTS = {OFFSET: DEFAULT_COLOR_OFFSET,
     RGBA: DEFAULT_RGBA_COLOR,
     MULT: DEFAULT_TRANSFORM_COLOR_MULT,
     ALIAS: DEFAULT_ALIAS_COLOR}
    VECTOR4_NAMES = (RGBA, MULT, OFFSET)
    STRING_NAMES = (ALIAS, GROUP)
    DEFAULT_TAG = 'default'
    COLOR_BLIND_TAG = 'color_blind'
    DEFAULT_SCHEME = {'alias_color': DEFAULT_ALIAS_COLOR,
     'rgba': DEFAULT_RGBA_COLOR,
     'transform': {'mult': DEFAULT_TRANSFORM_COLOR_MULT,
                   'offset': DEFAULT_TRANSFORM_COLOR_OFFSET},
     'adjust': {'offset': DEFAULT_ADJUST_OFFSET}}

    def __init__(self):
        self.__colors = {}

    def clear(self):
        self.__colors.clear()

    def __readXML(self, xmlCtx):
        xmlHash = self.__readHash(xmlCtx)
        xmlHash = self.__overrideTags(xmlHash, xmlHash)
        for scheme_name in xmlHash.keys():
            scheme = xmlHash[scheme_name]
            color_scheme = self.__readColorScheme(scheme)
            self.__colors[scheme_name] = color_scheme

    def __readHash(self, rootSection):
        outcome = {}
        for scheme_name, scheme_section in rootSection.items():
            if scheme_name in self.VECTOR4_NAMES:
                outcome[scheme_name] = self.__readVector4(rootSection, scheme_name)
            elif scheme_name in self.STRING_NAMES:
                outcome[scheme_name] = self.__readString(rootSection, scheme_name)
            else:
                outcome[scheme_name] = self.__readHash(scheme_section)

        return outcome

    def __overrideTags(self, rootSection, baseHash):
        keys = baseHash.keys()
        defaultExists = self.DEFAULT_TAG in keys
        for key in keys:
            if key == self.GROUP:
                groupNames = baseHash[key].split(' ')
                del baseHash[key]
                for groupName in groupNames:
                    insertingSection = rootSection[groupName]
                    overrideDefaultExists = self.DEFAULT_TAG in insertingSection.keys()
                    if defaultExists != overrideDefaultExists and len(keys) > 1:
                        if defaultExists:
                            LOG_ERROR('schemeGroup tag requires "default" tag. Failed Tag:\n' + str(baseHash))
                        else:
                            LOG_ERROR('schemeGroup tag requires to delete a "default" tag. Failed Tag:\n' + str(baseHash))
                        return baseHash
                    for subKey in insertingSection.keys():
                        if subKey not in baseHash.keys():
                            baseHash[subKey] = insertingSection[subKey]
                        else:
                            baseHash[subKey].update(insertingSection[subKey])

                baseHash = self.__overrideTags(rootSection, baseHash)
            else:
                section = baseHash[key]
                if key not in self.VECTOR4_NAMES and key not in self.STRING_NAMES:
                    baseHash[key] = self.__overrideTags(rootSection, section)

        return baseHash

    def __readColorScheme(self, hash):
        color_scheme = {self.DEFAULT_TAG: None}
        section = hash[self.DEFAULT_TAG] if self.DEFAULT_TAG in hash.keys() else None
        if section is not None:
            color_scheme[self.DEFAULT_TAG] = self.__readColorSection(section)
            if self.COLOR_BLIND_TAG in hash.keys():
                section = hash[self.COLOR_BLIND_TAG]
                if section is not None:
                    color_scheme[self.COLOR_BLIND_TAG] = self.__readColorSection(section)
        else:
            color_scheme[self.DEFAULT_TAG] = self.__readColorSection(hash)
        return color_scheme

    def __readVector4(self, section, tagName):
        value = section[tagName]
        return value.asVector4

    def __readString(self, section, tagName):
        value = section[tagName]
        return value.asString

    def __readTransformSection(self, section):
        mult = self.DEFAULT_TRANSFORM_COLOR_MULT
        offset = self.DEFAULT_TRANSFORM_COLOR_OFFSET
        processed = section['transform']
        if processed is not None:
            mult = self.__readVector4(processed, 'mult', self.DEFAULT_TRANSFORM_COLOR_MULT)
            offset = self.__readVector4(processed, 'offset', self.DEFAULT_TRANSFORM_COLOR_OFFSET)
        return {'mult': mult,
         'offset': offset}

    def __readColorSection(self, section):
        color_scheme = self.__initColorScheme(section)
        color_scheme = self.__readFilters(section, color_scheme)
        return color_scheme

    def __initColorScheme(self, section):
        keys = section.keys()
        color_scheme = {self.ALIAS: section[self.ALIAS] if self.ALIAS in keys else self.DEFAULT_ALIAS_COLOR,
         self.RGBA: section[self.RGBA] if self.RGBA in keys else self.DEFAULT_RGBA_COLOR}
        return color_scheme

    def __readFilters(self, section, color_scheme):
        keys = section.keys()
        color_scheme[self.TRANSFORM] = {self.MULT: self.DEFAULT_TRANSFORM_COLOR_MULT,
         self.OFFSET: self.DEFAULT_TRANSFORM_COLOR_OFFSET}
        if self.TRANSFORM in keys:
            transformSection = section[self.TRANSFORM]
            transformKeys = transformSection.keys()
            if self.MULT in transformKeys:
                color_scheme[self.TRANSFORM][self.MULT] = transformSection[self.MULT]
            if self.OFFSET in transformKeys:
                color_scheme[self.TRANSFORM][self.OFFSET] = transformSection[self.OFFSET]
        color_scheme[self.ADJUST] = {self.OFFSET: self.DEFAULT_ADJUST_OFFSET}
        if self.ADJUST in keys:
            if self.OFFSET in section[self.ADJUST].keys():
                color_scheme[self.ADJUST][self.OFFSET] = section[self.ADJUST][self.OFFSET]
        return color_scheme

    def load(self):
        xmlCtx = ResMgr.openSection(self.XML_PATH)
        if xmlCtx is None:
            _xml.raiseWrongXml(None, self.XML_PATH, 'can not open or read')
        self.__readXML(xmlCtx)
        return

    def items(self):
        return self.__colors.items()

    def schemasNames(self):
        return self.__colors.keys()

    def getColorScheme(self, schemeName):
        return self.__colors.get(schemeName)

    def getSubScheme(self, schemeName, group):
        scheme = self.getColorScheme(schemeName)
        if scheme is None:
            LOG_WARNING('Color scheme not found', schemeName, group)
            return self.DEFAULT_SCHEME
        elif group in scheme:
            return scheme[group]
        else:
            return scheme['default']

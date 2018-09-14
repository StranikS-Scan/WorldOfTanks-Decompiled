# Embedded file name: scripts/client/gui/Scaleform/ColorSchemeManager.py
import types
import Math, ResMgr
from debug_utils import LOG_ERROR, LOG_WARNING
from windows import UIInterface

class _ColorSchemeManager(UIInterface):
    COLOR_SCHEMES_FILE = 'gui/gui_colors.xml'
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
    GET_COLORS = 'colorSchemeManager.getColors'
    VECTOR4_NAMES = (RGBA, MULT, OFFSET)
    STRING_NAMES = (ALIAS, GROUP)
    DEFAULT_TAG = 'default'
    COLOR_BLIND_TAG = 'color_blind'
    __colors = {}
    __isXMLRead = False

    def __init__(self):
        UIInterface.__init__(self)
        self.__colorGroup = 'default'
        if not _ColorSchemeManager.__isXMLRead:
            _ColorSchemeManager.__isXMLRead = True
            self.__readXML()
        self.inited = False

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({self.GET_COLORS: self.onGetColors})
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.__onAccountSettingsChange
        self.update()
        self.inited = True

    def dispossessUI(self):
        self.inited = False
        if self.uiHolder is not None:
            self.uiHolder.removeExternalCallbacks(self.GET_COLORS)
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.__onAccountSettingsChange
        UIInterface.dispossessUI(self)
        return

    def onGetColors(self, _):
        self.__notifyFlash()

    def update(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        isColorBlind = g_settingsCore.getSetting('isColorBlind')
        self.__colorGroup = 'color_blind' if isColorBlind else 'default'
        self.__notifyFlash()

    def __onAccountSettingsChange(self, diff):
        if 'isColorBlind' in diff:
            self.update()

    def __readXML(self):
        rootSection = ResMgr.openSection(self.COLOR_SCHEMES_FILE)
        if rootSection is None:
            LOG_ERROR('Color schemes file loading failed: %s' % self.COLOR_SCHEMES_FILE)
            return
        else:
            xmlHash = self.__readHash(rootSection)
            xmlHash = self.__overrideTags(xmlHash, xmlHash)
            for scheme_name in xmlHash.keys():
                scheme = xmlHash[scheme_name]
                color_scheme = self.__readColorScheme(scheme)
                self.__colors[scheme_name] = color_scheme

            return

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
                        if subKey not in baseHash.keys() or not type(baseHash[subKey]) == types.DictType:
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

    def __readVector4(self, section, tagName):
        value = section[tagName]
        return value.asVector4

    def __readString(self, section, tagName):
        value = section[tagName]
        return value.asString

    def __notifyFlash(self):
        args = []
        for scheme_name, color_scheme in self.__colors.iteritems():
            colorGroup = self.__colorGroup if self.__colorGroup in color_scheme.keys() else 'default'
            scheme_params = color_scheme[colorGroup]
            rgba = scheme_params['rgba']
            args.append(scheme_name)
            args.append(scheme_params['alias_color'])
            args.append((int(rgba[0]) << 16) + (int(rgba[1]) << 8) + (int(rgba[2]) << 0))
            args.extend(scheme_params['adjust']['offset'].tuple())
            args.extend(scheme_params['transform']['mult'].tuple())
            args.extend(scheme_params['transform']['offset'].tuple())

        self.call('colorSchemeManager.setColors', args)

    @classmethod
    def getColorGroup(cls, isColorBlind = False):
        if isColorBlind:
            return 'color_blind'
        return 'default'

    @classmethod
    def getScheme(cls, schemeName):
        return cls.__colors.get(schemeName)

    @classmethod
    def getSubScheme(cls, schemeName, isColorBlind = False):
        scheme = cls.getScheme(schemeName)
        if scheme is not None:
            group = cls.getColorGroup(isColorBlind=isColorBlind)
            sub = scheme[group] if group in scheme else scheme['default']
        else:
            LOG_WARNING('Color scheme not found ', schemeName, isColorBlind, cls.__colors.keys())
            sub = {'alias_color': cls.DEFAULT_ALIAS_COLOR,
             'rgba': cls.DEFAULT_RGBA_COLOR,
             'adjust': {'offset': cls.DEFAULT_ADJUST_OFFSET},
             'transform': {'mult': cls.DEFAULT_TRANSFORM_COLOR_MULT,
                           'offset': cls.DEFAULT_TRANSFORM_COLOR_OFFSET}}
        return sub

    @classmethod
    def getRGBA(cls, schemeName, isColorBlind = False):
        return cls.getSubScheme(schemeName, isColorBlind)['rgba']

    @classmethod
    def _makeRGB(cls, subScheme):
        rgba = subScheme.get('rgba', (0, 0, 0))
        return (int(rgba[0]) << 16) + (int(rgba[1]) << 8) + (int(rgba[2]) << 0)

    @classmethod
    def _makeAdjustTuple(cls, subScheme):
        return subScheme['adjust']['offset'].tuple()

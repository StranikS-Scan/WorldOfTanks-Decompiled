# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/ColorSchemeManager.py
# Compiled at: 2018-11-29 14:33:44
from account_helpers.AccountSettings import AccountSettings
import BigWorld, Math, ResMgr
from debug_utils import LOG_ERROR
from windows import UIInterface

class _ColorSchemeManager(UIInterface):
    COLOR_SCHEMES_FILE = 'gui/gui_colors.xml'
    DEFAULT_ALIAS_COLOR = None
    DEFAULT_RGBA_COLOR = Math.Vector4(255, 255, 255, 255)
    DEFAULT_TRANSFORM_COLOR_MULT = Math.Vector4(1, 1, 1, 1)
    DEFAULT_TRANSFORM_COLOR_OFFSET = Math.Vector4(0, 0, 0, 0)
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
        self.uiHolder.addExternalCallbacks({'colorSchemeManager.getColors': self.onGetColors})
        self.update()
        self.inited = True

    def dispossessUI(self):
        self.inited = False
        if self.uiHolder is not None:
            self.uiHolder.removeExternalCallbacks('colorSchemeManager.getColors')
        UIInterface.dispossessUI(self)
        return

    def onGetColors(self, _):
        self.__notifyFlash()

    def update(self):
        isColorBlind = AccountSettings.getSettings('isColorBlind')
        self.__colorGroup = 'color_blind' if isColorBlind else 'default'
        self.__notifyFlash()

    def __readColorSection(self, section):
        color_scheme = {}
        processed = section['alias_color']
        color_scheme['alias_color'] = processed.asString if processed is not None else self.DEFAULT_ALIAS_COLOR
        processed = section['rgba']
        color_scheme['rgba'] = processed.asVector4 if processed is not None else self.DEFAULT_RGBA_COLOR
        processed = section['transform']
        if processed is not None:
            mult_section = processed['mult']
            offset_section = processed['offset']
            color_scheme['transform'] = {'mult': mult_section.asVector4 if mult_section is not None else self.DEFAULT_TRANSFORM_COLOR_MULT,
             'offset': offset_section.asVector4 if offset_section is not None else self.DEFAULT_TRANSFORM_COLOR_OFFSET}
        else:
            color_scheme['transform'] = {'mult': self.DEFAULT_TRANSFORM_COLOR_MULT,
             'offset': self.DEFAULT_TRANSFORM_COLOR_OFFSET}
        return color_scheme

    def __readXML(self):
        section = ResMgr.openSection(self.COLOR_SCHEMES_FILE)
        if section is None:
            LOG_ERROR('Color schemes file loading failed: %s' % self.COLOR_SCHEMES_FILE)
            return
        else:
            for scheme_name, scheme_section in section.items():
                color_scheme = {'default': None}
                section = scheme_section['default']
                if section is not None:
                    color_scheme['default'] = self.__readColorSection(section)
                    section = scheme_section['color_blind']
                    if section is not None:
                        color_scheme['color_blind'] = self.__readColorSection(section)
                else:
                    color_scheme['default'] = self.__readColorSection(scheme_section)
                self.__colors[scheme_name] = color_scheme

            return

    def __notifyFlash(self):
        args = []
        for scheme_name, color_scheme in self.__colors.iteritems():
            colorGroup = self.__colorGroup if self.__colorGroup in color_scheme.keys() else 'default'
            scheme_params = color_scheme[colorGroup]
            rgba = scheme_params['rgba']
            args.append(scheme_name)
            args.append(scheme_params['alias_color'])
            args.append((int(rgba[0]) << 16) + (int(rgba[1]) << 8) + (int(rgba[2]) << 0))
            args.extend(scheme_params['transform']['mult'].tuple())
            args.extend(scheme_params['transform']['offset'].tuple())

        self.call('colorSchemeManager.setColors', args)

    @classmethod
    def getColorGroup(cls, isColorBlind=False):
        if isColorBlind:
            return 'color_blind'

    @classmethod
    def getScheme(cls, schemeName):
        return cls.__colors.get(schemeName)

    @classmethod
    def getSubScheme(cls, schemeName, isColorBlind=False):
        scheme = cls.getScheme(schemeName)
        group = cls.getColorGroup(isColorBlind=isColorBlind)
        if group in scheme:
            return scheme[group]
        return scheme['default']

    @classmethod
    def _makeRGB(cls, subScheme):
        rgba = subScheme.get('rgba', (0, 0, 0))
        return (int(rgba[0]) << 16) + (int(rgba[1]) << 8) + (int(rgba[2]) << 0)

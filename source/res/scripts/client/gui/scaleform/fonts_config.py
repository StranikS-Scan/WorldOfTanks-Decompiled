# Embedded file name: scripts/client/gui/Scaleform/fonts_config.py
from debug_utils import LOG_NOTE
from gui.Scaleform import SCALEFORM_FONT_CONFIG_PATH, SCALEFORM_FONT_LIB_PATH, SCALEFORM_DEFAULT_CONFIG_NAME
import ResMgr
import _Scaleform
FONT_STYLE_DEFAULT = 16
FONT_STYLE_NORMAL = 0
FONT_STYLE_ITALIC = 1
FONT_STYLE_BOLD = 2
FONT_STYLE_BOLD_ITALIC = FONT_STYLE_ITALIC | FONT_STYLE_BOLD
FONT_STYLE_NAMES = {'Regular': FONT_STYLE_DEFAULT,
 'Normal': FONT_STYLE_NORMAL,
 'Italic': FONT_STYLE_ITALIC,
 'Bold': FONT_STYLE_BOLD}

class FONT_CONFIG_LOAD_RESULT(object):
    loaded, alreadyLoaded, notFound = range(3)


class FontConfig(object):

    def __init__(self, configName, fontlib, aliases):
        self.__configName = configName
        self.__fontlib = fontlib
        self.__aliases = aliases
        self.__loaded = False

    def load(self):
        if self.__loaded:
            return FONT_CONFIG_LOAD_RESULT.alreadyLoaded
        for embedded, (runtime, fontStyle, scaleFactor) in self.__aliases.items():
            _Scaleform.mapFont(embedded, runtime, fontStyle, scaleFactor)

        movieDef = _Scaleform.MovieDef(SCALEFORM_FONT_LIB_PATH + '/' + self.__fontlib)
        movieDef.setAsFontMovie()
        movieDef.addToFontLibrary()
        self.__loaded = True
        return FONT_CONFIG_LOAD_RESULT.loaded

    def configName(self):
        return self.__configName

    def isLoaded(self):
        return self.__loaded


class FontConfigMap(object):

    def __init__(self):
        self.__configs = dict()
        self.__readXml()

    def __readAliasSection(self, section, aliases):
        embedded = section.readString('embedded')
        runtime = section.readString('runtime')
        fontStyle = FONT_STYLE_DEFAULT
        if section.has_key('flags'):
            flagNames = section.readString('flags').split(' ')
            for name in flagNames:
                try:
                    fontStyle |= FONT_STYLE_NAMES[name]
                except KeyError:
                    LOG_NOTE('Available font style flags are:', FONT_STYLE_NAMES.keys())
                    raise Exception, "Flag isn't correct: {0:>s}.".format(name)

        scaleFactor = section.readFloat('scaleFactor', 1.0)
        aliases[embedded] = (runtime, fontStyle, scaleFactor)

    def __readXml(self):
        dataSection = ResMgr.openSection(SCALEFORM_FONT_CONFIG_PATH)
        if dataSection is None:
            raise IOError, 'can not open <%s>.' % SCALEFORM_FONT_CONFIG_PATH
        for tag, fontconfig in dataSection.items():
            if tag == 'config':
                aliases = dict()
                if fontconfig.has_key('name'):
                    configName = fontconfig.readString('name')
                else:
                    raise Exception, 'You must specify the name of the configuration'
                if fontconfig.has_key('fontlib'):
                    fontlib = fontconfig.readString('fontlib')
                else:
                    raise Exception, 'You must specify the font library file'
                if fontconfig.has_key('map'):
                    map = fontconfig['map']
                    for tag, alias in map.items():
                        if tag == 'alias':
                            self.__readAliasSection(alias, aliases)

                self.__configs[configName] = FontConfig(configName, fontlib, aliases)

        return

    def loadFonts(self, configName):
        result = FONT_CONFIG_LOAD_RESULT.notFound
        fontConfig = self.__configs.get(configName)
        if fontConfig:
            result = fontConfig.load()
        return result

    def load(self):
        return self.loadFonts(SCALEFORM_DEFAULT_CONFIG_NAME)


g_fontConfigMap = FontConfigMap()

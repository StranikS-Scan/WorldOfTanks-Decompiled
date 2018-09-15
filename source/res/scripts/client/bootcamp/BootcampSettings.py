# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampSettings.py
import ResMgr
from copy import deepcopy
from BootcampConstants import HINT_TYPE, HINT_NAMES
from helpers.i18n import makeString
from debug_utils_bootcamp import LOG_CURRENT_EXCEPTION_BOOTCAMP, LOG_ERROR_BOOTCAMP

class _HintParamType(object):
    FLOAT = 0
    STRING = 1
    INT = 2


class _LessonConfiguration(object):

    def __init__(self):
        self.hints = {}
        self.prebattle = {}
        self.ribbons = []
        self.visiblePanels = []
        self.hiddenPanels = []
        self.lessonPages = []


class BattleSettings(object):
    SETTINGS_XML_PATH = 'scripts/bootcamp_docs/battle_settings.xml'
    DEFAULTS_XML_PATH = 'scripts/bootcamp_docs/battle_defaults.xml'
    HINTS_PARAMS = {HINT_TYPE.HINT_MOVE: {'distance': _HintParamType.FLOAT},
     HINT_TYPE.HINT_NO_MOVE: {'seconds': _HintParamType.FLOAT},
     HINT_TYPE.HINT_MOVE_TURRET: {'angle': _HintParamType.FLOAT},
     HINT_TYPE.HINT_NO_MOVE_TURRET: {'seconds': _HintParamType.FLOAT},
     HINT_TYPE.HINT_ADVANCED_SNIPER: {'angle': _HintParamType.FLOAT,
                                      'time_between': _HintParamType.FLOAT,
                                      'message_sniper_before': _HintParamType.STRING,
                                      'target_name': _HintParamType.STRING,
                                      'message_sniper_exit': _HintParamType.STRING,
                                      'enter_voiceover': _HintParamType.STRING,
                                      'exit_voiceover': _HintParamType.STRING,
                                      'weak_points_voiceover': _HintParamType.STRING},
     HINT_TYPE.HINT_MESSAGE_SNEAK: {'timeout_between': _HintParamType.FLOAT},
     HINT_TYPE.HINT_AIM: {'aimFactor': _HintParamType.FLOAT,
                          'shootCount': _HintParamType.INT},
     HINT_TYPE.HINT_PLAYER_DETECT_ENEMIES: {'count': _HintParamType.INT},
     HINT_TYPE.HINT_SNIPER_ON_DISTANCE: {'distance': _HintParamType.FLOAT,
                                         'angle': _HintParamType.FLOAT,
                                         'exitHintText': _HintParamType.STRING,
                                         'exitHintDelay': _HintParamType.FLOAT,
                                         'enter_voiceover': _HintParamType.STRING,
                                         'exit_voiceover': _HintParamType.STRING},
     HINT_TYPE.HINT_SECONDARY_SNIPER: {'distance': _HintParamType.FLOAT,
                                       'angle': _HintParamType.FLOAT},
     HINT_TYPE.HINT_WAIT_RELOAD: {'maxShootErrorsCount': _HintParamType.INT},
     HINT_TYPE.HINT_EXIT_GAME_AREA: {'distanceToBorder': _HintParamType.FLOAT},
     HINT_TYPE.HINT_MOVE_TO_MARKER: {'maxDistance': _HintParamType.FLOAT},
     HINT_TYPE.HINT_START_NARRATIVE: {'time_before_shown': _HintParamType.FLOAT},
     HINT_TYPE.HINT_LOW_HP: {'first_percent': _HintParamType.FLOAT,
                             'second_percent': _HintParamType.FLOAT},
     HINT_TYPE.HINT_SHOT_WHILE_MOVING: {'maxShootErrorsCount': _HintParamType.INT}}

    def __init__(self):
        super(BattleSettings, self).__init__()
        self.__defaults = {'hints': {},
         'ribbons': [],
         'panels': [],
         'lessonPages': {},
         'prebattleHints': set()}
        self.__config = {}
        try:
            self.__loadDefaults()
            self.__loadConfig()
        except:
            LOG_CURRENT_EXCEPTION_BOOTCAMP()

    def lessonConfiguration(self, lessonId):
        return self.__config.get(lessonId, _LessonConfiguration())

    @property
    def defaults(self):
        return self.__defaults

    def __readPrebattleSection(self, prebattleSection):
        prebattleSettings = {}
        if prebattleSection.has_key('timeout'):
            prebattleSettings['timeout'] = prebattleSection['timeout'].asFloat
        if prebattleSection.has_key('hints'):
            prebattleSettings['visible_hints'] = set(prebattleSection['hints'].asString.split())
            prebattleSettings['invisible_hints'] = self.__defaults['prebattle'] - prebattleSettings['visible_hints']
        return prebattleSettings

    def __readRibbonsSection(self, ribbonsSection):
        defaultRibbons = self.__defaults['ribbons']
        ribbonsSettings = []
        ribbonNames = ribbonsSection.asString.split()
        for ribName in ribbonNames:
            if ribName in defaultRibbons:
                ribbonsSettings.append(ribName)
            LOG_ERROR_BOOTCAMP('Unknown ribbon name (%s)' % ribName)

        return ribbonsSettings

    def __readLoadingLessonsSection(self, lessonsSection):
        return lessonsSection.asString.split()

    def __readPanelsSection(self, panelsSection):
        panels = []
        defaultPanels = self.__defaults['panels']
        panelNames = panelsSection.asString.split()
        for name in panelNames:
            if name in defaultPanels:
                panels.append(name)
            LOG_ERROR_BOOTCAMP('Unknown panel name (%s)' % name)

        return panels

    def __readHintSection(self, hintName, hintSection, isDefaultSection=False):
        singleHint = {}
        hintId = HINT_NAMES.index(hintName)
        hintParams = BattleSettings.HINTS_PARAMS.get(hintId, None)
        if hintParams is not None:
            for keyParam, valueType in hintParams.iteritems():
                if isDefaultSection or hintSection.has_key(keyParam):
                    if valueType == _HintParamType.FLOAT:
                        singleHint[keyParam] = hintSection[keyParam].asFloat
                    elif valueType == _HintParamType.STRING:
                        singleHint[keyParam] = makeString(hintSection[keyParam].asString)
                    elif valueType == _HintParamType.INT:
                        singleHint[keyParam] = hintSection[keyParam].asInt
                    else:
                        raise Exception('Unknown hint param type (%d)', valueType)

        if hintSection.has_key('cooldown_after'):
            singleHint['cooldown_after'] = hintSection['cooldown_after'].asFloat
        if hintSection.has_key('time_completed'):
            singleHint['time_completed'] = hintSection['time_completed'].asFloat
        if hintSection.has_key('voiceover'):
            singleHint['voiceover'] = hintSection['voiceover'].asString
        if hintSection.has_key('timeout'):
            singleHint['timeout'] = hintSection['timeout'].asFloat
        if hintSection.has_key('message'):
            singleHint['message'] = makeString(hintSection['message'].asString)
        if not isDefaultSection and hintSection.has_key('names'):
            namesSection = hintSection['names']
            namesList = [ value.asString for key, value in namesSection.items() if key == 'name' ]
            singleHint['names'] = namesList
        return singleHint

    def __loadDefaults(self):
        defaultSettingsConfig = ResMgr.openSection(BattleSettings.DEFAULTS_XML_PATH)
        if not defaultSettingsConfig:
            raise Exception("Can't open defaults config file (%s)" % BattleSettings.DEFAULTS_XML_PATH)
        hints = self.__defaults['hints']
        for sectionName in ('primary_hints', 'secondary_hints'):
            hintsSection = defaultSettingsConfig[sectionName]
            for hintName, hintDefaultSection in hintsSection.items():
                hints[hintName] = self.__readHintSection(hintName, hintDefaultSection, True)

        ribString = defaultSettingsConfig['ribbons'].asString
        self.__defaults['ribbons'] = ribString.split()
        panelsString = defaultSettingsConfig['panels'].asString
        self.__defaults['panels'] = panelsString.split()
        prebattleHintsString = defaultSettingsConfig['prebattle'].asString
        self.__defaults['prebattle'] = set(prebattleHintsString.split())
        self.__readDefaultPagesSection(defaultSettingsConfig['lesson_pages'])

    def __loadConfig(self):
        settingsConfig = ResMgr.openSection(BattleSettings.SETTINGS_XML_PATH)
        if not settingsConfig:
            raise Exception("Can't open defaults config file (%s)" % BattleSettings.SETTINGS_XML_PATH)
        for name, xmlSection in settingsConfig.items():
            if name == 'lesson':
                lessonId = xmlSection['id'].asInt
                lessonConf = _LessonConfiguration()
                self.__config[lessonId] = lessonConf
                defaultsHints = self.__defaults['hints']
                for sectionName in ('primary_hints', 'secondary_hints'):
                    if xmlSection.has_key(sectionName):
                        hintsXmlSection = xmlSection[sectionName]
                        for hintName, hintSection in hintsXmlSection.items():
                            curHintInfo = deepcopy(defaultsHints[hintName])
                            curHintInfo.update(self.__readHintSection(hintName, hintSection, False))
                            lessonConf.hints[hintName] = curHintInfo

                if xmlSection.has_key('prebattle'):
                    lessonConf.prebattle = self.__readPrebattleSection(xmlSection['prebattle'])
                if xmlSection.has_key('ribbons'):
                    lessonConf.ribbons = self.__readRibbonsSection(xmlSection['ribbons'])
                if xmlSection.has_key('lesson_pages'):
                    lessonConf.lessonPages = self.__readLoadingLessonsSection(xmlSection['lesson_pages'])
                if xmlSection.has_key('panels'):
                    lessonConf.visiblePanels = self.__readPanelsSection(xmlSection['panels'])
                    lessonConf.hiddenPanels = list(set(self.__defaults['panels']) - set(lessonConf.visiblePanels))

    def __readDefaultPagesSection(self, pagesXmlSection):
        lessonPagesDefaults = self.__defaults['lessonPages']
        for pageName, pageProps in pagesXmlSection.items():
            lessonProps = {}
            for itemName, itemProps in pageProps.items():
                lessonProps[itemName + 'Text'] = makeString(itemProps['text'].asString)
                lessonProps[itemName + 'AutoSize'] = itemProps['autoSize'].asString

            lessonPagesDefaults[pageName] = lessonProps


class GarageSettings(object):
    DEFAULTS_XML_PATH = 'scripts/bootcamp_docs/garage_defaults.xml'

    def __init__(self):
        super(GarageSettings, self).__init__()
        self.__defaults = {'panels': {}}
        try:
            defaultSettingsConfig = ResMgr.openSection(GarageSettings.DEFAULTS_XML_PATH)
            if not defaultSettingsConfig:
                raise Exception("Can't open defaults config file (%s)" % GarageSettings.DEFAULTS_XML_PATH)
            panelSection = defaultSettingsConfig['panels']
            panels = self.__defaults['panels']
            visiblePanels = panelSection['visible'].asString
            visiblePanelNames = visiblePanels.split()
            for panelName in visiblePanelNames:
                panels['hide' + panelName] = False

            invisiblePanels = panelSection['invisible'].asString
            invisiblePanelNames = invisiblePanels.split()
            for panelName in invisiblePanelNames:
                panels['hide' + panelName] = True

        except:
            LOG_CURRENT_EXCEPTION_BOOTCAMP()

    @property
    def defaults(self):
        return self.__defaults


_GarageSettings = GarageSettings()
_BattleSettings = BattleSettings()

def getBattleSettings(lessonId):
    return _BattleSettings.lessonConfiguration(lessonId)


def getBattleDefaults():
    return _BattleSettings.defaults


def getGarageDefaults():
    return _GarageSettings.defaults

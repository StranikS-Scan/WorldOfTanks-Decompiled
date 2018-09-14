# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/GuiSettings.py
from collections import namedtuple
import nations
import constants
import resource_helper
from debug_utils import LOG_NOTE, LOG_CURRENT_EXCEPTION
from helpers import getClientLanguage, time_utils
from gui import macroses
GUI_SETTINGS_FILE_PATH = 'gui/gui_settings.xml'
VIDEO_SETTINGS_FILE_PATH = 'gui/video_settings.xml'
MovingTextProps = namedtuple('MovingTextProps', 'show internalBrowser')
LoginRssFeedProps = namedtuple('LoginRssFeedProps', 'show url internalBrowser')
EULAProps = namedtuple('EULAProps', 'full url')
BrowserProps = namedtuple('BrowserProps', 'url params')
PostBattleExchangeProps = namedtuple('PostBattleExchangeProps', 'enabled url')
EncyclopediaProps = namedtuple('EncyclopediaProps', 'url enabled')
_MacrosValue = namedtuple('MacrosValue', 'macros dictValue')

def _readMacros(xmlCtx, section, valueName='value'):
    result = {}
    name = resource_helper.readItemName(xmlCtx, section)
    macros = _readItemMacros(xmlCtx, section)
    subCtx, subSection = resource_helper.getSubSection(xmlCtx, section, valueName)
    for nextCtx, nextSection in resource_helper.getIterator(subCtx, subSection):
        item = resource_helper.readItem(nextCtx, nextSection)
        if not item.name:
            raise resource_helper.ResourceError(nextCtx, '{0}: name is required in each item'.format(name))
        result[item.name] = item.value

    return resource_helper.ResourceItem('macros', name, _MacrosValue(macros, result))


def _readItemMacros(xmlCtx, section, keys=None):
    return resource_helper.readItemAttr(xmlCtx, section, 'macros', default='', keys=keys)


def _convertVector4ToTuple(_, item):
    return item.value.tuple()


def _convertToNamedTuple(settings, item):
    return settings._replace(**item.value)


def _convertEULASetting(settings, item):
    value = item.value
    if 'full' in value:
        value['full'] = getClientLanguage() in value['full']
    else:
        value['full'] = False
    return settings._replace(**item.value)


def _convertEncyclopedia(_, item):
    value = item.value
    if isinstance(value, _MacrosValue):
        dictValue = value.dictValue
        dictValue['enabled'] = getClientLanguage() in dictValue.pop('languages', [])
    else:
        value['enabled'] = getClientLanguage() in value.pop('languages', [])
    return value


_SETTING_CONVERTERS = {'loginRssFeed': _convertToNamedTuple,
 'movingText': _convertToNamedTuple,
 'eula': _convertEULASetting,
 'markerScaleSettings': _convertVector4ToTuple,
 'markerBgSettings': _convertVector4ToTuple,
 'browser': _convertToNamedTuple,
 'postBattleExchange': _convertToNamedTuple,
 'encyclopedia': _convertEncyclopedia}
_DEFAULT_SETTINGS = {'registrationURL': '',
 'registrationProxyURL': '',
 'recoveryPswdURL': '',
 'paymentURL': '',
 'securitySettingsURL': '',
 'supportURL': '',
 'migrationURL': '',
 'nations_order': nations.AVAILABLE_NAMES[:],
 'language_bar': [],
 'guiEnabled': True,
 'disabledUIElements': [],
 'trainingObserverModeEnabled': False,
 'minimapSize': True,
 'goldTransfer': False,
 'voiceChat': True,
 'technicalInfo': True,
 'nationHangarSpace': False,
 'customizationHorns': False,
 'showMinimapSuperHeavy': False,
 'showMinimapDeath': True,
 'permanentMinimapDeath': False,
 'markerHitSplashDuration': 0,
 'sixthSenseDuration': 0,
 'minimapDeathDuration': 0,
 'rememberPassVisible': True,
 'clearLoginValue': False,
 'markerScaleSettings': (0, 0, 0, 0),
 'markerBgSettings': (0, 0, 0, 0),
 'specPrebatlesVisible': True,
 'roaming': True,
 'movingText': MovingTextProps(False, False),
 'loginRssFeed': LoginRssFeedProps(True, '', False),
 'eula': EULAProps(False, ''),
 'igrCredentialsReset': False,
 'igrEnabled': False,
 'battleEndWarningEnabled': True,
 'isPollEnabled': False,
 'csisRequestRate': 0,
 'showSectorLines': False,
 'showDirectionLine': False,
 'isBattleCmdCoolDownVisible': False,
 'browser': BrowserProps('about:blank', ''),
 'reportBugLinks': [],
 'cache': [],
 'imageCache': [],
 'postBattleExchange': PostBattleExchangeProps(False, ''),
 'actionComeToEnd': time_utils.QUARTER_HOUR,
 'goldFishActionShowCooldown': 86400,
 'guiScale': [],
 'playerFeedbackDelay': 0.75,
 'allowedNotSupportedGraphicSettings': {},
 'userRoomsService': '',
 'cryptLoginInfo': True,
 'compulsoryIntroVideos': [],
 'encyclopedia': {},
 'useDefaultGunMarkers': False,
 'spgAlternativeAimingCameraEnabled': False,
 'tokenShopAvailabilityURL': '',
 'tokenShopAPIKey': ''}

class GuiSettings(object):

    def __init__(self):
        """
        constructs GuiSettings instance using values from guiPresetsResource
        """
        self.__settings = _DEFAULT_SETTINGS.copy()
        settings = {}
        for item in resource_helper.root_iterator(GUI_SETTINGS_FILE_PATH, customReaders={'macros': _readMacros}):
            if item.name in _SETTING_CONVERTERS:
                setting = _DEFAULT_SETTINGS[item.name]
                converter = _SETTING_CONVERTERS[item.name]
                value = converter(setting, item)
            else:
                value = item.value
            settings[item.name] = value

        if constants.IS_DEVELOPMENT:
            diff = set(self.__settings.keys()) - set(settings.keys())
            if len(diff):
                LOG_NOTE('Settings are not in {0}:'.format(GUI_SETTINGS_FILE_PATH), diff)
        self.__settings.update(settings)

    def __getattr__(self, name):
        if name in self.__settings:
            return self.__applyMacros(self.__settings[name])
        raise AttributeError('Setting not found in {0}: {1}'.format(self.__class__, name))

    def __setattr__(self, name, value):
        if name == '_GuiSettings__settings':
            self.__dict__[name] = value
        elif name in self.__settings:
            raise AttributeError('Assignment is forbidden for {0}. Argument name: {1}'.format(self.__class__, name))

    def __contains__(self, item):
        return item in self.__settings

    @property
    def isShowLanguageBar(self):
        """
        @return: <bool> show laguage bar or not
        """
        try:
            return getClientLanguage() in self.language_bar
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return False

    def isEmpty(self, name):
        value = None
        if name in self.__settings:
            value = self.__applyMacros(self.__settings[name])
        return not value

    def isGuiEnabled(self):
        return self.guiEnabled or not constants.IS_DEVELOPMENT

    def lookup(self, name):
        settings = None
        if name in self.__settings:
            settings = self.__applyMacros(self.__settings[name])
        return settings

    def __applyMacros(self, value):
        if isinstance(value, _MacrosValue):
            macros = value.macros
            dictValue = value.dictValue
            simpleMacroses = macroses.getSyncMacroses()
            if macros in simpleMacroses:
                macrosKey = simpleMacroses[macros]()
            else:
                if macros == 'MACROS_DICT':
                    value = {}
                    for key, mValue in dictValue.iteritems():
                        value[key] = self.__applyMacros(mValue)

                    return value
                raise AttributeError("Unsupported macros '{0}', not found in {1}".format(macros, simpleMacroses))
            if macrosKey in dictValue:
                return self.__applyMacros(dictValue[macrosKey])
            if 'default' in dictValue:
                return self.__applyMacros(dictValue['default'])
            raise AttributeError("Incorrect section in {0}, dict {1} with macros '{2}' should contains item '{3}' or 'default'".format(GUI_SETTINGS_FILE_PATH, dictValue, macros, macrosKey))
        return value

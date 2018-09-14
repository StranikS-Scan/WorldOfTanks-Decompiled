# Embedded file name: scripts/client/gui/GuiSettings.py
from collections import namedtuple
import nations
import constants
import resource_helper
from debug_utils import *
from helpers import getClientLanguage
GUI_SETTINGS_FILE_PATH = 'gui/gui_settings.xml'
VIDEO_SETTINGS_FILE_PATH = 'gui/video_settings.xml'
MovingTextProps = namedtuple('MovingTextProps', 'show internalBrowser')
LoginRssFeedProps = namedtuple('LoginRssFeedProps', 'show url internalBrowser')
EULAProps = namedtuple('EULAProps', 'full url')

def _convertMovingTextSetting(settings, item):
    return settings._replace(**item.value)


def _convertLoginRssFeed(settings, item):
    return settings._replace(**item.value)


def _convertEULASetting(settings, item):
    value = item.value
    if 'full' in value:
        value['full'] = getClientLanguage() in value['full']
    else:
        value['full'] = False
    return settings._replace(**item.value)


def _convertVector4ToTuple(_, item):
    return item.value.tuple()


_SETTING_CONVERTERS = {'loginRssFeed': _convertLoginRssFeed,
 'movingText': _convertMovingTextSetting,
 'eula': _convertEULASetting,
 'markerScaleSettings': _convertVector4ToTuple,
 'markerBgSettings': _convertVector4ToTuple}
_DEFAULT_SETTINGS = {'registrationURL': '',
 'recoveryPswdURL': '',
 'paymentURL': '',
 'securitySettingsURL': '',
 'supportURL': '',
 'migrationURL': '',
 'nations_order': nations.AVAILABLE_NAMES[:],
 'language_bar': [],
 'guiEnabled': True,
 'trainingObserverModeEnabled': False,
 'minimapSize': True,
 'goldTransfer': False,
 'voiceChat': True,
 'technicalInfo': True,
 'nationHangarSpace': False,
 'customizationCamouflages': True,
 'customizationHorns': False,
 'customizationEmblems': True,
 'customizationInscriptions': True,
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
 'battleStatsInHangar': True,
 'freeXpToTankman': False,
 'roaming': True,
 'movingText': MovingTextProps(False, False),
 'loginRssFeed': LoginRssFeedProps(True, '', False),
 'eula': EULAProps(False, ''),
 'igrCredentialsReset': False,
 'igrEnabled': False,
 'isPollEnabled': False,
 'csisRequestRate': 0,
 'showSectorLines': False,
 'showDirectionLine': False,
 'isBattleCmdCoolDownVisible': False}

class GuiSettings(object):

    def __init__(self):
        """
        constructs GuiSettings instance using values from guiPresetsResource
        """
        self.__settings = _DEFAULT_SETTINGS.copy()
        ctx, section = resource_helper.getRoot(GUI_SETTINGS_FILE_PATH)
        settings = {}
        for ctx, subSection in resource_helper.getIterator(ctx, section):
            item = resource_helper.readItem(ctx, subSection, name='setting')
            if item.name in _SETTING_CONVERTERS:
                setting = _DEFAULT_SETTINGS[item.name]
                converter = _SETTING_CONVERTERS[item.name]
                value = converter(setting, item)
            else:
                value = item.value
            settings[item.name] = value

        if IS_DEVELOPMENT:
            diff = set(self.__settings.keys()) - set(settings.keys())
            if len(diff):
                LOG_NOTE('Settings are not in {0}:'.format(GUI_SETTINGS_FILE_PATH), diff)
        self.__settings.update(settings)
        for key, reader in externalReaders.iteritems():
            self.__settings[key] = reader()

    def __getattr__(self, name):
        if name in self.__settings:
            return self.__settings[name]
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
            value = self.__settings[name]
        return not value

    def isGuiEnabled(self):
        return self.guiEnabled or not constants.IS_DEVELOPMENT

    def lookup(self, name):
        settings = None
        if name in self.__settings:
            settings = self.__settings[name]
        return settings


class VideoSettings(object):

    def __init__(self):
        """
        Initialization.
        """
        super(VideoSettings, self).__init__()
        self.__setting = {'audio': {},
         'subtitles': {}}

    def read(self, path):
        """
        Reads video setting from file.
        @param path: path to file with video setting.
        """
        ctx, section = resource_helper.getRoot(path, safe=True)
        if section is None:
            LOG_WARNING('File with video settings not found. Uses default values', path)
            return
        else:
            subCtx, subSection = resource_helper.getSubSection(ctx, section, 'audio', safe=True)
            if subSection:
                self.__setting['audio'] = self.__readTracks(subCtx, subSection)
            subCtx, subSection = resource_helper.getSubSection(ctx, section, 'subtitles', safe=True)
            if subSection:
                self.__setting['subtitles'] = self.__readTracks(subCtx, subSection, offset=1)
            return self

    @property
    def audioTrack(self):
        """
        Returns number of audio track by language code. If track not found than
        returns 0.
        @return: number of audio track.
        """
        audio = self.__setting['audio']
        code = getClientLanguage()
        if code in audio:
            return audio[code]
        return 0

    @property
    def subtitleTrack(self):
        """
        Returns number of subtitle by language code. If track not found than
        returns 0.
        Note: subtitle track 0 turns subtitles off.
        @return: number of subtitle track.
        """
        subtitles = self.__setting['subtitles']
        code = getClientLanguage()
        if code in subtitles:
            return subtitles[code]
        return 0

    def __readTracks(self, ctx, section, offset = 0):
        result = {}
        iterator = resource_helper.getIterator(ctx, section)
        for idx, (subCtx, subSec) in enumerate(iterator):
            for langCtx, langSec in resource_helper.getIterator(subCtx, subSec):
                lang = resource_helper.readStringItem(langCtx, langSec).value
                if len(lang) > 0:
                    result[lang] = idx + offset

        return result


externalReaders = {'video': lambda : VideoSettings().read(VIDEO_SETTINGS_FILE_PATH)}

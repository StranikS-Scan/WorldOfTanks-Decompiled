# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/IntSettingsRequester.py
import BigWorld
import copy
import constants
from adisp import async, process
from debug_utils import LOG_ERROR
from gui.shared.utils import code2str

class IntSettingsRequester(object):
    """
    Setting dictionary presenting int settings keys by section names.
    Don't forget to duplicate new value in common.constanst.INT_USER_SETTINGS_KEYS
    """
    SETTINGS = {'VERSION': 0,
     'GAME': 1,
     'GRAPHICS': 2,
     'SOUND': 3,
     'CONTROLS': 4,
     'AIM_ARCADE_1': 43,
     'AIM_ARCADE_2': 44,
     'AIM_ARCADE_3': 45,
     'AIM_SNIPER_1': 46,
     'AIM_SNIPER_2': 47,
     'AIM_SNIPER_3': 48,
     'MARKERS_ENEMY': 49,
     'MARKERS_DEAD': 50,
     'MARKERS_ALLY': 51,
     'GUI_START_BEHAVIOR': 52,
     'FEEDBACK': 53,
     'EULA_VERSION': 54,
     'GAMEPLAY': 55,
     'FORT': 56,
     'USERS_STORAGE_REV': 57,
     'CONTACTS': 58,
     'GAME_EXTENDED': constants.USER_SERVER_SETTINGS.GAME_EXTENDED,
     'FALLOUT': 60,
     'TUTORIAL': 61,
     'AIM_ARCADE_4': 63,
     'AIM_SNIPER_4': 64,
     'MARKS_ON_GUN': constants.USER_SERVER_SETTINGS.HIDE_MARKS_ON_GUN,
     'ONCE_ONLY_HINTS': 70,
     'CAROUSEL_FILTER_1': 73,
     'CAROUSEL_FILTER_2': 74,
     'FALLOUT_CAROUSEL_FILTER_1': 75,
     'FALLOUT_CAROUSEL_FILTER_2': 76,
     'ENCYCLOPEDIA_RECOMMENDATIONS_1': 77,
     'ENCYCLOPEDIA_RECOMMENDATIONS_2': 78,
     'ENCYCLOPEDIA_RECOMMENDATIONS_3': 79}

    def __init__(self):
        self.__cache = dict()

    def _response(self, resID, value, callback):
        """
        Common server response method. Must be called ANYWAY after
        server operation will complete.
        
        @param resID: request result id
        @param value: requested value
        @param callback: function to be called after operation will complete
        """
        if resID < 0:
            LOG_ERROR('[class %s] There is error while getting data from cache: %s[%d]' % (self.__class__.__name__, code2str(resID), resID))
            return callback(dict())
        callback(value)

    @async
    def _requestCache(self, callback=None):
        """
        Request data from server
        """
        BigWorld.player().intUserSettings.getCache(lambda resID, value: self._response(resID, value, callback))

    @async
    @process
    def request(self, callback=None):
        """
        Public request method. Validate player entity to request
        possibility and itself as single callback argument.
        """
        self.__cache = yield self._requestCache()
        callback(self)

    def getCacheValue(self, key, defaultValue=None):
        """
        Public interface method to get value from cache.
        
        @param key: value's key in cache
        @param defaultValue: default value if key does not exist
        @return: value
        """
        return self.__cache.get(key, defaultValue)

    @process
    def setSetting(self, key, value):
        yield self._addIntSettings({self.SETTINGS[key]: int(value)})

    @process
    def setSettings(self, settings):
        intSettings = dict(map(lambda item: (self.SETTINGS[item[0]], int(item[1])), settings.iteritems()))
        yield self._addIntSettings(intSettings)

    def getSetting(self, key, defaultValue=None):
        return self.getCacheValue(self.SETTINGS[key], defaultValue)

    @async
    def _addIntSettings(self, settings, callback=None):
        import BattleReplay
        if not BattleReplay.g_replayCtrl.isPlaying:
            self.__cache.update(settings)
            BigWorld.player().intUserSettings.addIntSettings(settings, callback)

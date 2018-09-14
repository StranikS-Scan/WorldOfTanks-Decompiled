# Embedded file name: scripts/client/gui/shared/utils/requesters/IntSettingsRequester.py
import BigWorld
import constants
from adisp import async, process
from debug_utils import LOG_ERROR
from gui.shared.utils import code2str

class IntSettingsRequester(object):
    """
    Setting dictionary presenting int settings keys by section names
    """
    SETTINGS = {'VERSION': 0,
     'GAME': 1,
     'GRAPHICS': 2,
     'SOUND': 3,
     'CONTROLS': 4,
     'CMD_MOVE_FORWARD': 5,
     'CMD_MOVE_BACKWARD': 6,
     'CMD_ROTATE_LEFT': 7,
     'CMD_ROTATE_RIGHT': 8,
     'CMD_CM_VEHICLE_SWITCH_AUTOROTATION': 9,
     'CMD_INCREMENT_CRUISE_MODE': 10,
     'CMD_DECREMENT_CRUISE_MODE': 11,
     'CMD_STOP_UNTIL_FIRE': 12,
     'CMD_CM_SHOOT': 13,
     'CMD_CM_LOCK_TARGET': 14,
     'CMD_CM_LOCK_TARGET_OFF': 15,
     'CMD_CM_ALTERNATE_MODE': 16,
     'CMD_RELOAD_PARTIAL_CLIP': 17,
     'CMD_TOGGLE_GUI': 18,
     'CMD_RADIAL_MENU_SHOW': 19,
     'CMD_AMMO_CHOICE_1': 20,
     'CMD_AMMO_CHOICE_2': 21,
     'CMD_AMMO_CHOICE_3': 22,
     'CMD_AMMO_CHOICE_4': 23,
     'CMD_AMMO_CHOICE_5': 24,
     'CMD_AMMO_CHOICE_6': 25,
     'CMD_AMMO_CHOICE_7': 26,
     'CMD_AMMO_CHOICE_8': 27,
     'CMD_CHAT_SHORTCUT_ATTACK': 28,
     'CMD_CHAT_SHORTCUT_BACKTOBASE': 29,
     'CMD_CHAT_SHORTCUT_POSITIVE': 30,
     'CMD_CHAT_SHORTCUT_NEGATIVE': 31,
     'CMD_CHAT_SHORTCUT_HELPME': 32,
     'CMD_CHAT_SHORTCUT_RELOAD': 33,
     'CMD_CM_CAMERA_ROTATE_UP': 34,
     'CMD_CM_CAMERA_ROTATE_DOWN': 35,
     'CMD_CM_CAMERA_ROTATE_LEFT': 36,
     'CMD_CM_CAMERA_ROTATE_RIGHT': 37,
     'CMD_VOICECHAT_MUTE': 38,
     'CMD_LOGITECH_SWITCH_VIEW': 39,
     'CMD_MINIMAP_SIZE_UP': 40,
     'CMD_MINIMAP_SIZE_DOWN': 41,
     'CMD_MINIMAP_VISIBLE': 42,
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
     'CAROUSEL_FILTER': 53,
     'EULA_VERSION': 54,
     'GAMEPLAY': 55,
     'FORT': 56,
     'USERS_STORAGE_REV': 57,
     'CONTACTS': 58,
     'GAME_EXTENDED': constants.USER_SERVER_SETTINGS.GAME_EXTENDED,
     'FALLOUT': 60,
     'TUTORIAL': 61,
     'FALLOUT_CAROUSEL_FILTER': 62,
     'MARKS_ON_GUN': constants.USER_SERVER_SETTINGS.HIDE_MARKS_ON_GUN,
     'ONCE_ONLY_HINTS': 70}

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
    def _requestCache(self, callback = None):
        """
        Request data from server
        """
        BigWorld.player().intUserSettings.getCache(lambda resID, value: self._response(resID, value, callback))

    @async
    @process
    def request(self, callback = None):
        """
        Public request method. Validate player entity to request
        possibility and itself as single callback argument.
        """
        self.__cache = yield self._requestCache()
        callback(self)

    def getCacheValue(self, key, defaultValue = None):
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

    def getSetting(self, key, defaultValue = None):
        return self.getCacheValue(self.SETTINGS[key], defaultValue)

    @async
    def _addIntSettings(self, settings, callback = None):
        import BattleReplay
        if not BattleReplay.g_replayCtrl.isPlaying:
            BigWorld.player().intUserSettings.addIntSettings(settings, callback)

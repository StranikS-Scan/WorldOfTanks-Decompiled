# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Settings.py
# Compiled at: 2019-02-28 17:28:16
import BigWorld
g_instance = None
KEY_UPDATE_URL = 'updateUrl'
KEY_FAKE_MODEL = 'fakeModel'
KEY_CONTROL_MODE = 'controlMode'
KEY_LOGIN_INFO = 'loginInfo'
KEY_TOKEN2 = 'token2'
KEY_SCREEN_SIZE = 'screenSize'
KEY_VIDEO_MODE = 'videoMode'
KEY_LOBBY_TOOLTIP_DELAY = 'lobbyTooltipDelay'
KEY_SOUND_PREFERENCES = 'soundPrefs'
KEY_REPLAY_PREFERENCES = 'replayPrefs'
APPLICATION_CLOSE_DELAY = 'closeApplicationDelay'
KEY_MESSENGER_PREFERENCES = 'messengerPrefs'
KEY_ACCOUNT_SETTINGS = 'accounts'
KEY_SHOW_STARTUP_MOVIE = 'showStartupMovie'
KEY_SHOW_LANGUAGE_BAR_OLD = 'showLangugeBar'
KEY_SHOW_LANGUAGE_BAR = 'showLanguageBar'
KEY_ENABLE_VOIP = 'enableVoIP'
KEY_LOG_PARSER = 'logParser'
KEY_VIBRATION = 'vibration'
KEY_ENABLE_EDGE_DETECT_AA = 'enableEdgeDetectAA'
KEY_ENABLE_MORTEM_POST_EFFECT_OLD = 'enableMortemPostEffect'
KEY_ENABLE_MORTEM_POST_EFFECT = 'enablePostMortemEffect'

class Settings(object):

    def __init__(self, scriptConfig, engineConfig, userPrefs):
        self.scriptConfig = scriptConfig
        self.engineConfig = engineConfig
        self.userPrefs = userPrefs

    def save(self):
        BigWorld.savePreferences()

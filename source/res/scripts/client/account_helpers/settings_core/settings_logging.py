# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/settings_logging.py
import json
import hashlib
import logging
from helpers import dependency
from account_helpers.settings_core import ISettingsCore, settings_constants
from account_helpers import AccountSettings
from account_helpers.AccountSettings import DEFERRED_LOG_PLAYER_SETTINGS_ACTIONS
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.settings.loggers import SettingsLogger
from uilogging.settings.constants import SettingsLogActions
from wotdecorators import noexcept
from functools import wraps
_logger = logging.getLogger(__name__)
EXCLUDED_SETTINGS = [settings_constants.GAME.GAMEPLAY_ONLY_10_MODE,
 settings_constants.GAME.GAMEPLAY_NATIONS,
 settings_constants.GAME.GAMEPLAY_DEV_MAPS,
 settings_constants.GAME.GAMEPLAY_EPIC_DOMINATION,
 settings_constants.GAME.PLAYERS_PANELS_SHOW_TYPES,
 settings_constants.GAME.PLAYERS_PANELS_STATE,
 settings_constants.GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE,
 settings_constants.GAME.STORE_RECEIVER_IN_BATTLE,
 settings_constants.GAME.SNIPER_MODE_SWINGING_ENABLED,
 settings_constants.BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION,
 settings_constants.GRAPHICS.GAMMA_SETTING,
 settings_constants.GRAPHICS.COLOR_FILTER_IMAGES,
 settings_constants.GRAPHICS.COLOR_FILTER_SETTING,
 settings_constants.GRAPHICS.GRAPHICS_QUALITY_HD_SD,
 settings_constants.GRAPHICS.GRAPHICS_QUALITY_HD_SD_HIGH,
 settings_constants.GRAPHICS.IS_SD_QUALITY,
 settings_constants.GRAPHICS.TESSELLATION_SUPPORTED,
 settings_constants.GRAPHICS.NATIVE_RESOLUTION,
 settings_constants.GRAPHICS.GRAPHICS_SETTINGS_LIST,
 'DECOR_LEVEL',
 'HAVOK_QUALITY',
 'DEBUG_SHADER',
 settings_constants.SOUND.SOUND_QUALITY_VISIBLE,
 settings_constants.SOUND.VOIP_SUPPORTED,
 settings_constants.SOUND.NATIONS_VOICES,
 settings_constants.SOUND.GAME_EVENT_GUI,
 settings_constants.SOUND.GAME_EVENT_AMBIENT,
 settings_constants.SOUND.GAME_EVENT_VOICE,
 settings_constants.SOUND.GAME_EVENT_VEHICLES,
 settings_constants.SOUND.GAME_EVENT_MUSIC,
 settings_constants.SOUND.GAME_EVENT_EFFECTS,
 settings_constants.CONTROLS.KEYBOARD_IMPORTANT_BINDS,
 settings_constants.CONTROLS.KEYS_LAYOUT,
 settings_constants.CONTROLS.KEYS_TOOLTIPS]

def _getConfig():
    lobbyContext = dependency.instance(ILobbyContext)
    serverSettings = lobbyContext.getServerSettings()
    return None if serverSettings is None else serverSettings.settingsLoggingConfig


def _isEnabled():
    config = _getConfig()
    return config is not None and config.isEnabled


def _logChangesPerSession():
    config = _getConfig()
    return config is not None and config.logChangesPerSession


def _ifSettingsLoggingEnabled(result=None):

    def inner(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not _isEnabled():
                _logger.debug('Settings logging disabled.')
                return result
            return func(*args, **kwargs)

        return wrapper

    return inner


def _getHash(settings):
    keys = settings.keys()
    keys.sort()
    md5 = hashlib.md5()
    for key in keys:
        md5.update(key)

    return md5.hexdigest()


def _addDeferredLogPlayerSettingsAction(action):
    actions = AccountSettings.getSettings(DEFERRED_LOG_PLAYER_SETTINGS_ACTIONS)
    actions.add(action)
    AccountSettings.setSettings(DEFERRED_LOG_PLAYER_SETTINGS_ACTIONS, actions)


def _resetDeferredLogPlayerSettingsActions():
    defaultActions = AccountSettings.getSettingsDefault(DEFERRED_LOG_PLAYER_SETTINGS_ACTIONS)
    AccountSettings.setSettings(DEFERRED_LOG_PLAYER_SETTINGS_ACTIONS, defaultActions)


def _logPlayerSettings(action):
    connectionMgr = dependency.instance(IConnectionManager)
    settingsCore = dependency.instance(ISettingsCore)
    globalSettings, localSettings = settingsCore.getSettings(excludedNames=EXCLUDED_SETTINGS)
    SettingsLogger().log(action=action, sessionId=connectionMgr.lastSessionID, globalSettings=json.dumps(globalSettings), globalSettingsHash=_getHash(globalSettings), localSettings=json.dumps(localSettings), localSettingsHash=_getHash(localSettings))


@noexcept
@_ifSettingsLoggingEnabled()
def logPlayerSettingsOnDisconnect():
    actions = AccountSettings.getSettings(DEFERRED_LOG_PLAYER_SETTINGS_ACTIONS)
    if not actions:
        return
    if SettingsLogActions.SETTINGS_INITED in actions:
        _logPlayerSettings(SettingsLogActions.SETTINGS_INITED)
    elif SettingsLogActions.SETTINGS_CHANGED in actions:
        _logPlayerSettings(SettingsLogActions.SETTINGS_CHANGED)
    _resetDeferredLogPlayerSettingsActions()


@noexcept
@_ifSettingsLoggingEnabled()
def logPlayerSettingsBeforeChange():
    actions = AccountSettings.getSettings(DEFERRED_LOG_PLAYER_SETTINGS_ACTIONS)
    if SettingsLogActions.SETTINGS_INITED in actions and not _logChangesPerSession():
        _logPlayerSettings(SettingsLogActions.SETTINGS_INITED)
        _resetDeferredLogPlayerSettingsActions()


@noexcept
@_ifSettingsLoggingEnabled()
def logPlayerSettingsAfterChange():
    if _logChangesPerSession():
        _addDeferredLogPlayerSettingsAction(SettingsLogActions.SETTINGS_CHANGED)
    else:
        _logPlayerSettings(SettingsLogActions.SETTINGS_CHANGED)
        _resetDeferredLogPlayerSettingsActions()


@noexcept
def logPlayerSettingsOnMigration():
    _addDeferredLogPlayerSettingsAction(SettingsLogActions.SETTINGS_INITED)

# Embedded file name: scripts/client/account_helpers/settings_core/migrations.py
from account_helpers.settings_core.SettingsCache import g_settingsCache
import constants
import BigWorld
from account_helpers.settings_core.settings_constants import GAME, CONTROLS
from adisp import process, async
from debug_utils import LOG_DEBUG

def _initializeDefaultSettings(core, data, initialized):
    LOG_DEBUG('Initializing server settings.')
    from account_helpers.AccountSettings import AccountSettings
    gameData = data['gameData'] = {GAME.DATE_TIME_MESSAGE_INDEX: 2,
     GAME.ENABLE_OL_FILTER: core.getSetting(GAME.ENABLE_OL_FILTER),
     GAME.ENABLE_SPAM_FILTER: core.getSetting(GAME.ENABLE_SPAM_FILTER),
     GAME.INVITES_FROM_FRIENDS: core.getSetting(GAME.INVITES_FROM_FRIENDS),
     GAME.RECEIVE_FRIENDSHIP_REQUEST: core.getSetting(GAME.RECEIVE_FRIENDSHIP_REQUEST),
     GAME.STORE_RECEIVER_IN_BATTLE: core.getSetting(GAME.STORE_RECEIVER_IN_BATTLE),
     GAME.REPLAY_ENABLED: core.getSetting(GAME.REPLAY_ENABLED),
     GAME.ENABLE_SERVER_AIM: core.getSetting(GAME.ENABLE_SERVER_AIM),
     GAME.SHOW_VEHICLES_COUNTER: core.getSetting(GAME.SHOW_VEHICLES_COUNTER),
     GAME.MINIMAP_ALPHA: core.getSetting(GAME.MINIMAP_ALPHA),
     GAME.PLAYERS_PANELS_SHOW_LEVELS: core.getSetting(GAME.PLAYERS_PANELS_SHOW_LEVELS),
     GAME.ENABLE_POSTMORTEM: core.getSetting(GAME.ENABLE_POSTMORTEM)}
    gameplayData = data['gameplayData'] = {GAME.GAMEPLAY_MASK: AccountSettings.getSettingsDefault('gameplayMask')}
    aimData = data['aimData'] = {'arcade': core.getSetting('arcade'),
     'sniper': core.getSetting('sniper')}
    controlsData = data['controlsData'] = {CONTROLS.MOUSE_HORZ_INVERSION: core.getSetting(CONTROLS.MOUSE_HORZ_INVERSION),
     CONTROLS.MOUSE_VERT_INVERSION: core.getSetting(CONTROLS.MOUSE_VERT_INVERSION),
     CONTROLS.BACK_DRAFT_INVERSION: core.getSetting(CONTROLS.BACK_DRAFT_INVERSION)}
    from gui import game_control
    if game_control.g_instance.igr.getRoomType() == constants.IGR_TYPE.NONE:
        import Settings
        section = Settings.g_instance.userPrefs
        if section.has_key(Settings.KEY_MESSENGER_PREFERENCES):
            subSec = section[Settings.KEY_MESSENGER_PREFERENCES]
            tags = subSec.keys()
            _userProps = {GAME.DATE_TIME_MESSAGE_INDEX: 'readInt',
             GAME.ENABLE_OL_FILTER: 'readBool',
             GAME.ENABLE_SPAM_FILTER: 'readBool',
             GAME.INVITES_FROM_FRIENDS: 'readBool',
             GAME.RECEIVE_FRIENDSHIP_REQUEST: 'readBool',
             GAME.RECEIVE_INVITES_IN_BATTLE: 'readBool',
             GAME.STORE_RECEIVER_IN_BATTLE: 'readBool'}
            for key, reader in _userProps.iteritems():
                if key in tags:
                    gameData[key] = getattr(subSec, reader)(key)

        try:
            value = section['replayPrefs'].readBool('enabled', None)
            if value:
                gameData[GAME.REPLAY_ENABLED] = 2
            elif value is not None:
                gameData[GAME.REPLAY_ENABLED] = 0
        except:
            LOG_DEBUG('Replay preferences is not available.')

        gameData[GAME.ENABLE_SERVER_AIM] = AccountSettings.getSettings('useServerAim')
        gameData[GAME.SHOW_VEHICLES_COUNTER] = AccountSettings.getSettings('showVehiclesCounter')
        gameData[GAME.MINIMAP_ALPHA] = AccountSettings.getSettings('minimapAlpha')
        gameData[GAME.PLAYERS_PANELS_SHOW_LEVELS] = AccountSettings.getSettings('players_panel')['showLevels']
        gameplayData[GAME.GAMEPLAY_MASK] = AccountSettings.getSettings('gameplayMask')
        arcade = AccountSettings.getSettings('arcade')
        sniper = AccountSettings.getSettings('sniper')
        aimData['arcade'] = core.options.getSetting('arcade').fromAccountSettings(arcade)
        aimData['sniper'] = core.options.getSetting('sniper').fromAccountSettings(sniper)
        from post_processing import g_postProcessing
        gameData[GAME.ENABLE_POSTMORTEM] = g_postProcessing.getSetting('mortem_post_effect')
        if section.has_key(Settings.KEY_CONTROL_MODE):
            ds = section[Settings.KEY_CONTROL_MODE]
            try:
                controlsData[CONTROLS.MOUSE_HORZ_INVERSION] = ds['arcadeMode'].readBool('horzInvert', False)
                controlsData[CONTROLS.MOUSE_VERT_INVERSION] = ds['arcadeMode'].readBool('vertInvert', False)
                controlsData[CONTROLS.MOUSE_VERT_INVERSION] = ds['arcadeMode'].readBool('backDraftInvert', False)
            except:
                LOG_DEBUG('Controls preferences is not available.')

    data['markersData'] = AccountSettings.getSettings('markers')
    data['keyboardData'] = core.options.getSetting('keyboard').getCurrentMapping()
    data['graphicsData'] = {GAME.LENS_EFFECT: core.getSetting(GAME.LENS_EFFECT)}
    data['marksOnGun'] = {GAME.SHOW_MARKS_ON_GUN: core.getSetting(GAME.SHOW_MARKS_ON_GUN)}
    return


@async
@process
def _reinitializeDefaultSettings(core, data, initialized, callback = None):

    @async
    def wrapper(callback = None):
        BigWorld.player().intUserSettings.delIntSettings(range(1, 60), callback)

    yield wrapper()
    _initializeDefaultSettings(core, data, initialized)
    callback(data)
    return


def _migrateTo3(core, data, initialized):
    aimData = data['aimData']
    if not initialized:
        data['aimData'].update({'arcade': core.getSetting('arcade'),
         'sniper': core.getSetting('sniper')})
    aimData['arcade']['reloaderTimer'] = 100
    aimData['sniper']['reloaderTimer'] = 100
    if not initialized:
        data['gameData']['horStabilizationSnp'] = core.getSetting('dynamicCamera')


def _migrateTo4(core, data, initialized):
    gameData = data['gameData']
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = g_settingsCache.getSectionSettings(SETTINGS_SECTIONS.GAME, 0)
    if storedValue & 128:
        gameData[GAME.REPLAY_ENABLED] = 2
    else:
        gameData[GAME.REPLAY_ENABLED] = 0


def _migrateTo5(core, data, initialized):
    data['gameData'][GAME.ENABLE_POSTMORTEM_DELAY] = True


def _migrateTo6(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = g_settingsCache.getSectionSettings(SETTINGS_SECTIONS.GAME, 0)
    maskOffset = 7168
    currentMask = (storedValue & maskOffset) >> 10
    import ArenaType
    newMask = currentMask | ArenaType.getVisibilityMask(ArenaType.getGameplayIDForName('nations'))
    data['gameplayData'][GAME.GAMEPLAY_MASK] = newMask
    clear = data['clear']
    clear[SETTINGS_SECTIONS.GAME] = clear.get(SETTINGS_SECTIONS.GAME, 0) | maskOffset


def _migrateTo7(core, data, initialized):
    BigWorld.setTripleBuffering(True)


def _migrateTo8(core, data, initialized):
    data['graphicsData'][GAME.LENS_EFFECT] = True


def _migrateTo9(core, data, initialized):
    data['marksOnGun'][GAME.SHOW_MARKS_ON_GUN] = False


def _migrateTo11(core, data, initialized):
    data['marksOnGun'][GAME.SHOW_MARKS_ON_GUN] = False


def _migrateTo12(core, data, initialized):
    data['gameData'][GAME.SHOW_VECTOR_ON_MAP] = True
    data['gameData'][GAME.SHOW_SECTOR_ON_MAP] = True


def _migrateTo13(core, data, initialized):
    data['gameData'][GAME.RECEIVE_FRIENDSHIP_REQUEST] = True


def _migrateTo14(core, data, initialized):
    data['gameExtData'][GAME.RECEIVE_INVITES_IN_BATTLE] = True


def _migrateTo15(core, data, initialized):
    data['gameExtData'][GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS] = True


def _migrateTo16(core, data, initialized):
    data['gameExtData'][GAME.RECEIVE_INVITES_IN_BATTLE] = True


def _migrateTo17(core, data, initialized):
    data['gameExtData'][GAME.RECEIVE_CLAN_INVITES_NOTIFICATIONS] = True


_versions = ((1,
  _initializeDefaultSettings,
  True,
  False),
 (2,
  _reinitializeDefaultSettings,
  True,
  True),
 (3,
  _migrateTo3,
  False,
  False),
 (4,
  _migrateTo4,
  True,
  False),
 (5,
  _migrateTo5,
  False,
  False),
 (6,
  _migrateTo6,
  True,
  False),
 (7,
  _migrateTo7,
  False,
  False),
 (8,
  _migrateTo8,
  True,
  False),
 (9,
  _migrateTo9,
  True,
  False),
 (11,
  _migrateTo11,
  True,
  False),
 (12,
  _migrateTo12,
  False,
  False),
 (13,
  _migrateTo13,
  False,
  False),
 (14,
  _migrateTo14,
  False,
  False),
 (15,
  _migrateTo15,
  False,
  False),
 (16,
  _migrateTo16,
  False,
  False),
 (17,
  _migrateTo17,
  False,
  False))

@async
@process
def migrateToVersion(fromVersion, core, data, callback = None):
    yield lambda callback: callback(None)
    initialized = False
    for version, migration, isInitialize, isAsync in _versions:
        if fromVersion < version and (not isInitialize or not initialized):
            if isAsync:
                yield migration(core, data, initialized)
            else:
                migration(core, data, initialized)
            LOG_DEBUG('Migrated to version: ', version, data)
            if isInitialize:
                initialized = True

    callback(data)

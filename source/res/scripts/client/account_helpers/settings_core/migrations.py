# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/migrations.py
import BigWorld
import constants
from account_helpers.settings_core.settings_constants import GAME, CONTROLS, VERSION, DAMAGE_INDICATOR, DAMAGE_LOG, BATTLE_EVENTS
from adisp import process, async
from debug_utils import LOG_DEBUG
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCache
from skeletons.gui.game_control import IIGRController

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
    igrCtrl = dependency.instance(IIGRController)
    if igrCtrl.getRoomType() == constants.IGR_TYPE.NONE:
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
    data['graphicsData'] = {GAME.LENS_EFFECT: core.getSetting(GAME.LENS_EFFECT)}
    data['marksOnGun'] = {GAME.SHOW_MARKS_ON_GUN: core.getSetting(GAME.SHOW_MARKS_ON_GUN)}
    return


@async
@process
def _reinitializeDefaultSettings(core, data, initialized, callback=None):

    @async
    def wrapper(callback=None):
        BigWorld.player().intUserSettings.delIntSettings(range(1, 60), callback)

    yield wrapper()
    _initializeDefaultSettings(core, data, initialized)
    callback(data)
    return


def _getSettingsCache():
    return dependency.instance(ISettingsCache)


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
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME, 0)
    if storedValue & 128:
        gameData[GAME.REPLAY_ENABLED] = 2
    else:
        gameData[GAME.REPLAY_ENABLED] = 0


def _migrateTo5(core, data, initialized):
    data['gameData'][GAME.ENABLE_POSTMORTEM_DELAY] = True


def _migrateTo6(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME, 0)
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
    pass


def _migrateTo16(core, data, initialized):
    data['gameExtData'][GAME.RECEIVE_INVITES_IN_BATTLE] = True


def _migrateTo17(core, data, initialized):
    data['gameExtData'][GAME.RECEIVE_CLAN_INVITES_NOTIFICATIONS] = True


def _migrateTo18(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from constants import QUEUE_TYPE
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.FALLOUT, 0)
    currentType = storedValue & 3
    if currentType > 0:
        oldTypeToNewType = {1: QUEUE_TYPE.FALLOUT_CLASSIC,
         2: QUEUE_TYPE.FALLOUT_MULTITEAM}
        newType = oldTypeToNewType.get(currentType, QUEUE_TYPE.UNKNOWN)
        data['fallout']['falloutBattleType'] = newType


def _migrateTo19(core, data, initialized):
    data['gameExtData'][GAME.MINIMAP_DRAW_RANGE] = True
    data['gameExtData'][GAME.MINIMAP_MAX_VIEW_RANGE] = True
    data['gameExtData'][GAME.MINIMAP_VIEW_RANGE] = True


def _migrateTo20(core, data, initialized):
    data['gameData'][GAME.STORE_RECEIVER_IN_BATTLE] = True


def _migrateTo21(core, data, initialized):
    aimData = data['aimData']
    for settingName in ('arcade', 'sniper'):
        if settingName not in aimData:
            data['aimData'].update({settingName: core.getSetting(settingName)})

    aimData['arcade']['zoomIndicator'] = 100
    aimData['sniper']['zoomIndicator'] = 100


def _migrateTo22(core, data, initialized):
    data['gameExtData'][GAME.SIMPLIFIED_TTC] = True


def _migrateTo23(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME, 0)
    settingOffset = 1610612736
    currentValue = (storedValue & settingOffset) >> 29
    if currentValue == 0:
        data['gameData'][GAME.SHOW_VEH_MODELS_ON_MAP] = 2


def _migrateTo24(core, data, initialized):
    pass


def _migrateTo25(core, data, initialized):
    data['carousel_filter']['hideEvent'] = False


def _migrateTo26(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, 0)
    maskOffset = 1
    if (storedValue & maskOffset) >> 0:
        clear = data['clear']
        clear[SETTINGS_SECTIONS.GAME_EXTENDED] = clear.get(SETTINGS_SECTIONS.GAME_EXTENDED, 0) | maskOffset
    feedbackData = data.get('feedbackData', {})
    feedbackData[DAMAGE_INDICATOR.TYPE] = 1
    feedbackData[DAMAGE_INDICATOR.PRESETS] = 0
    feedbackData[DAMAGE_INDICATOR.DAMAGE_VALUE] = True
    feedbackData[DAMAGE_INDICATOR.VEHICLE_INFO] = True
    feedbackData[DAMAGE_INDICATOR.ANIMATION] = True
    feedbackData[DAMAGE_LOG.TOTAL_DAMAGE] = True
    feedbackData[DAMAGE_LOG.BLOCKED_DAMAGE] = True
    feedbackData[DAMAGE_LOG.ASSIST_DAMAGE] = True
    feedbackData[DAMAGE_LOG.SHOW_DETAILS] = 2
    for key in BATTLE_EVENTS.ALL():
        feedbackData[key] = True

    data['feedbackData'] = feedbackData


def _migrateTo27(core, data, initialized):
    data['carousel_filter']['hideEvent'] = False


def _migrateTo28(core, data, initialized):
    data['gameExtData'][GAME.CAROUSEL_TYPE] = 1


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
  False),
 (18,
  _migrateTo18,
  False,
  False),
 (19,
  _migrateTo19,
  False,
  False),
 (20,
  _migrateTo20,
  False,
  False),
 (21,
  _migrateTo21,
  False,
  False),
 (22,
  _migrateTo22,
  False,
  False),
 (23,
  _migrateTo23,
  False,
  False),
 (24,
  _migrateTo24,
  False,
  False),
 (25,
  _migrateTo25,
  False,
  False),
 (26,
  _migrateTo26,
  False,
  False),
 (27,
  _migrateTo27,
  False,
  False),
 (28,
  _migrateTo28,
  False,
  False))

@async
@process
def migrateToVersion(fromVersion, core, data, callback=None):
    yield lambda callback: callback(None)
    initialized = False
    for version, migration, isInitialize, isAsync in _versions:
        if fromVersion < version:
            if not isInitialize or not initialized:
                if isAsync:
                    yield migration(core, data, initialized)
                else:
                    migration(core, data, initialized)
                if isInitialize:
                    initialized = True
            data[VERSION] = version
            LOG_DEBUG('Migrated to version: ', version, data)

    callback(data)

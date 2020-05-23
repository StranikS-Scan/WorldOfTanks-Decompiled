# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/migrations.py
import BigWorld
import constants
from account_helpers.settings_core.settings_constants import GAME, CONTROLS, VERSION, DAMAGE_INDICATOR, DAMAGE_LOG, BATTLE_EVENTS, SESSION_STATS
from adisp import process, async
from debug_utils import LOG_DEBUG
from gui.server_events.pm_constants import PM_TUTOR_FIELDS
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCache
from skeletons.gui.game_control import IIGRController

def _initializeDefaultSettings(core, data, initialized):
    LOG_DEBUG('Initializing server settings.')
    from account_helpers.counter_settings import dropCounters as dropNewSettingsCounters
    from account_helpers.AccountSettings import AccountSettings
    options = core.options
    gameData = data['gameData'] = {GAME.DATE_TIME_MESSAGE_INDEX: 2,
     GAME.ENABLE_OL_FILTER: options.getSetting(GAME.ENABLE_OL_FILTER).getDefaultValue(),
     GAME.ENABLE_SPAM_FILTER: options.getSetting(GAME.ENABLE_SPAM_FILTER).getDefaultValue(),
     GAME.INVITES_FROM_FRIENDS: options.getSetting(GAME.INVITES_FROM_FRIENDS).getDefaultValue(),
     GAME.RECEIVE_FRIENDSHIP_REQUEST: core.options.getSetting(GAME.RECEIVE_FRIENDSHIP_REQUEST).getDefaultValue(),
     GAME.STORE_RECEIVER_IN_BATTLE: core.options.getSetting(GAME.STORE_RECEIVER_IN_BATTLE).getDefaultValue(),
     GAME.REPLAY_ENABLED: core.getSetting(GAME.REPLAY_ENABLED),
     GAME.ENABLE_SERVER_AIM: core.getSetting(GAME.ENABLE_SERVER_AIM),
     GAME.SHOW_DAMAGE_ICON: core.getSetting(GAME.SHOW_DAMAGE_ICON),
     GAME.SHOW_VEHICLES_COUNTER: core.getSetting(GAME.SHOW_VEHICLES_COUNTER),
     GAME.MINIMAP_ALPHA: core.getSetting(GAME.MINIMAP_ALPHA),
     GAME.PLAYERS_PANELS_SHOW_LEVELS: core.getSetting(GAME.PLAYERS_PANELS_SHOW_LEVELS)}
    data['gameExtData'][GAME.CHAT_CONTACTS_LIST_ONLY] = options.getSetting(GAME.CHAT_CONTACTS_LIST_ONLY).getDefaultValue()
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
             GAME.STORE_RECEIVER_IN_BATTLE: 'readBool',
             GAME.CHAT_CONTACTS_LIST_ONLY: 'readBool'}
            for key, reader in _userProps.iteritems():
                if key in tags:
                    gameData[key] = getattr(subSec, reader)(key)

        try:
            value = section['replayPrefs'].readBool('enabled', None)
            if value:
                gameData[GAME.REPLAY_ENABLED] = 2
            elif value is not None:
                gameData[GAME.REPLAY_ENABLED] = 0
        except Exception:
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
        if section.has_key(Settings.KEY_CONTROL_MODE):
            ds = section[Settings.KEY_CONTROL_MODE]
            try:
                controlsData[CONTROLS.MOUSE_HORZ_INVERSION] = ds['arcadeMode'].readBool('horzInvert', False)
                controlsData[CONTROLS.MOUSE_VERT_INVERSION] = ds['arcadeMode'].readBool('vertInvert', False)
                controlsData[CONTROLS.MOUSE_VERT_INVERSION] = ds['arcadeMode'].readBool('backDraftInvert', False)
            except Exception:
                LOG_DEBUG('Controls preferences is not available.')

    data['markersData'] = AccountSettings.getSettings('markers')
    data['graphicsData'] = {GAME.LENS_EFFECT: core.getSetting(GAME.LENS_EFFECT)}
    data['marksOnGun'] = {GAME.SHOW_MARKS_ON_GUN: core.getSetting(GAME.SHOW_MARKS_ON_GUN)}
    dropNewSettingsCounters()
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
    pass


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
    data['carousel_filter']['event'] = False


def _migrateTo26(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, 0)
    maskOffset = 1
    if (storedValue & maskOffset) >> 0:
        clear = data['clear']
        clear[SETTINGS_SECTIONS.GAME_EXTENDED] = clear.get(SETTINGS_SECTIONS.GAME_EXTENDED, 0) | maskOffset
    feedbackData = data.get('feedbackData', {})
    feedbackData[DAMAGE_INDICATOR.TYPE] = 1
    feedbackData[DAMAGE_INDICATOR.PRESET_CRITS] = 0
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
    data['carousel_filter']['event'] = False


def _migrateTo28(core, data, initialized):
    data['gameExtData'][GAME.CAROUSEL_TYPE] = 1


def _migrateTo29(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, 0)
    settingOffset = 8
    if storedValue & settingOffset:
        data['onceOnlyHints']['ShopTradeInHint'] = 1
        clear = data['clear']
        clear['onceOnlyHints'] = clear.get('onceOnlyHints', 0) | settingOffset
    else:
        data['onceOnlyHints']['ShopTradeInHint'] = 0


def _migrateTo30(core, data, initialized):
    feedbackData = data.get('feedbackData', {})
    feedbackData[BATTLE_EVENTS.ENEMY_WORLD_COLLISION] = True
    feedbackData[DAMAGE_INDICATOR.DYNAMIC_INDICATOR] = True
    data['feedbackData'] = feedbackData


def _migrateTo31(core, data, initialized):
    feedbackData = data.get('feedbackData', {})
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    currentVal = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.FEEDBACK, 0)
    maskOffset = 33554432
    if not currentVal & maskOffset:
        feedbackData[DAMAGE_INDICATOR.DYNAMIC_INDICATOR] = False
    feedbackData[BATTLE_EVENTS.RECEIVED_DAMAGE] = True
    feedbackData[BATTLE_EVENTS.RECEIVED_CRITS] = True
    feedbackData[DAMAGE_LOG.SHOW_EVENT_TYPES] = 0
    feedbackData[DAMAGE_LOG.EVENT_POSITIONS] = 0


def _migrateTo32(core, data, initialized):
    data['carousel_filter']['rented'] = True
    data['carousel_filter']['event'] = True


def _migrateTo33(core, data, initialized):
    data['gameExtData'][GAME.VEHICLE_CAROUSEL_STATS] = True


def _migrateTo34(core, data, initialized):
    if constants.IS_CHINA:
        data['gameExtData'][GAME.CHAT_CONTACTS_LIST_ONLY] = True


def _migrateTo35(core, data, initialized):
    feedbackDamageIndicator = data.get('feedbackDamageIndicator', {})
    feedbackDamageLog = data.get('feedbackDamageLog', {})
    feedbackBattleEvents = data.get('feedbackBattleEvents', {})
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    currentVal = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.FEEDBACK, 0)
    feedbackDamageIndicator[DAMAGE_INDICATOR.TYPE] = __migrateMaskValue(currentVal, 1, 0)
    feedbackDamageIndicator[DAMAGE_INDICATOR.PRESET_CRITS] = __migrateMaskValue(currentVal, 1, 1)
    feedbackDamageIndicator[DAMAGE_INDICATOR.DAMAGE_VALUE] = __migrateMaskValue(currentVal, 1, 2)
    feedbackDamageIndicator[DAMAGE_INDICATOR.VEHICLE_INFO] = __migrateMaskValue(currentVal, 1, 3)
    feedbackDamageIndicator[DAMAGE_INDICATOR.ANIMATION] = __migrateMaskValue(currentVal, 1, 4)
    feedbackDamageIndicator[DAMAGE_INDICATOR.DYNAMIC_INDICATOR] = __migrateMaskValue(currentVal, 1, 25)
    feedbackDamageLog[DAMAGE_LOG.TOTAL_DAMAGE] = __migrateMaskValue(currentVal, 1, 5)
    feedbackDamageLog[DAMAGE_LOG.BLOCKED_DAMAGE] = __migrateMaskValue(currentVal, 1, 6)
    feedbackDamageLog[DAMAGE_LOG.ASSIST_DAMAGE] = __migrateMaskValue(currentVal, 1, 7)
    feedbackDamageLog[DAMAGE_LOG.ASSIST_STUN] = False
    feedbackDamageLog[DAMAGE_LOG.SHOW_DETAILS] = __migrateMaskValue(currentVal, 3, 8)
    feedbackDamageLog[DAMAGE_LOG.SHOW_EVENT_TYPES] = __migrateMaskValue(currentVal, 3, 28)
    feedbackDamageLog[DAMAGE_LOG.EVENT_POSITIONS] = __migrateMaskValue(currentVal, 3, 30)
    feedbackBattleEvents[BATTLE_EVENTS.SHOW_IN_BATTLE] = __migrateMaskValue(currentVal, 1, 10)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_HP_DAMAGE] = __migrateMaskValue(currentVal, 1, 11)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_BURNING] = __migrateMaskValue(currentVal, 1, 12)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_RAM_ATTACK] = __migrateMaskValue(currentVal, 1, 13)
    feedbackBattleEvents[BATTLE_EVENTS.BLOCKED_DAMAGE] = __migrateMaskValue(currentVal, 1, 14)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_DETECTION_DAMAGE] = __migrateMaskValue(currentVal, 1, 15)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_TRACK_DAMAGE] = __migrateMaskValue(currentVal, 1, 16)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_DETECTION] = __migrateMaskValue(currentVal, 1, 17)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_KILL] = __migrateMaskValue(currentVal, 1, 18)
    feedbackBattleEvents[BATTLE_EVENTS.BASE_CAPTURE_DROP] = __migrateMaskValue(currentVal, 1, 19)
    feedbackBattleEvents[BATTLE_EVENTS.BASE_CAPTURE] = __migrateMaskValue(currentVal, 1, 20)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_CRITICAL_HIT] = __migrateMaskValue(currentVal, 1, 21)
    feedbackBattleEvents[BATTLE_EVENTS.EVENT_NAME] = __migrateMaskValue(currentVal, 1, 22)
    feedbackBattleEvents[BATTLE_EVENTS.VEHICLE_INFO] = __migrateMaskValue(currentVal, 1, 23)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_WORLD_COLLISION] = __migrateMaskValue(currentVal, 1, 24)
    feedbackBattleEvents[BATTLE_EVENTS.RECEIVED_DAMAGE] = __migrateMaskValue(currentVal, 1, 26)
    feedbackBattleEvents[BATTLE_EVENTS.RECEIVED_CRITS] = __migrateMaskValue(currentVal, 1, 27)
    feedbackBattleEvents[BATTLE_EVENTS.ENEMY_ASSIST_STUN] = False


def __migrateMaskValue(currentVal, mask, offset):
    return currentVal >> offset & mask


def _migrateTo36(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from account_helpers.AccountSettings import AccountSettings
    default = AccountSettings.getSettingsDefault(GAME.GAMEPLAY_MASK)
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAMEPLAY, default)
    currentMask = storedValue & 65535
    import ArenaType
    newMask = currentMask | ArenaType.getVisibilityMask(ArenaType.getGameplayIDForName('ctf30x30'))
    newnewMask = newMask | ArenaType.getVisibilityMask(ArenaType.getGameplayIDForName('domination30x30'))
    data['gameplayData'][GAME.GAMEPLAY_MASK] = newnewMask


def _migrateTo37(core, data, initialized):
    data['delete'].extend((75, 76))


def _migrateTo38(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from account_helpers.AccountSettings import AccountSettings
    default = AccountSettings.getSettingsDefault(GAME.GAMEPLAY_MASK)
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAMEPLAY, default)
    currentGameplayMask = storedValue & 65535
    import ArenaType
    epicCtfEnabled = bool(currentGameplayMask & 1 << ArenaType.getGameplayIDForName('ctf30x30'))
    dominationEnabled = bool(currentGameplayMask & 1 << ArenaType.getGameplayIDForName('domination'))
    if not epicCtfEnabled or not dominationEnabled:
        currentGameplayMask &= ~ArenaType.getVisibilityMask(ArenaType.getGameplayIDForName('domination30x30'))
    data['gameplayData'][GAME.GAMEPLAY_MASK] = currentGameplayMask
    data['gameData'][GAME.MINIMAP_ALPHA] = 0
    data['gameExtData'][GAME.MINIMAP_ALPHA_ENABLED] = False


def _migrateTo39(core, data, initialized):
    data['gameExtData'][GAME.C11N_HISTORICALLY_ACCURATE] = True


def _migrateTo40(core, data, initialized):
    data['gameExtData'][GAME.HANGAR_CAM_PERIOD] = 0
    data['gameExtData'][GAME.HANGAR_CAM_PARALLAX_ENABLED] = True


def _migrateTo41(core, data, initialized):
    data['gameData'][GAME.SHOW_DAMAGE_ICON] = True


def _migrateTo42(core, data, initialized):
    data['uiStorage'][PM_TUTOR_FIELDS.GREETING_SCREEN_SHOWN] = False


def _migrateTo43(core, data, initialized):
    data['delete'].extend((91,))


def _migrateTo44(core, data, initialized):
    data['guiStartBehavior']['isRankedWelcomeViewShowed'] = False


def _migrateTo45(core, data, initialized):
    data['onceOnlyHints']['AccountButtonHint'] = True


def _migrateTo46(core, data, initialized):
    data['gameExtData'][GAME.ENABLE_SPEEDOMETER] = True


def _migrateTo47(core, data, initialized):
    data['delete'].extend((92,))
    data['delete'].extend((93,))


def _migrateTo48(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, 0)
    clear = data['clear']
    for bitPosition in range(22, 25):
        settingOffset = 1 << bitPosition
        if storedValue & settingOffset:
            clear['onceOnlyHints'] = clear.get('onceOnlyHints', 0) | settingOffset


def _migrateTo49(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    data['delete'].extend((91, 92, 93, 94, 95))
    clear = data['clear']
    newYearFilter = 256
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.CAROUSEL_FILTER_2, 0)
    if storedValue & newYearFilter:
        clear['carousel_filter'] = clear.get('carousel_filter', 0) | newYearFilter
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.EPICBATTLE_CAROUSEL_FILTER_2, 0)
    if storedValue & newYearFilter:
        clear['epicCarouselFilter2'] = clear.get('epicCarouselFilter2', 0) | newYearFilter


def _migrateTo50(core, data, initialized):
    data['sessionStats'][SESSION_STATS.SHOW_WTR] = True
    data['sessionStats'][SESSION_STATS.SHOW_RATIO_DAMAGE] = True
    data['sessionStats'][SESSION_STATS.SHOW_RATIO_KILL] = True
    data['sessionStats'][SESSION_STATS.SHOW_WINS] = True
    data['sessionStats'][SESSION_STATS.SHOW_AVERAGE_DAMAGE] = True
    data['sessionStats'][SESSION_STATS.SHOW_HELP_DAMAGE] = True
    data['sessionStats'][SESSION_STATS.SHOW_BLOCKED_DAMAGE] = True
    data['sessionStats'][SESSION_STATS.SHOW_AVERAGE_XP] = True


def _migrateTo51(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    currentVal = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.DAMAGE_INDICATOR, 0)
    feedbackDamageIndicator = data.get('feedbackDamageIndicator', {})
    feedbackDamageIndicator[DAMAGE_INDICATOR.PRESET_CRITS] = not __migrateMaskValue(currentVal, 1, 1)
    feedbackDamageIndicator[DAMAGE_INDICATOR.PRESET_ALLIES] = True


def _migrateTo52(core, data, initialized):
    data['onceOnlyHints']['CrewOperationBtnHint'] = True
    data['onceOnlyHints']['SoundButtonExHint'] = True


def _migrateTo53(core, data, initialized):
    data['gameExtData'][GAME.DISABLE_EVENT_HORN] = False


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
  False),
 (29,
  _migrateTo29,
  False,
  False),
 (30,
  _migrateTo30,
  False,
  False),
 (31,
  _migrateTo31,
  False,
  False),
 (32,
  _migrateTo32,
  False,
  False),
 (33,
  _migrateTo33,
  False,
  False),
 (34,
  _migrateTo34,
  False,
  False),
 (35,
  _migrateTo35,
  False,
  False),
 (36,
  _migrateTo36,
  True,
  False),
 (37,
  _migrateTo37,
  False,
  False),
 (38,
  _migrateTo38,
  False,
  False),
 (39,
  _migrateTo39,
  False,
  False),
 (40,
  _migrateTo40,
  False,
  False),
 (41,
  _migrateTo41,
  False,
  False),
 (42,
  _migrateTo42,
  False,
  False),
 (43,
  _migrateTo43,
  False,
  False),
 (44,
  _migrateTo44,
  False,
  False),
 (45,
  _migrateTo45,
  False,
  False),
 (46,
  _migrateTo46,
  False,
  False),
 (47,
  _migrateTo47,
  False,
  False),
 (48,
  _migrateTo48,
  False,
  False),
 (49,
  _migrateTo49,
  False,
  False),
 (50,
  _migrateTo50,
  False,
  False),
 (51,
  _migrateTo51,
  False,
  False),
 (52,
  _migrateTo52,
  False,
  False),
 (53,
  _migrateTo53,
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

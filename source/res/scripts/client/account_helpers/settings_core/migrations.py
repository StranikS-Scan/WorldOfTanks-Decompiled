# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/migrations.py
import BigWorld
import constants
from account_helpers.AccountSettings import NEW_SETTINGS_COUNTER
from account_helpers.settings_core.settings_constants import GAME, CONTROLS, VERSION, DAMAGE_INDICATOR, DAMAGE_LOG, BATTLE_EVENTS, SESSION_STATS, BattlePassStorageKeys, BattleCommStorageKeys, OnceOnlyHints, ScorePanelStorageKeys, SPGAim, GuiSettingsBehavior
from adisp import adisp_process, adisp_async
from debug_utils import LOG_DEBUG
from gui.server_events.pm_constants import PM_TUTOR_FIELDS
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCache
from skeletons.gui.game_control import IIGRController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

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
    data['gameExtData'] = {GAME.CHAT_CONTACTS_LIST_ONLY: options.getSetting(GAME.CHAT_CONTACTS_LIST_ONLY).getDefaultValue(),
     GAME.SNIPER_ZOOM: core.getSetting(GAME.SNIPER_ZOOM),
     GAME.HULLLOCK_ENABLED: core.getSetting(GAME.HULLLOCK_ENABLED),
     GAME.PRE_COMMANDER_CAM: core.getSetting(GAME.PRE_COMMANDER_CAM),
     GAME.COMMANDER_CAM: core.getSetting(GAME.COMMANDER_CAM)}
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


@adisp_async
@adisp_process
def _reinitializeDefaultSettings(core, data, initialized, callback=None):

    @adisp_async
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
    data['gameData'][GAME.POSTMORTEM_MODE] = True


def _migrateTo6(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME, 0)
    maskOffset = 7168
    currentMask = (storedValue & maskOffset) >> 10
    import ArenaType
    newMask = currentMask | ArenaType.getGameplaysMask(('nations',))
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
    newMask = currentMask | ArenaType.getGameplaysMask(('ctf30x30',))
    newnewMask = newMask | ArenaType.getGameplaysMask(('domination30x30',))
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
    epicCtfEnabled = bool(currentGameplayMask & ArenaType.getGameplaysMask(('ctf30x30',)))
    dominationEnabled = bool(currentGameplayMask & ArenaType.getGameplaysMask(('domination',)))
    if not epicCtfEnabled or not dominationEnabled:
        currentGameplayMask &= ~ArenaType.getGameplaysMask(('domination30x30',))
    data['gameplayData'][GAME.GAMEPLAY_MASK] = currentGameplayMask
    data['gameData'][GAME.MINIMAP_ALPHA] = 0
    data['gameExtData'][GAME.MINIMAP_ALPHA_ENABLED] = False


def _migrateTo39(core, data, initialized):
    data['gameExtData2'][GAME.CUSTOMIZATION_DISPLAY_TYPE] = 0


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
    pass


def _migrateTo54(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, 0)
    settingOffset = 50331648
    if storedValue & settingOffset:
        clear = data['clear']
        clear[SETTINGS_SECTIONS.GAME_EXTENDED] = clear.get(SETTINGS_SECTIONS.GAME_EXTENDED, 0) | settingOffset


def _migrateTo55(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, 0)
    settingOffset = 2
    if storedValue & settingOffset:
        clear = data['clear']
        clear['onceOnlyHints'] = clear.get('onceOnlyHints', 0) | settingOffset


def _migrateTo56(core, data, initialized):
    data['battlePassStorage'][BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN] = False
    data['battlePassStorage'][BattlePassStorageKeys.INTRO_VIDEO_SHOWN] = False


def _migrateTo57(core, data, initialized):
    data['guiStartBehavior']['isRankedWelcomeViewShowed'] = False


def _migrateTo58(core, data, initialized):
    gameData = data['battleComm']
    gameData[BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION] = True
    gameData[BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST] = True
    gameData[BattleCommStorageKeys.SHOW_STICKY_MARKERS] = True
    gameData[BattleCommStorageKeys.SHOW_CALLOUT_MESSAGES] = True
    gameData[BattleCommStorageKeys.SHOW_BASE_MARKERS] = True


def _migrateTo59(core, data, initialized):
    dtData = data['dogTags']
    dtData[GAME.SHOW_DOGTAG_TO_KILLER] = True
    dtData[GAME.SHOW_VICTIMS_DOGTAG] = True


def _migrateTo60(core, data, initialized):
    gameData = data['battleComm']
    isIBCEnabled = bool(core.getSetting(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION))
    if not isIBCEnabled:
        gameData[BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION] = True
        gameData[BattleCommStorageKeys.SHOW_LOCATION_MARKERS] = False
    else:
        gameData[BattleCommStorageKeys.SHOW_LOCATION_MARKERS] = True


def _migrateTo61(core, data, initialized):
    data['gameExtData'][GAME.DISPLAY_PLATOON_MEMBERS] = True


def _migrateTo62(core, data, initialized):
    data['onceOnlyHints2'][OnceOnlyHints.PLATOON_BTN_HINT] = initialized


def _migrateTo63(core, data, initialized):
    gameData = data['gameExtData']
    gameData[GAME.MINIMAP_MIN_SPOTTING_RANGE] = False
    gameData[GAME.ENABLE_REPAIR_TIMER] = True


def _migrateTo64(core, data, initialized):
    gameData = data['gameExtData']
    gameData[GAME.ENABLE_BATTLE_NOTIFIER] = True


def _migrateTo65(core, data, initialized):
    battlehudData = data['battleHud']
    battlehudData[ScorePanelStorageKeys.SHOW_HP_BAR] = True


def _migrateTo66(core, data, initialized):
    data['battlePassStorage'][BattlePassStorageKeys.DAILY_QUESTS_INTRO_SHOWN] = False


def _migrateTo67(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.BATTLE_PASS_STORAGE, 0)
    clear = data['clear']
    for position in range(2, 16) + range(18, 20):
        settingOffset = 1 << position
        if storedValue & settingOffset:
            clear['battlePassStorage'] = clear.get('battlePassStorage', 0) | settingOffset


def _migrateTo68(core, data, initialized):
    data['battlePassStorage'][BattlePassStorageKeys.INTRO_SHOWN] = False
    data['battlePassStorage'][BattlePassStorageKeys.INTRO_VIDEO_SHOWN] = False


def _migrateTo69(core, data, initialized):
    data['gameExtData'][GAME.HULLLOCK_ENABLED] = True


def _migrateTo70(core, data, initialized):
    gameData = data['gameExtData2']
    gameData[GAME.SHOW_ARTY_HIT_ON_MAP] = True
    spgAim = data['spgAim']
    spgAim[SPGAim.SHOTS_RESULT_INDICATOR] = True
    spgAim[SPGAim.SPG_SCALE_WIDGET] = True
    spgAim[SPGAim.SPG_STRATEGIC_CAM_MODE] = 0
    spgAim[SPGAim.AUTO_CHANGE_AIM_MODE] = True
    spgAim[SPGAim.AIM_ENTRANCE_MODE] = 0


def _migrateTo71(core, data, initialized):
    data['rankedCarouselFilter2'] = {'role_HT_assault': False,
     'role_HT_break': False,
     'role_HT_universal': False,
     'role_HT_support': False,
     'role_MT_assault': False,
     'role_MT_universal': False,
     'role_MT_sniper': False,
     'role_MT_support': False,
     'role_ATSPG_assault': False,
     'role_ATSPG_universal': False,
     'role_ATSPG_sniper': False,
     'role_ATSPG_support': False,
     'role_LT_universal': False,
     'role_LT_wheeled': False,
     'role_SPG': False}


def _migrateTo72(core, data, initialized):
    data['gameExtData'][GAME.PRE_COMMANDER_CAM] = True
    data['gameExtData'][GAME.COMMANDER_CAM] = True
    data['battleHud'][GAME.SHOW_VEHICLE_HP_IN_PLAYERS_PANEL] = core.options.getSetting(GAME.SHOW_VEHICLE_HP_IN_PLAYERS_PANEL).getDefaultValue()
    data['battleHud'][GAME.SHOW_VEHICLE_HP_IN_MINIMAP] = core.options.getSetting(GAME.SHOW_VEHICLE_HP_IN_MINIMAP).getDefaultValue()


def _migrateTo73(core, data, initialized):
    data['gameExtData2'][GAME.GAMEPLAY_ONLY_10_MODE] = False


def _migrateTo74(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, 0)
    maskOffset = 131072
    valueToSave = (storedValue & maskOffset) >> 17
    if data['gameExtData2'].get(GAME.CUSTOMIZATION_DISPLAY_TYPE, None) is None:
        if valueToSave:
            clear = data['clear']
            clear[SETTINGS_SECTIONS.GAME_EXTENDED] = clear.get(SETTINGS_SECTIONS.GAME_EXTENDED, 0) | maskOffset
            data['gameExtData2'][GAME.CUSTOMIZATION_DISPLAY_TYPE] = 0
        else:
            data['gameExtData2'][GAME.CUSTOMIZATION_DISPLAY_TYPE] = 1
    return


def _migrateTo75(core, data, initialized):
    data['clear']['rankedCarouselFilter2'] = data['clear'].get('rankedCarouselFilter2', 0) | 1024


def _migrateTo76(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED_2, 0)
    maskOffset = 12
    valueToCheck = (storedValue & maskOffset) >> 2
    if valueToCheck == 1 or data['gameExtData2'].get(GAME.CUSTOMIZATION_DISPLAY_TYPE) == 1:
        data['gameExtData2'][GAME.CUSTOMIZATION_DISPLAY_TYPE] = 2


def _migrateTo77(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.VEH_POST_PROGRESSION_UNLOCK_MSG_NEED_SHOW] = True


def _migrateTo78(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
    onceOnlyHintsData = data['onceOnlyHints2']
    onceOnlyHintsData[OnceOnlyHints.VEHICLE_PREVIEW_POST_PROGRESSION_BUTTON_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.HERO_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.SWITCH_EQUIPMENT_AUXILIARY_LOADOUT_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.SWITCH_EQUIPMENT_ESSENTIALS_LOADOUT_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.COMPARE_MODIFICATIONS_PANEL_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.COMPARE_SPECIALIZATION_BUTTON_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.TRADE_IN_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.PERSONAL_TRADE_IN_VEHICLE_POST_PROGRESSION_ENTRY_POINT_HINT] = False
    data['uiStorage'][UI_STORAGE_KEYS.VEH_PREVIEW_POST_PROGRESSION_BULLET_SHOWN] = False


def _migrateTo79(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR]['birthdayCalendarIntroShowed'] = False


def _migrateTo80(core, data, initialized):
    pass


def _migrateTo81(core, data, initialized):
    data['rankedCarouselFilter1'] = {'ussr': False,
     'germany': False,
     'usa': False,
     'china': False,
     'france': False,
     'uk': False,
     'japan': False,
     'czech': False,
     'sweden': False,
     'poland': False,
     'italy': False,
     'lightTank': False,
     'mediumTank': False,
     'heavyTank': False,
     'SPG': False,
     'AT-SPG': False,
     'level_1': False,
     'level_2': False,
     'level_3': False,
     'level_4': False,
     'level_5': False,
     'level_6': False,
     'level_7': False,
     'level_8': False,
     'level_9': False,
     'level_10': False}
    data['rankedCarouselFilter2'] = {'premium': False,
     'elite': False,
     'igr': False,
     'rented': True,
     'event': True,
     'gameMode': False,
     'favorite': False,
     'bonus': False,
     'crystals': False,
     'ranked': True,
     'role_HT_assault': False,
     'role_HT_break': False,
     'role_HT_universal': False,
     'role_HT_support': False,
     'role_MT_assault': False,
     'role_MT_universal': False,
     'role_MT_sniper': False,
     'role_MT_support': False,
     'role_ATSPG_assault': False,
     'role_ATSPG_universal': False,
     'role_ATSPG_sniper': False,
     'role_ATSPG_support': False,
     'role_LT_universal': False,
     'role_LT_wheeled': False,
     'role_SPG': False}


def _migrateTo82(core, data, initialized):
    data['guiStartBehavior']['isRankedWelcomeViewShowed'] = False


def _migrateTo83(core, data, initialized):
    pass


def _migrateTo84(core, data, initialized):
    pass


def _migrateTo85(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS, GUI_START_BEHAVIOR
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GUI_START_BEHAVIOR, 0)
    settingOffset = 25165824
    if storedValue & settingOffset:
        clear = data['clear']
        clear[GUI_START_BEHAVIOR] = clear.get(SETTINGS_SECTIONS.GUI_START_BEHAVIOR, 0) | settingOffset


def _migrateTo86(core, data, initialized):
    for position in range(2) + range(17, 18):
        data['clear']['battlePassStorage'] = data['clear'].get('battlePassStorage', 0) | 1 << position


def _migrateTo87(core, data, initialized):
    gameData = data['gameExtData2']
    gameData[GAME.SCROLL_SMOOTHING] = True


def _migrateTo88(core, data, initialized):
    data['battlePassStorage'][BattlePassStorageKeys.EXTRA_CHAPTER_INTRO_SHOWN] = False
    data['battlePassStorage'][BattlePassStorageKeys.EXTRA_CHAPTER_VIDEO_SHOWN] = False


def _migrateTo89(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from account_helpers.settings_core.settings_constants import CONTOUR
    if not initialized:
        data[SETTINGS_SECTIONS.CONTOUR][CONTOUR.ENHANCED_CONTOUR] = False
        data[SETTINGS_SECTIONS.CONTOUR][CONTOUR.CONTOUR_PENETRABLE_ZONE] = 0
        data[SETTINGS_SECTIONS.CONTOUR][CONTOUR.CONTOUR_IMPENETRABLE_ZONE] = 0


def _migrateTo90(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    data[SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_1] = {'ussr': False,
     'germany': False,
     'usa': False,
     'china': False,
     'france': False,
     'uk': False,
     'japan': False,
     'czech': False,
     'sweden': False,
     'poland': False,
     'italy': False,
     'lightTank': True,
     'mediumTank': True,
     'heavyTank': True,
     'SPG': False,
     'AT-SPG': False,
     'level_1': False,
     'level_2': False,
     'level_3': False,
     'level_4': False,
     'level_5': False,
     'level_6': False,
     'level_7': False,
     'level_8': False,
     'level_9': False,
     'level_10': False}
    data[SETTINGS_SECTIONS.ROYALE_CAROUSEL_FILTER_2] = {'premium': False,
     'elite': False,
     'igr': False,
     'rented': True,
     'event': True,
     'gameMode': False,
     'favorite': False,
     'bonus': False,
     'crystals': False,
     'battleRoyale': True}


def _migrateTo91(core, data, initialized):
    pass


def _migrateTo92(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.RESOURCE_WELL_INTRO_SHOWN] = False


def _migrateTo93(_, data, __):
    from account_helpers import AccountSettings
    from account_helpers.AccountSettings import FUN_RANDOM_CAROUSEL_FILTER_1, FUN_RANDOM_CAROUSEL_FILTER_2
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS as SECTIONS
    data[SECTIONS.FUN_RANDOM_CAROUSEL_FILTER_1] = AccountSettings.getFilterDefault(FUN_RANDOM_CAROUSEL_FILTER_1)
    data[SECTIONS.FUN_RANDOM_CAROUSEL_FILTER_2] = AccountSettings.getFilterDefault(FUN_RANDOM_CAROUSEL_FILTER_2)


def _migrateTo94(core, data, initialized):
    onceOnlyHintsData = data['onceOnlyHints2']
    onceOnlyHintsData[OnceOnlyHints.BATTLE_MATTERS_FIGHT_BUTTON_HINT] = False
    onceOnlyHintsData[OnceOnlyHints.BATTLE_MATTERS_ENTRY_POINT_BUTTON_HINT] = False
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    data[SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS] = {'shown': 0}


def _migrateTo95(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS, SETTINGS_SECTIONS
    data[SETTINGS_SECTIONS.UI_STORAGE_2][UI_STORAGE_KEYS.ROCKET_ACCELERATION_HIGHLIGHTS_COUNTER] = 0


def _migrateTo96(core, data, initialized):
    data['comp7CarouselFilter1'] = {'ussr': False,
     'germany': False,
     'usa': False,
     'china': False,
     'france': False,
     'uk': False,
     'japan': False,
     'czech': False,
     'sweden': False,
     'poland': False,
     'italy': False,
     'lightTank': False,
     'mediumTank': False,
     'heavyTank': False,
     'SPG': False,
     'AT-SPG': False,
     'level_1': False,
     'level_2': False,
     'level_3': False,
     'level_4': False,
     'level_5': False,
     'level_6': False,
     'level_7': False,
     'level_8': False,
     'level_9': False,
     'level_10': False}
    data['comp7CarouselFilter2'] = {'premium': False,
     'elite': False,
     'igr': False,
     'rented': True,
     'event': True,
     'gameMode': False,
     'favorite': False,
     'bonus': False,
     'crystals': False,
     'comp7': True,
     'role_HT_assault': False,
     'role_HT_break': False,
     'role_HT_universal': False,
     'role_HT_support': False,
     'role_MT_assault': False,
     'role_MT_universal': False,
     'role_MT_sniper': False,
     'role_MT_support': False,
     'role_ATSPG_assault': False,
     'role_ATSPG_universal': False,
     'role_ATSPG_sniper': False,
     'role_ATSPG_support': False,
     'role_LT_universal': False,
     'role_LT_wheeled': False,
     'role_SPG': False}
    data['guiStartBehavior']['isComp7IntroShown'] = False


def _migrateTo97(core, data, initialized):
    pass


def _migrateTo98(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, 0)
    settingOffset = 1073741824
    if storedValue & settingOffset:
        clear = data['clear']
        clear['onceOnlyHints'] = clear.get('onceOnlyHints', 0) | settingOffset


def _migrateTo99(_, data, __):
    from account_helpers import AccountSettings
    from account_helpers.AccountSettings import FUN_RANDOM_CAROUSEL_FILTER_1, FUN_RANDOM_CAROUSEL_FILTER_2
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS as SECTIONS
    data[SECTIONS.FUN_RANDOM_CAROUSEL_FILTER_1] = AccountSettings.getFilterDefault(FUN_RANDOM_CAROUSEL_FILTER_1)
    data[SECTIONS.FUN_RANDOM_CAROUSEL_FILTER_2] = AccountSettings.getFilterDefault(FUN_RANDOM_CAROUSEL_FILTER_2)


def _migrateTo100(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from account_helpers.settings_core.ServerSettingsManager import BATTLE_MATTERS_KEYS
    data[SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS] = {BATTLE_MATTERS_KEYS.QUESTS_SHOWN: core.serverSettings.getBattleMattersQuestWasShowed(),
     BATTLE_MATTERS_KEYS.QUEST_PROGRESS: 0}


def _migrateTo101(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.COMP7_INTRO_SHOWN] = False


def _migrateTo102(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.CREW_22_WELCOME_SHOWN] = False
    feedbackBattleEvents = data.get('feedbackBattleEvents', {})
    feedbackBattleEvents[BATTLE_EVENTS.CREW_PERKS] = True


def _migrateTo103(core, data, initialized):
    from account_helpers import AccountSettings
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS, LIMITED_UI_STORAGES, LIMITED_UI_SPAM_OFF, LIMITED_UI_KEY
    for storage in LIMITED_UI_STORAGES:
        data[storage][LIMITED_UI_KEY] = 0

    settingsPrefix = 'uiSpamVisited_{}'
    bitMask = 0
    for index, key in enumerate(LIMITED_UI_SPAM_OFF.ORDER):
        if AccountSettings.getUIFlag(settingsPrefix.format(key)):
            AccountSettings.setUIFlag(settingsPrefix.format(key), False)
            bitMask |= 1 << index

    data[SETTINGS_SECTIONS.LIMITED_UI_1][LIMITED_UI_KEY] = bitMask
    newSettingsCounter = AccountSettings.getSettings(NEW_SETTINGS_COUNTER)
    newSettingsCounter['GameSettings'].update({GAME.LIMITED_UI_ACTIVE: True})
    AccountSettings.setSettings(NEW_SETTINGS_COUNTER, newSettingsCounter)


def _migrateTo104(_, data, __):
    from account_helpers import AccountSettings
    from account_helpers.AccountSettings import FUN_RANDOM_CAROUSEL_FILTER_1, FUN_RANDOM_CAROUSEL_FILTER_2
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS as SECTIONS
    data[SECTIONS.FUN_RANDOM_CAROUSEL_FILTER_1] = AccountSettings.getFilterDefault(FUN_RANDOM_CAROUSEL_FILTER_1)
    data[SECTIONS.FUN_RANDOM_CAROUSEL_FILTER_2] = AccountSettings.getFilterDefault(FUN_RANDOM_CAROUSEL_FILTER_2)


def _migrateTo105(_, __, ___):
    pass


def _migrateTo106(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from account_helpers.settings_core.ServerSettingsManager import BATTLE_MATTERS_KEYS
    resetQuests = (5, 6, 7, 8, 9, 11, 12, 16, 18, 21, 23)
    lastShowedQuest = core.serverSettings.getBattleMattersQuestWasShowed() + 1
    if lastShowedQuest in resetQuests:
        data[SETTINGS_SECTIONS.BATTLE_MATTERS_QUESTS][BATTLE_MATTERS_KEYS.QUEST_PROGRESS] = 0


def _migrateTo107(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS, SETTINGS_SECTIONS
    data[SETTINGS_SECTIONS.UI_STORAGE_2][UI_STORAGE_KEYS.DUAL_ACCURACY_HIGHLIGHTS_COUNTER] = 0


def _migrateTo108(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN] = False


def _migrateTo109(core, data, initialized):
    data['gameExtData2'][GAME.GAMEPLAY_DEV_MAPS] = True


def _migrateTo110(core, data, initialized):
    pass


def _migrateTo111(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.IS_PRESTIGE_ONBOARDING_VIEWED] = False
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.PRESTIGE_FIRST_ENTRY_NOTIFICATION_SHOWN] = False


def _migrateTo112(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.COMP7_SEASON_STATISTICS_SHOWN] = False


def _migrateTo113(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from account_helpers.settings_core.settings_constants import SeniorityAwardsStorageKeys as keys
    data[SETTINGS_SECTIONS.SENIORITY_AWARDS_STORAGE][keys.SENIORITY_AWARDS_ON_PAUSE_NOTIFICATION_SHOWED] = False


def _migrateTo114(core, data, initialized):
    pass


def _migrateTo115(core, data, initialized):
    data['battlePassStorage'][BattlePassStorageKeys.FLAGS_VERSION_HOLIDAY] = 0


def _migrateTo116(core, data, initialized):
    if initialized:
        newbiesConfigs = {'gameData': {GAME.REPLAY_ENABLED: 1,
                      GAME.SNIPER_MODE_STABILIZATION: True,
                      GAME.SHOW_VEH_MODELS_ON_MAP: 2},
         'gameExtData': {GAME.CAROUSEL_TYPE: 0,
                         GAME.DOUBLE_CAROUSEL_TYPE: 0,
                         GAME.VEHICLE_CAROUSEL_STATS: 0,
                         GAME.PRE_COMMANDER_CAM: False,
                         GAME.INCREASED_ZOOM: True,
                         GAME.HULLLOCK_ENABLED: False,
                         GAME.MINIMAP_MIN_SPOTTING_RANGE: True,
                         GAME.MINIMAP_VIEW_RANGE: True,
                         GAME.MINIMAP_MAX_VIEW_RANGE: False,
                         GAME.MINIMAP_DRAW_RANGE: True},
         'gameExtData2': {GAME.CUSTOMIZATION_DISPLAY_TYPE: 2},
         'dogTags': {GAME.SHOW_VICTIMS_DOGTAG: False,
                     GAME.SHOW_DOGTAG_TO_KILLER: False,
                     GAME.SHOW_KILLERS_DOGTAG: False},
         'graphicsData': {GAME.LENS_EFFECT: False},
         'battleHud': {GAME.SHOW_VEHICLE_HP_IN_PLAYERS_PANEL: 0,
                       ScorePanelStorageKeys.SHOW_HP_VALUES: True},
         'feedbackDamageIndicator': {DAMAGE_INDICATOR.TYPE: 1,
                                     DAMAGE_INDICATOR.PRESET_ALLIES: False,
                                     DAMAGE_INDICATOR.DAMAGE_VALUE: True,
                                     DAMAGE_INDICATOR.DYNAMIC_INDICATOR: True,
                                     DAMAGE_INDICATOR.VEHICLE_INFO: True},
         'feedbackBattleEvents': {BATTLE_EVENTS.SHOW_IN_BATTLE: True,
                                  BATTLE_EVENTS.EVENT_NAME: True,
                                  BATTLE_EVENTS.VEHICLE_INFO: True,
                                  BATTLE_EVENTS.BLOCKED_DAMAGE: True,
                                  BATTLE_EVENTS.RECEIVED_DAMAGE: True,
                                  BATTLE_EVENTS.RECEIVED_CRITS: True,
                                  BATTLE_EVENTS.ENEMIES_STUN: False,
                                  BATTLE_EVENTS.BASE_CAPTURE_DROP: True,
                                  BATTLE_EVENTS.BASE_CAPTURE: True,
                                  BATTLE_EVENTS.ENEMY_DETECTION: True,
                                  BATTLE_EVENTS.ENEMY_RAM_ATTACK: True,
                                  BATTLE_EVENTS.ENEMY_KILL: True,
                                  BATTLE_EVENTS.ENEMY_TRACK_DAMAGE: True,
                                  BATTLE_EVENTS.ENEMY_CRITICAL_HIT: True,
                                  BATTLE_EVENTS.ENEMY_HP_DAMAGE: True,
                                  BATTLE_EVENTS.ENEMY_WORLD_COLLISION: True,
                                  BATTLE_EVENTS.ENEMY_DETECTION_DAMAGE: True,
                                  BATTLE_EVENTS.ENEMY_ASSIST_STUN: True,
                                  BATTLE_EVENTS.ENEMY_BURNING: True},
         'feedbackDamageLog': {DAMAGE_LOG.TOTAL_DAMAGE: True,
                               DAMAGE_LOG.BLOCKED_DAMAGE: True,
                               DAMAGE_LOG.ASSIST_DAMAGE: True,
                               DAMAGE_LOG.ASSIST_STUN: True,
                               DAMAGE_LOG.SHOW_DETAILS: 0},
         'FEEDBACK_BORDER_MAP': {'battleBorderMapMode': 2}}
        for configGroup, configs in newbiesConfigs.items():
            if data.get(configGroup):
                data[configGroup].update(configs)
            data[configGroup] = configs

        newbiesAimData = {'arcade': {'netType': 0,
                    'centralTagType': 4},
         'sniper': {'net': 100,
                    'netType': 0,
                    'centralTag': 100,
                    'centralTagType': 4,
                    'reloader': 100,
                    'condition': 100,
                    'mixingType': 3,
                    'mixing': 100,
                    'gunTagType': 9,
                    'gunTag': 100,
                    'cassette': 100,
                    'reloaderTimer': 100,
                    'zoomIndicator': 100}}
        aimData = data.get('aimData')
        if aimData:
            for aimDataType in newbiesAimData:
                if aimDataType in aimData:
                    data['aimData'][aimDataType].update(newbiesAimData[aimDataType])
                data['aimData'][aimDataType] = newbiesAimData[aimDataType]

        else:
            data['aimData'] = newbiesAimData
        newbiesMarkersData = {'enemy': {'markerBaseHp': 1,
                   'markerBaseLevel': True,
                   'markerBaseVehicleName': True,
                   'markerBasePlayerName': False,
                   'markerAltIcon': True,
                   'markerAltVehicleName': True,
                   'markerAltPlayerName': True,
                   'markerAltHp': 1},
         'ally': {'markerBaseHp': 1,
                  'markerBaseLevel': True,
                  'markerBaseVehicleName': True,
                  'markerBasePlayerName': False,
                  'markerAltIcon': True,
                  'markerAltVehicleName': True,
                  'markerAltPlayerName': True,
                  'markerAltHp': 1},
         'dead': {'markerBaseHp': 3,
                  'markerBaseHpIndicator': False,
                  'markerBaseVehicleName': True,
                  'markerAltIcon': True,
                  'markerAltVehicleName': True,
                  'markerAltPlayerName': False,
                  'markerAltHp': 1}}
        markersData = data.get('markersData')
        if markersData:
            for markerType in newbiesMarkersData:
                if markerType in markersData:
                    data['markersData'][markerType].update(newbiesMarkersData[markerType])
                data['markersData'][markerType] = newbiesMarkersData[markerType]

        else:
            data['markersData'] = newbiesMarkersData
    elif 'dogTags' in data:
        data['dogTags'][GAME.SHOW_KILLERS_DOGTAG] = True
    else:
        data['dogTags'] = {GAME.SHOW_KILLERS_DOGTAG: True}


def _migrateTo117(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS, LIMITED_UI_STORAGES_ALL, LIMITED_UI_SPAM_OFF, LIMITED_UI_KEY, UI_STORAGE_KEYS
    itemsCache = dependency.instance(IItemsCache)
    sectionBitsCount = 32
    permanentRulesLength = len(LIMITED_UI_SPAM_OFF.ORDER)
    commonRulesStartLength = sectionBitsCount - permanentRulesLength
    firstSectionValue = data[SETTINGS_SECTIONS.LIMITED_UI_1].get(LIMITED_UI_KEY, _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.LIMITED_UI_1, 0))
    secondSectionValue = data[SETTINGS_SECTIONS.LIMITED_UI_2].get(LIMITED_UI_KEY, _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.LIMITED_UI_2, 0))
    for storage in LIMITED_UI_STORAGES_ALL:
        data[storage][LIMITED_UI_KEY] = 0

    permanentRules = firstSectionValue & (1 << permanentRulesLength) - 1
    positionToDeleteStart = 10
    positionToDeleteEnd = 12
    permanentRulesRight = permanentRules & (1 << positionToDeleteStart) - 1
    permanentRulesLeft = permanentRules >> positionToDeleteEnd & (1 << permanentRulesLength - positionToDeleteEnd) - 1
    permanentRules = (permanentRulesLeft << positionToDeleteStart | permanentRulesRight) & (1 << permanentRulesLength - 2) - 1
    data[SETTINGS_SECTIONS.LIMITED_UI_PERMANENT_1][LIMITED_UI_KEY] = permanentRules
    commonRules = firstSectionValue >> permanentRulesLength & (1 << commonRulesStartLength) - 1
    rulesCount = itemsCache.items.stats.luiVersion
    allCommonRulesCompleted = (1 << rulesCount) - 1
    if rulesCount > commonRulesStartLength:
        commonRules = (secondSectionValue << commonRulesStartLength | commonRules) & allCommonRulesCompleted
    data[SETTINGS_SECTIONS.LIMITED_UI_1][LIMITED_UI_KEY] = commonRules
    data['uiStorage'][UI_STORAGE_KEYS.LIMITED_UI_ALL_NOVICE_RULES_COMPLETED] = False
    if rulesCount == 0 or commonRules & allCommonRulesCompleted == allCommonRulesCompleted:
        data['uiStorage'][UI_STORAGE_KEYS.LIMITED_UI_ALL_NOVICE_RULES_COMPLETED] = True
    clear = data['clear']
    hintsToClear = {('onceOnlyHints', _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS, 0)): (1, 24, 25),
     ('onceOnlyHints2', _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS_2, 0)): (0,)}
    for sectionData, hintsPositions in hintsToClear.items():
        section, sectionValue = sectionData
        for bitPosition in hintsPositions:
            settingOffset = 1 << bitPosition
            if sectionValue & settingOffset:
                clear[section] = clear.get(section, 0) | settingOffset


def _migrateTo118(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.UI_STORAGE, 0)
    clear = data['clear']
    for bitPosition in (9, 18, 26):
        settingOffset = 1 << bitPosition
        if storedValue & settingOffset:
            clear['uiStorage'] = clear.get('uiStorage', 0) | settingOffset

    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.UI_STORAGE_2, 0)
    clear = data['clear']
    for bitPosition in (0, 8):
        settingOffset = 1 << bitPosition
        if storedValue & settingOffset:
            clear[SETTINGS_SECTIONS.UI_STORAGE_2] = clear.get(SETTINGS_SECTIONS.UI_STORAGE_2, 0) | settingOffset


def _migrateTo119(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN] = False


def _migrateTo120(core, data, initialized):
    itemsCache = dependency.instance(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)
    import gui.prebattle_hints.newbie_controller
    from gui.battle_hints.newbie_battle_hints_controller import NEWBIE_SETTINGS_MAX_BATTLES as BH_NEWBIE_MAX_BATTLES
    disabled = itemsCache.items.stats.attributes & constants.ACCOUNT_ATTR.NEWBIE_FEATURES_DISABLED
    battlesCount = itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
    data['gameExtData2'][GAME.NEWBIE_PREBATTLE_HINTS] = not disabled and battlesCount <= gui.prebattle_hints.newbie_controller.IS_NEWBIE_MAX_BATTLES
    data['gameExtData2'][GAME.NEWBIE_BATTLE_HINTS] = not disabled and battlesCount <= BH_NEWBIE_MAX_BATTLES
    newbieGroup = itemsCache.items.stats.newbieHintsGroup
    abConfig = lobbyContext.getServerSettings().abFeatureTestConfig
    if not disabled and newbieGroup and hasattr(abConfig, 'newbieHints'):
        properties = abConfig.newbieHints.get(newbieGroup)['properties']
        for param in [GAME.NEWBIE_PREBATTLE_HINTS, GAME.NEWBIE_BATTLE_HINTS]:
            if param in properties:
                data['gameExtData2'][param] = properties[param]


def _migrateTo121(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    gameData = data['gameData']
    gameExtData2 = data['gameExtData2']
    currentVal = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.GAME, 0)
    gameExtData2[GAME.ENABLE_SERVER_AIM] = __migrateMaskValue(currentVal, 1, 8)
    if GAME.ENABLE_SERVER_AIM in gameData:
        gameData.pop(GAME.ENABLE_SERVER_AIM)
    if initialized:
        defaultValue = core.options.getSetting(GAME.POSTMORTEM_MODE).getNoviceValue()
    else:
        defaultValue = core.options.getSetting(GAME.POSTMORTEM_MODE).getDefaultValue()
    gameData[GAME.POSTMORTEM_MODE] = defaultValue


def _migrateTo122(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.CREW_5075_WELCOME_SHOWN] = False


def _migrateTo123(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.CLAN_SUPPLY_INTRO_SHOWN] = False


def _migrateTo124(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import GUI_START_BEHAVIOR
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN] = False
    data[GUI_START_BEHAVIOR][GuiSettingsBehavior.COMP7_SEASON_STATISTICS_SHOWN] = False


def _migrateTo125(core, data, initialized):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    storedValue = _getSettingsCache().getSectionSettings(SETTINGS_SECTIONS.ONCE_ONLY_HINTS_2, 0)
    clear = data['clear']
    for bitPosition in (27, 28):
        settingOffset = 1 << bitPosition
        if storedValue & settingOffset:
            clear['onceOnlyHints2'] = clear.get('onceOnlyHints2', 0) | settingOffset


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
  False),
 (54,
  _migrateTo54,
  False,
  False),
 (55,
  _migrateTo55,
  False,
  False),
 (56,
  _migrateTo56,
  False,
  False),
 (57,
  _migrateTo57,
  False,
  False),
 (58,
  _migrateTo58,
  False,
  False),
 (59,
  _migrateTo59,
  False,
  False),
 (60,
  _migrateTo60,
  False,
  False),
 (61,
  _migrateTo61,
  False,
  False),
 (62,
  _migrateTo62,
  False,
  False),
 (63,
  _migrateTo63,
  False,
  False),
 (64,
  _migrateTo64,
  False,
  False),
 (65,
  _migrateTo65,
  False,
  False),
 (66,
  _migrateTo66,
  False,
  False),
 (67,
  _migrateTo67,
  False,
  False),
 (68,
  _migrateTo68,
  False,
  False),
 (69,
  _migrateTo69,
  False,
  False),
 (70,
  _migrateTo70,
  False,
  False),
 (71,
  _migrateTo71,
  False,
  False),
 (72,
  _migrateTo72,
  False,
  False),
 (73,
  _migrateTo73,
  False,
  False),
 (74,
  _migrateTo74,
  False,
  False),
 (75,
  _migrateTo75,
  False,
  False),
 (76,
  _migrateTo76,
  False,
  False),
 (77,
  _migrateTo77,
  False,
  False),
 (78,
  _migrateTo78,
  False,
  False),
 (79,
  _migrateTo79,
  False,
  False),
 (80,
  _migrateTo80,
  False,
  False),
 (81,
  _migrateTo81,
  False,
  False),
 (82,
  _migrateTo82,
  False,
  False),
 (83,
  _migrateTo83,
  False,
  False),
 (84,
  _migrateTo84,
  False,
  False),
 (85,
  _migrateTo85,
  False,
  False),
 (86,
  _migrateTo86,
  False,
  False),
 (87,
  _migrateTo87,
  False,
  False),
 (88,
  _migrateTo88,
  False,
  False),
 (89,
  _migrateTo89,
  False,
  False),
 (90,
  _migrateTo90,
  False,
  False),
 (91,
  _migrateTo91,
  False,
  False),
 (92,
  _migrateTo92,
  False,
  False),
 (93,
  _migrateTo93,
  False,
  False),
 (94,
  _migrateTo94,
  False,
  False),
 (95,
  _migrateTo95,
  False,
  False),
 (96,
  _migrateTo96,
  False,
  False),
 (97,
  _migrateTo97,
  False,
  False),
 (98,
  _migrateTo98,
  False,
  False),
 (99,
  _migrateTo99,
  False,
  False),
 (100,
  _migrateTo100,
  False,
  False),
 (101,
  _migrateTo101,
  False,
  False),
 (102,
  _migrateTo102,
  False,
  False),
 (103,
  _migrateTo103,
  False,
  False),
 (104,
  _migrateTo104,
  False,
  False),
 (105,
  _migrateTo105,
  False,
  False),
 (106,
  _migrateTo106,
  False,
  False),
 (107,
  _migrateTo107,
  False,
  False),
 (108,
  _migrateTo108,
  False,
  False),
 (109,
  _migrateTo109,
  False,
  False),
 (110,
  _migrateTo110,
  False,
  False),
 (111,
  _migrateTo111,
  False,
  False),
 (112,
  _migrateTo112,
  False,
  False),
 (113,
  _migrateTo113,
  False,
  False),
 (114,
  _migrateTo114,
  False,
  False),
 (115,
  _migrateTo115,
  False,
  False),
 (116,
  _migrateTo116,
  False,
  False),
 (117,
  _migrateTo117,
  False,
  False),
 (118,
  _migrateTo118,
  False,
  False),
 (119,
  _migrateTo119,
  False,
  False),
 (120,
  _migrateTo120,
  False,
  False),
 (121,
  _migrateTo121,
  False,
  False),
 (122,
  _migrateTo122,
  False,
  False),
 (123,
  _migrateTo123,
  False,
  False),
 (124,
  _migrateTo124,
  False,
  False),
 (125,
  _migrateTo125,
  False,
  False))

@adisp_async
@adisp_process
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

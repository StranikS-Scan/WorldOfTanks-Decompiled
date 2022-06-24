# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/settings/config.py
from constants import HAS_DEV_RESOURCES, ARENA_GUI_TYPE, IS_DEVELOPMENT_BUILD
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS
from gui.shared.system_factory import registerScaleformBattlePackages, registerScaleformLobbyPackages, registerLobbyTooltipsBuilders
_COMMON_RELEASE_PACKAGES = ('gui.Scaleform.daapi.view.common',)
_COMMON_DEBUG_PACKAGES = ('gui.development.ui.GUIEditor', 'gui.development.ui.uilogging', 'gui.development.ui')
_LOBBY_DEVELOPMENT_BUILD_PACKAGES = tuple()
_LOBBY_RELEASE_PACKAGES = ('gui.Scaleform.daapi.view.lobby', 'gui.Scaleform.daapi.view.lobby.barracks', 'gui.Scaleform.daapi.view.lobby.boosters', 'gui.Scaleform.daapi.view.lobby.clans', 'gui.Scaleform.daapi.view.lobby.crewOperations', 'gui.Scaleform.daapi.view.lobby.customization', 'gui.Scaleform.daapi.view.lobby.cyberSport', 'gui.Scaleform.daapi.view.lobby.exchange', 'gui.Scaleform.daapi.view.lobby.fortifications', 'gui.Scaleform.daapi.view.lobby.hangar', 'gui.Scaleform.daapi.view.lobby.header', 'gui.Scaleform.daapi.view.lobby.inputChecker', 'gui.Scaleform.daapi.view.lobby.messengerBar', 'gui.Scaleform.daapi.view.lobby.prb_windows', 'gui.Scaleform.daapi.view.lobby.profile', 'gui.Scaleform.daapi.view.lobby.rankedBattles', 'gui.Scaleform.daapi.view.lobby.epicBattle', 'gui.Scaleform.daapi.view.lobby.store', 'gui.Scaleform.daapi.view.lobby.storage', 'gui.Scaleform.daapi.view.lobby.techtree', 'gui.Scaleform.daapi.view.lobby.trainings', 'gui.Scaleform.daapi.view.lobby.vehicle_preview', 'gui.Scaleform.daapi.view.lobby.vehicle_compare', 'gui.Scaleform.daapi.view.lobby.wgnc', 'gui.Scaleform.daapi.view.login', 'messenger.gui.Scaleform.view.lobby', 'gui.Scaleform.daapi.view.lobby.missions.regular', 'gui.Scaleform.daapi.view.lobby.missions.personal', 'gui.Scaleform.daapi.view.lobby.missions.linked_set', 'gui.Scaleform.daapi.view.bootcamp.lobby', 'gui.Scaleform.daapi.view.lobby.event_boards', 'gui.Scaleform.daapi.view.lobby.shop', 'gui.Scaleform.daapi.view.lobby.session_stats', 'gui.Scaleform.daapi.view.lobby.epicBattleTraining', 'gui.Scaleform.daapi.view.lobby.tank_setup', 'battle_royale.gui.Scaleform.daapi.view.lobby', 'gui.Scaleform.daapi.view.lobby.mapbox', 'gui.Scaleform.daapi.view.lobby.veh_post_progression', 'gui.Scaleform.daapi.view.lobby.fun_random')
_LOBBY_DEBUG_PACKAGES = ('gui.development.ui.messenger.view.lobby', 'gui.development.ui.demo', 'gui.Scaleform.daapi.view.lobby.epicBattleTraining', 'gui.development.ui.gf_viewer')
_BATTLE_RELEASE_PACKAGES = ('gui.Scaleform.daapi.view.battle.shared', 'messenger.gui.Scaleform.view.battle')
_BATTLE_DEBUG_PACKAGES = ('gui.development.ui.battle',)
_LOBBY_DEBUG_TOOLTIPS_BUILDERS_PATHS = (('gui.development.ui.tooltips.development_builders', _TOOLTIPS.DEVELOPMENT_SET),)
__LOBBY_TOOLTIPS_BUILDERS_PATHS = [('gui.Scaleform.daapi.view.tooltips.achievement_builders', _TOOLTIPS.ACHIEVEMENTS_SET),
 ('gui.Scaleform.daapi.view.tooltips.battle_consumable_builder', (_TOOLTIPS.BATTLE_CONSUMABLE,)),
 ('gui.Scaleform.daapi.view.tooltips.boosters_builders', _TOOLTIPS.BOOSTERS_SET),
 ('gui.Scaleform.daapi.view.tooltips.bootcamp_builders', _TOOLTIPS.BOOTCAMP_SET),
 ('gui.Scaleform.daapi.view.tooltips.common_builders', _TOOLTIPS.COMMON_SET),
 ('gui.Scaleform.daapi.view.tooltips.customization_builders', _TOOLTIPS.CUSTOMIZATION_SET),
 ('gui.Scaleform.daapi.view.tooltips.cybersport_builders', _TOOLTIPS.CYBER_SPORT_SET),
 ('gui.Scaleform.daapi.view.tooltips.elen_builders', _TOOLTIPS.ELEN_SET),
 ('gui.Scaleform.daapi.view.tooltips.epic_battle_builders', _TOOLTIPS.EPIC_BATTLE_SET),
 ('gui.Scaleform.daapi.view.tooltips.fortifications_builder', _TOOLTIPS.FORT_SORTIE_SET),
 ('gui.Scaleform.daapi.view.tooltips.personal_missions_builders', _TOOLTIPS.PERSONAL_MISSION_SET),
 ('gui.Scaleform.daapi.view.tooltips.quests_builders', _TOOLTIPS.QUESTS_SET),
 ('gui.Scaleform.daapi.view.tooltips.ranked_builders', _TOOLTIPS.RANKED_SET),
 ('gui.Scaleform.daapi.view.tooltips.settings_builders', _TOOLTIPS.SETTINGS_SET),
 ('gui.Scaleform.daapi.view.tooltips.tankman_builders', _TOOLTIPS.TANKMAN_SET),
 ('gui.Scaleform.daapi.view.tooltips.crew_skin_builders', _TOOLTIPS.CREW_SKIN_SET),
 ('gui.Scaleform.daapi.view.tooltips.crew_book_builders', _TOOLTIPS.CREW_BOOK_SET),
 ('gui.Scaleform.daapi.view.tooltips.tutorial_builders', _TOOLTIPS.TUTORIAL_SET),
 ('gui.Scaleform.daapi.view.tooltips.veh_cmp_builders', _TOOLTIPS.VEH_CMP_SET),
 ('gui.Scaleform.daapi.view.tooltips.vehicle_builders', _TOOLTIPS.VEHICLES_SET),
 ('gui.Scaleform.daapi.view.tooltips.blueprint_builders', _TOOLTIPS.BLUEPRINTS_SET),
 ('gui.Scaleform.daapi.view.tooltips.vehicle_items_builders', _TOOLTIPS.VEHICLES_ITEMS_SET),
 ('gui.Scaleform.daapi.view.tooltips.wgm_currency_builders', _TOOLTIPS.WGM_CURRENCY_SET),
 ('gui.Scaleform.daapi.view.tooltips.marathon_builders', _TOOLTIPS.MARATHON_SET),
 ('gui.Scaleform.daapi.view.tooltips.frontline_builders', _TOOLTIPS.FRONTLINE_SET),
 ('gui.Scaleform.daapi.view.tooltips.session_stats_builders', _TOOLTIPS.SESSION_STATS_SET),
 ('gui.Scaleform.daapi.view.tooltips.trade_in_builders', _TOOLTIPS.TRADE_IN_SET),
 ('gui.Scaleform.daapi.view.tooltips.crew_bundle_builders', _TOOLTIPS.CREW_BUNDLE_SET),
 ('gui.Scaleform.daapi.view.tooltips.demount_kit_builders', _TOOLTIPS.DEMOUNT_KIT_SET),
 ('gui.Scaleform.daapi.view.tooltips.vehicle_collector_builders', _TOOLTIPS.VEHICLE_COLLECTOR_SET),
 ('gui.Scaleform.daapi.view.tooltips.badges_builders', _TOOLTIPS.BADGES_SET),
 ('gui.Scaleform.daapi.view.tooltips.battle_pass_builders', _TOOLTIPS.BATTLE_PASS_SET),
 ('gui.Scaleform.daapi.view.tooltips.mapbox_lobby_builders', _TOOLTIPS.MAPBOX_LOBBY_SET),
 ('gui.Scaleform.daapi.view.tooltips.account_completion_builders', _TOOLTIPS.ACCOUNT_COMPLETION_SET),
 ('gui.Scaleform.daapi.view.tooltips.referral_program_builder', _TOOLTIPS.REFERRAL_PROGRAM_SET),
 ('gui.Scaleform.daapi.view.tooltips.resource_well_builders', _TOOLTIPS.RESOURCE_WELL_SET),
 ('gui.Scaleform.daapi.view.tooltips.fun_random_lobby_builders', _TOOLTIPS.FUN_RANDOM_LOBBY_SET)]
ADVANCED_COMPLEX_TOOLTIPS = {'#tooltips:hangar/ammo_panel/device/empty': 'equipment',
 '#tooltips:hangar/ammo_panel/equipment/empty': 'service',
 '#tooltips:equipment/empty': 'service',
 '#tooltips:XP': 'economyTankExperience',
 '#tooltips:hangar/ammo_panel/battleBooster/empty': 'instructions',
 '#tooltips:battleTypes/standart': 'gamemodeRandom',
 '#tooltips:battleTypes/unit': 'gamemodeTeam',
 '#tooltips:battleTypes/strongholds': 'gamemodeStronghold',
 '#tooltips:battleTypes/strongholds/disabled': 'gamemodeStronghold',
 '#tooltips:battleTypes/spec': 'gamemodeSpecial',
 '#tooltips:battleTypes/training': 'gamemodeTraining',
 '#tooltips:header/premium_buy': 'economyPremium',
 '#tooltips:header/premium_extend': 'economyPremium',
 '#tooltips:header/premium_upgrade': 'economyPremium'}
BATTLE_TOOLTIPS_BUILDERS_PATHS = (('gui.Scaleform.daapi.view.tooltips.settings_builders', _TOOLTIPS.SETTINGS_SET),
 ('gui.Scaleform.daapi.view.tooltips.battle_opt_devices_builder', _TOOLTIPS.BATTLE_BLOCK_TOOLTIPS),
 ('battle_royale.gui.Scaleform.daapi.view.tooltips.royale_battle_builders', _TOOLTIPS.ROYALE_BATTLE_SET),
 ('gui.Scaleform.daapi.view.tooltips.bootcamp_builders', _TOOLTIPS.BOOTCAMP_SET),
 ('gui.Scaleform.daapi.view.tooltips.epic_in_battle_builders', _TOOLTIPS.EPIC_IN_BATTE_SET))
LOBBY_PACKAGES = _LOBBY_RELEASE_PACKAGES
BATTLE_PACKAGES = _BATTLE_RELEASE_PACKAGES
COMMON_PACKAGES = _COMMON_RELEASE_PACKAGES
if HAS_DEV_RESOURCES:
    LOBBY_PACKAGES += _LOBBY_DEBUG_PACKAGES
    BATTLE_PACKAGES += _BATTLE_DEBUG_PACKAGES
    COMMON_PACKAGES += _COMMON_DEBUG_PACKAGES
    __LOBBY_TOOLTIPS_BUILDERS_PATHS += _LOBBY_DEBUG_TOOLTIPS_BUILDERS_PATHS
elif IS_DEVELOPMENT_BUILD:
    LOBBY_PACKAGES += _LOBBY_DEVELOPMENT_BUILD_PACKAGES
registerLobbyTooltipsBuilders(__LOBBY_TOOLTIPS_BUILDERS_PATHS)
registerScaleformLobbyPackages(LOBBY_PACKAGES)

def __registerDefaultBattlePackage(guiType, name):
    registerScaleformBattlePackages(guiType, BATTLE_PACKAGES + ('gui.Scaleform.daapi.view.battle.{}'.format(name),))


__registerDefaultBattlePackage(ARENA_GUI_TYPE.TUTORIAL, 'tutorial')
__registerDefaultBattlePackage(ARENA_GUI_TYPE.EVENT_BATTLES, 'event')
__registerDefaultBattlePackage(ARENA_GUI_TYPE.RANKED, 'ranked')
__registerDefaultBattlePackage(ARENA_GUI_TYPE.EPIC_RANDOM, 'epic_random')
__registerDefaultBattlePackage(ARENA_GUI_TYPE.EPIC_RANDOM_TRAINING, 'epic_random')
__registerDefaultBattlePackage(ARENA_GUI_TYPE.EPIC_BATTLE, 'epic')
__registerDefaultBattlePackage(ARENA_GUI_TYPE.EPIC_TRAINING, 'epic')
__registerDefaultBattlePackage(ARENA_GUI_TYPE.SORTIE_2, 'stronghold')
__registerDefaultBattlePackage(ARENA_GUI_TYPE.FORT_BATTLE_2, 'stronghold')
registerScaleformBattlePackages(ARENA_GUI_TYPE.BOOTCAMP, BATTLE_PACKAGES + ('gui.Scaleform.daapi.view.bootcamp.battle',))

def __registerScaleformBattlePackagesMapsTraining():
    packges = ('messenger.gui.Scaleform.view.battle', 'gui.Scaleform.daapi.view.battle.maps_training')
    if HAS_DEV_RESOURCES:
        packges += _BATTLE_DEBUG_PACKAGES
    registerScaleformBattlePackages(ARENA_GUI_TYPE.MAPS_TRAINING, packges)


__registerScaleformBattlePackagesMapsTraining()
BATTLE_PACKAGES_BY_DEFAULT = BATTLE_PACKAGES + ('gui.Scaleform.daapi.view.battle.classic',)

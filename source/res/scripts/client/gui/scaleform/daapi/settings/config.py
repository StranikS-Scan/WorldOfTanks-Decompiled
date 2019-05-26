# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/settings/config.py
from constants import HAS_DEV_RESOURCES, ARENA_GUI_TYPE, IS_DEVELOPMENT_BUILD
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS
_COMMON_RELEASE_PACKAGES = ('gui.Scaleform.daapi.view.common',)
_COMMON_DEBUG_PACKAGES = ('gui.development.ui.GUIEditor',)
_LOBBY_DEVELOPMENT_BUILD_PACKAGES = ('gui.Scaleform.daapi.view.lobby.epicBattleTraining',)
_LOBBY_RELEASE_PACKAGES = ('gui.Scaleform.daapi.view.lobby', 'gui.Scaleform.daapi.view.lobby.barracks', 'gui.Scaleform.daapi.view.lobby.boosters', 'gui.Scaleform.daapi.view.lobby.clans', 'gui.Scaleform.daapi.view.lobby.crewOperations', 'gui.Scaleform.daapi.view.lobby.customization', 'gui.Scaleform.daapi.view.lobby.cyberSport', 'gui.Scaleform.daapi.view.lobby.exchange', 'gui.Scaleform.daapi.view.lobby.fortifications', 'gui.Scaleform.daapi.view.lobby.hangar', 'gui.Scaleform.daapi.view.lobby.header', 'gui.Scaleform.daapi.view.lobby.inputChecker', 'gui.Scaleform.daapi.view.lobby.messengerBar', 'gui.Scaleform.daapi.view.lobby.prb_windows', 'gui.Scaleform.daapi.view.lobby.profile', 'gui.Scaleform.daapi.view.lobby.rankedBattles', 'gui.Scaleform.daapi.view.lobby.epicBattle', 'gui.Scaleform.daapi.view.lobby.store', 'gui.Scaleform.daapi.view.lobby.storage', 'gui.Scaleform.daapi.view.lobby.techtree', 'gui.Scaleform.daapi.view.lobby.trainings', 'gui.Scaleform.daapi.view.lobby.vehiclePreview', 'gui.Scaleform.daapi.view.lobby.vehiclePreview20', 'gui.Scaleform.daapi.view.lobby.vehicle_compare', 'gui.Scaleform.daapi.view.lobby.wgnc', 'gui.Scaleform.daapi.view.login', 'messenger.gui.Scaleform.view.lobby', 'gui.Scaleform.daapi.view.lobby.missions.regular', 'gui.Scaleform.daapi.view.lobby.missions.personal', 'gui.Scaleform.daapi.view.lobby.missions.linked_set', 'gui.Scaleform.daapi.view.bootcamp.lobby', 'gui.Scaleform.daapi.view.lobby.event_boards', 'gui.Scaleform.daapi.view.lobby.shop20', 'gui.Scaleform.daapi.view.lobby.session_stats')
_LOBBY_DEBUG_PACKAGES = ('gui.development.ui.messenger.view.lobby', 'gui.development.ui.demo', 'gui.Scaleform.daapi.view.lobby.epicBattleTraining')
_BATTLE_RELEASE_PACKAGES = ('gui.Scaleform.daapi.view.battle.shared', 'messenger.gui.Scaleform.view.battle')
_BATTLE_DEBUG_PACKAGES = ('gui.development.ui.battle',)
LOBBY_PACKAGES = _LOBBY_RELEASE_PACKAGES
BATTLE_PACKAGES = _BATTLE_RELEASE_PACKAGES
COMMON_PACKAGES = _COMMON_RELEASE_PACKAGES
BATTLE_PACKAGES_BY_ARENA_TYPE = {ARENA_GUI_TYPE.TUTORIAL: ('gui.Scaleform.daapi.view.battle.tutorial',),
 ARENA_GUI_TYPE.EVENT_BATTLES: ('gui.Scaleform.daapi.view.battle.event',),
 ARENA_GUI_TYPE.RANKED: ('gui.Scaleform.daapi.view.battle.ranked',),
 ARENA_GUI_TYPE.BOOTCAMP: ('gui.Scaleform.daapi.view.bootcamp.battle',),
 ARENA_GUI_TYPE.EPIC_RANDOM: ('gui.Scaleform.daapi.view.battle.epic_random',),
 ARENA_GUI_TYPE.EPIC_RANDOM_TRAINING: ('gui.Scaleform.daapi.view.battle.epic_random',),
 ARENA_GUI_TYPE.EPIC_BATTLE: ('gui.Scaleform.daapi.view.battle.epic',),
 ARENA_GUI_TYPE.EPIC_TRAINING: ('gui.Scaleform.daapi.view.battle.epic',)}
BATTLE_PACKAGES_BY_DEFAULT = ('gui.Scaleform.daapi.view.battle.classic',)
LOBBY_TOOLTIPS_BUILDERS_PATHS = (('gui.Scaleform.daapi.view.tooltips.achievement_builders', _TOOLTIPS.ACHIEVEMENTS_SET),
 ('gui.Scaleform.daapi.view.tooltips.battle_consumable_builder', (_TOOLTIPS.BATTLE_CONSUMABLE,)),
 ('gui.Scaleform.daapi.view.tooltips.boosters_builders', _TOOLTIPS.BOOSTERS_SET),
 ('gui.Scaleform.daapi.view.tooltips.bootcamp_builders', (_TOOLTIPS.BOOTCAMP_AWARD_MEDAL,)),
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
 ('gui.Scaleform.daapi.view.tooltips.session_stats_builders', _TOOLTIPS.SESSION_STATS_SET))
ADVANCED_COMPLEX_TOOLTIPS = {'#tooltips:hangar/ammo_panel/device/empty': 'equipment',
 '#tooltips:hangar/ammo_panel/equipment/empty': 'service',
 '#tooltips:equipment/empty': 'service',
 '#tooltips:XP': 'economyTankExperience',
 '#tooltips:hangar/ammo_panel/battleBooster/empty': 'instructions',
 '#tooltips:hangar/maintenance': 'service',
 '#tooltips:battleTypes/standart': 'gamemodeRandom',
 '#tooltips:battleTypes/unit': 'gamemodeTeam',
 '#tooltips:battleTypes/strongholds': 'gamemodeStronghold',
 '#tooltips:battleTypes/strongholds/disabled': 'gamemodeStronghold',
 '#tooltips:battleTypes/spec': 'gamemodeSpecial',
 '#tooltips:battleTypes/training': 'gamemodeTraining',
 '#tooltips:header/premium_buy': 'economyPremium',
 '#tooltips:header/premium_extend': 'economyPremium',
 '#tooltips:header/premium_upgrade': 'economyPremium'}
BATTLE_TOOLTIPS_BUILDERS_PATHS = (('gui.Scaleform.daapi.view.tooltips.settings_builders', _TOOLTIPS.SETTINGS_SET),)
if HAS_DEV_RESOURCES:
    LOBBY_PACKAGES += _LOBBY_DEBUG_PACKAGES
    BATTLE_PACKAGES += _BATTLE_DEBUG_PACKAGES
    COMMON_PACKAGES += _COMMON_DEBUG_PACKAGES
elif IS_DEVELOPMENT_BUILD:
    LOBBY_PACKAGES += _LOBBY_DEVELOPMENT_BUILD_PACKAGES

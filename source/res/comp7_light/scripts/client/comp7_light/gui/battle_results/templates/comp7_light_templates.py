# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/battle_results/templates/comp7_light_templates.py
from comp7_light.gui.battle_results.components import comp7_light_components
from comp7_core.gui.battle_results.components import comp7_core_components
from comp7_core.gui.battle_results.components import progress
from comp7_core.gui.battle_results.components import shared as comp7_core_shared
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_results.components import base, vehicles, shared, style
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.battle_results.templates.regular import _PERSONAL_VO_META, REGULAR_PERSONAL_STATS_BLOCK, REGULAR_COMMON_STATS_BLOCK, TEAMS_VO_META
from helpers import i18n
_PERSONAL_VO_META.addMeta({'deserterStr': ''})
STATS_COMPONENT_NUMBER = 8
COMPONENTS_TO_EXCLUDE = (STATS_COMPONENT_NUMBER,)
COMP7_LIGHT_PERSONAL_STATS_BLOCK = REGULAR_PERSONAL_STATS_BLOCK.clone(*COMPONENTS_TO_EXCLUDE)
COMP7_LIGHT_PERSONAL_STATS_BLOCK.addComponent(STATS_COMPONENT_NUMBER, comp7_core_components.PersonalVehiclesComp7CoreStatsBlock(base.ListMeta(), 'statValues', _RECORD.PERSONAL))
COMP7_LIGHT_PERSONAL_STATS_BLOCK.addNextComponent(comp7_light_components.IsDeserterFlag('deserterStr', _RECORD.PERSONAL))
TOURNAMENT_COMP7_LIGHT_PERSONAL_STATS_BLOCK = COMP7_LIGHT_PERSONAL_STATS_BLOCK.clone()
TRAINING_COMP7_LIGHT_PERSONAL_STATS_BLOCK = COMP7_LIGHT_PERSONAL_STATS_BLOCK.clone()
SORTING_COMPONENT_NUMBER = 0
COMPONENTS_TO_EXCLUDE = (SORTING_COMPONENT_NUMBER,)
COMP7_LIGHT_COMMON_STATS_BLOCK = REGULAR_COMMON_STATS_BLOCK.clone(*COMPONENTS_TO_EXCLUDE)
TOURNAMENT_COMP7_LIGHT_COMMON_STATS_BLOCK = REGULAR_COMMON_STATS_BLOCK.clone(*COMPONENTS_TO_EXCLUDE)
TRAINING_COMP7_LIGHT_COMMON_STATS_BLOCK = REGULAR_COMMON_STATS_BLOCK.clone(*COMPONENTS_TO_EXCLUDE)
COMP7_LIGHT_COMMON_STATS_BLOCK.addComponent(SORTING_COMPONENT_NUMBER, comp7_core_shared.Comp7CoreSortingBlock())
COMP7_LIGHT_BATTLE_PASS_PROGRESS_STATS_BLOCK = progress.Comp7CoreBattlePassProgressBlock(base.ListMeta(), 'battlePass', _RECORD.PERSONAL)
VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shots', 0, 'shots'),
 ('hits', style.SlashedValuesBlock('hits'), 'hits'),
 ('explosionHits', 0, 'explosionHits'),
 ('damageDealt', 0, 'damageDealt'),
 ('sniperDamageDealt', 0, 'sniperDamageDealt'),
 ('damageDealtBySkills', 0, 'damageDealtBySkills'),
 ('directHitsReceived', 0, 'directHitsReceived'),
 ('piercingsReceived', 0, 'piercingsReceived'),
 ('noDamageDirectHitsReceived', 0, 'noDamageDirectHitsReceived'),
 ('explosionHitsReceived', 0, 'explosionHitsReceived'),
 ('damageBlockedByArmor', 0, 'damageBlockedByArmor'),
 ('teamHitsDamage', style.RedSlashedValuesBlock('teamHitsDamage'), 'teamHitsDamage'),
 ('spotted', 0, 'spotted'),
 ('damagedKilled', style.SlashedValuesBlock('damagedKilled'), 'damagedKilled'),
 ('damageAssisted', 0, 'damageAssisted'),
 ('stunDuration', 0.0, 'stunDuration'),
 ('damageAssistedStun', 0, 'damageAssistedStun'),
 ('stunNum', 0, 'stunNum'),
 ('capturePointsVal', style.SlashedValuesBlock('capturePointsVal'), 'capturePoints'),
 ('mileage', style.MetersToKillometersItem('mileage'), 'mileage'),
 ('healed', style.SlashedValuesBlock('healed'), 'healed'),
 ('capturedPointsOfInterest', 0, 'capturedPointsOfInterest'),
 ('roleSkillUsed', 0, 'roleSkillUsed')))
VEHICLE_STATS_BLOCK_VO_META.bind(comp7_core_components.Comp7CoreVehicleStatValuesBlock)
COMP7_LIGHT_TEAM_ITEM_VO_META = base.PropertyMeta((('achievements', shared.AchievementsBlock(base.ListMeta(), 'achievements'), 'achievements'),
 ('medalsCount', 0, 'achievementsCount'),
 ('vehicleStateStr', '', 'vehicleState'),
 ('vehicleStatePrefixStr', '', 'vehicleStatePrefix'),
 ('vehicleStateSuffixStr', '', 'vehicleStateSuffix'),
 ('killerID', 0, 'killerID'),
 ('deathReason', -1, 'deathReason'),
 ('isPrematureLeave', False, 'isPrematureLeave'),
 ('vehicleCD', 0, 'intCD'),
 ('vehicleFullName', i18n.makeString(INGAME_GUI.PLAYERS_PANEL_UNKNOWN_VEHICLE), 'vehicleName'),
 ('tankIcon', '../maps/icons/vehicle/small/noImage.png', 'vehicleIcon'),
 ('vehicleName', i18n.makeString(INGAME_GUI.PLAYERS_PANEL_UNKNOWN_VEHICLE), 'vehicleShortName'),
 ('vehicles', [{'icon': '../maps/icons/vehicle/noImage.png'}], 'vehicles'),
 ('vehicleSort', '', 'vehicleSort'),
 ('xpSort', 0, 'xpSort'),
 ('isSelf', False, 'isPersonal'),
 ('kills', 0, 'kills'),
 ('tkills', 0, 'tkills'),
 ('realKills', 0, 'realKills'),
 ('xp', 0, 'xp'),
 ('damageDealt', 0, 'damageDealt'),
 ('playerId', 0, 'playerID'),
 ('userVO', vehicles.TeamPlayerNameBlock(field='userVO'), 'player'),
 ('squadID', 0, 'squadIndex'),
 ('isOwnSquad', False, 'isPersonalSquad'),
 ('isTeamKiller', False, 'isTeamKiller'),
 ('isKilledByTeamKiller', False, 'isKilledByTeamKiller'),
 ('statValues', comp7_core_components.AllComp7CoreVehicleStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'),
 ('resourceCount', 0, 'fortResource'),
 ('rank', 0, 'rank'),
 ('rankIcon', '', 'rankIcon'),
 ('hasSelectedBadge', False, 'hasSelectedBadge'),
 ('badgeVO', vehicles.BadgeBlock(field='badgeVO'), 'badge'),
 ('playerRank', 0, 'playerRank'),
 ('respawns', 0, 'respawns'),
 ('suffixBadgeIcon', '', 'suffixBadgeIcon'),
 ('suffixBadgeStripIcon', '', 'suffixBadgeStripIcon'),
 ('prestigePoints', 0, 'prestigePoints'),
 ('isSuperSquad', False, 'isSuperSquad')))
COMP7_LIGHT_TEAM_ITEM_VO_META.bind(comp7_core_components.Comp7CoreVehicleStatsBlock)
COMP7_LIGHT_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(TEAMS_VO_META, '', _RECORD.VEHICLES)
COMP7_LIGHT_TEAMS_STATS_BLOCK.addNextComponent(comp7_core_components.Comp7CoreTeamStatsBlock(meta=base.ListMeta(), field='team1'))
COMP7_LIGHT_TEAMS_STATS_BLOCK.addNextComponent(comp7_core_components.Comp7CoreTeamStatsBlock(meta=base.ListMeta(), field='team2'))
EFFICIENCY_TITLE_WITH_SKILLS_VO = comp7_core_components.EfficiencyTitleWithSkills('efficiencyTitle')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/racing.py
from gui.battle_results.templates import regular
from helpers import i18n
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_results.components import base
from gui.battle_results.components import vehicles
from gui.battle_results.components import common
from gui.battle_results.components import style
from gui.battle_results.components import personal
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
regular.FINISH_RESULT_VO_META.bind(common.RegularFinishResultBlock)
_RACING_TABS_VO_META = base.ListMeta([{'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_EPICSTATS),
  'linkage': 'RacingStats',
  'viewId': 'RacingStats',
  'showWndBg': False}, {'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_TEAMSTATS),
  'linkage': 'TeamStatsUI',
  'viewId': 'TeamStatsUI',
  'showWndBg': False}])
RACING_TABS_BLOCK = base.StatsBlock(_RACING_TABS_VO_META, 'tabInfo')
RACING_TIME_STATS_BLOCK = base.StatsBlock(base.ListMeta(runtime=False), 'timeStats', _RECORD.COMMON)
RACING_TIME_STATS_BLOCK.addComponent(0, common.ArenaShortTimeVO('arenaCreateTimeOnlyStr', 'arenaCreateTime'))
RACING_TIME_STATS_BLOCK.addComponent(1, common.ArenaDurationVO('duration', 'duration'))
RACING_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(11)
RACING_COMMON_STATS_BLOCK.addComponent(11, RACING_TIME_STATS_BLOCK.clone())
RACING_ACHIEVEMENT_META = base.PropertyMeta((('enable', False, 'enable'), ('cupType', '', 'cupType')))
RACING_ACHIEVEMENT_META.bind(personal.RacingAchievementBlock)
RACING_PERSONAL_STATS_BLOCK = regular.REGULAR_PERSONAL_STATS_BLOCK.clone(2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16)
RACING_PERSONAL_STATS_BLOCK.addComponent(8, vehicles.PersonalVehiclesRacingStatsBlock(base.ListMeta(), 'statValues', _RECORD.PERSONAL))
RACING_PERSONAL_STATS_BLOCK.addNextComponent(personal.PersonalRacingPoints('racingPoints'))
RACING_PERSONAL_STATS_BLOCK.addNextComponent(personal.PersonalRacingDamageDealt('damageDealt'))
RACING_PERSONAL_STATS_BLOCK.addNextComponent(personal.PersonalRacingKills('kills'))
RACING_PERSONAL_STATS_BLOCK.addNextComponent(personal.PersonalRacingCapturePoints('capturePoints'))
RACING_PERSONAL_STATS_BLOCK.addNextComponent(personal.PersonalRacingFinishTime('racingFinishTime'))
RACING_PERSONAL_STATS_BLOCK.addNextComponent(personal.PersonalRacingAchievementsBlock(base.ListMeta(), 'racingAchievements', _RECORD.PERSONAL))
RACING_TEAM_ITEM_VO_META = base.PropertyMeta((('vehicleStateStr', '', 'vehicleState'),
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
 ('damageDealt', 0, 'damageDealt'),
 ('playerId', 0, 'playerID'),
 ('userVO', vehicles.TeamPlayerNameBlock(field='userVO'), 'player'),
 ('squadID', 0, 'squadIndex'),
 ('isOwnSquad', False, 'isPersonalSquad'),
 ('isTeamKiller', False, 'isTeamKiller'),
 ('isKilledByTeamKiller', False, 'isKilledByTeamKiller'),
 ('statValues', vehicles.AllRacingVehicleStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'),
 ('badge', 0, 'badge'),
 ('badgeIcon', '', 'badgeIcon'),
 ('suffixBadgeIcon', '', 'suffixBadgeIcon'),
 ('capturePoints', 0, 'capturePoints'),
 ('bowlCount', 0, 'bowlCount'),
 ('bowlsTooltip', '', 'bowlsTooltip')))
RACING_TEAM_ITEM_VO_META.bind(vehicles.RacingVehicleStatsBlock)
RACING_VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shots', 0, 'shots'),
 ('damageDealt', 0, 'damageDealt'),
 ('directHitsReceived', 0, 'directHitsReceived'),
 ('piercingsReceived', 0, 'piercingsReceived'),
 ('noDamageDirectHitsReceived', 0, 'noDamageDirectHitsReceived'),
 ('damageBlockedByArmor', 0, 'damageBlockedByArmor'),
 ('damagedKilled', style.SlashedValuesBlock('damagedKilled'), 'damagedKilled'),
 ('capturePointsVal', style.SlashedValuesBlock('capturePointsVal'), 'capturePoints'),
 ('racingFinishTime', '', 'racingFinishTime'),
 ('mileage', style.MetersToKillometersItem('mileage'), 'mileage')))
RACING_VEHICLE_STATS_BLOCK_VO_META.bind(vehicles.RacingVehicleStatValuesBlock)
RACING_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
RACING_TEAMS_STATS_BLOCK.addNextComponent(vehicles.RacingTeamStatsBlock(meta=base.ListMeta(), field='team1'))
RACING_TEAMS_STATS_BLOCK.addNextComponent(vehicles.RacingTeamStatsBlock(meta=base.ListMeta(), field='team2'))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_results/templates.py
from gui.battle_results.templates import regular
from gui.battle_results.components import base
from gui.battle_results.components import vehicles
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl import backport
from gui.impl.gen import R
from halloween.gui.battle_results.components import HWBattleVehicleStatsBlock, HWBattleTeamStatsBlock, HWSortingBlock, AllyTeamDamage, EnemyTeamDamage, AllRegularVehicleStatValuesBlock, RegularVehicleStatValuesBlock, DamageItem, KillsItem, PlayerNameItem, PlayerClanItem, VehicleNameItem, HalloweenXPItem, RespawnsItem, PlayerDBIDItem, BaseStatValuesBlock, AllBasesStatValuesBlock, ArenaDurationItem, HalloweenFinishResultBlock, QuestsProgressBlock, HWArenaFullNameItem
from halloween.gui.battle_results.style import MetersToKillometersItem
from halloween.gui.impl.gen.view_models.views.lobby.base_info_model import BaseStateEnum
TOTAL_VO_META = base.DictMeta({'damageDelta': 0,
 'kills': 0,
 'playerName': '',
 'playerDBID': 0,
 'playerClan': '',
 'vehicleName': '',
 'arenaDuration': '',
 'respawns': 0,
 'hwXP': 0,
 'allyTeamDamage': 0,
 'enemyTeamDamage': 0,
 'bases': [],
 'common': {},
 'team1': [],
 'team2': [],
 'quests': None})
HW_TOTAL_RESULTS_BLOCK = base.StatsBlock(TOTAL_VO_META, 'hw_meta')
HW_TOTAL_RESULTS_BLOCK.addNextComponent(DamageItem('damageDelta', _RECORD.PERSONAL))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(KillsItem('kills', _RECORD.PERSONAL))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(PlayerNameItem('playerName', _RECORD.PERSONAL))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(PlayerDBIDItem('playerDBID', _RECORD.PERSONAL))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(PlayerClanItem('playerClan', _RECORD.PERSONAL))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(VehicleNameItem('vehicleName', _RECORD.PERSONAL))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(ArenaDurationItem('arenaDuration', _RECORD.COMMON, 'duration'))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(RespawnsItem('respawns', _RECORD.PERSONAL))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(HalloweenXPItem('hwXP', _RECORD.PERSONAL))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(AllyTeamDamage('allyTeamDamage', _RECORD.VEHICLES))
HW_TOTAL_RESULTS_BLOCK.addNextComponent(EnemyTeamDamage('enemyTeamDamage', _RECORD.VEHICLES))
VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shots', '0', 'shots'),
 ('hits', '0 / 0', 'hits'),
 ('explosionHits', '0', 'explosionHits'),
 ('damageDealt', '0', 'damageDealt'),
 ('sniperDamageDealt', '0', 'sniperDamageDealt'),
 ('directHitsReceived', '0', 'directHitsReceived'),
 ('piercingsReceived', '0', 'piercingsReceived'),
 ('noDamageDirectHitsReceived', '0', 'noDamageDirectHitsReceived'),
 ('explosionHitsReceived', '0', 'explosionHitsReceived'),
 ('damageBlockedByArmor', '0', 'damageBlockedByArmor'),
 ('teamHitsDamage', '0 / 0', 'teamHitsDamage'),
 ('spotted', '0', 'spotted'),
 ('damagedKilled', '0 / 0', 'damagedKilled'),
 ('damageAssisted', '0', 'damageAssisted'),
 ('stunDuration', '0.0', 'stunDuration'),
 ('damageAssistedStun', '0', 'damageAssistedStun'),
 ('stunNum', '0', 'stunNum'),
 ('mileage', MetersToKillometersItem('mileage'), 'mileage'),
 ('respawns', '0', 'respawns')))
VEHICLE_STATS_BLOCK_VO_META.bind(RegularVehicleStatValuesBlock)
HW_TEAM_ITEM_VO_META = base.PropertyMeta((('achievements', '', 'achievements'),
 ('medalsCount', 0, 'achievementsCount'),
 ('vehicleStateStr', '', 'vehicleState'),
 ('vehicleStatePrefixStr', '', 'vehicleStatePrefix'),
 ('vehicleStateSuffixStr', '', 'vehicleStateSuffix'),
 ('killerID', 0, 'killerID'),
 ('deathReason', -1, 'deathReason'),
 ('isPrematureLeave', False, 'isPrematureLeave'),
 ('vehicleCD', 0, 'intCD'),
 ('vehicleLvl', 0, 'vehicleLvl'),
 ('vehicleType', '', 'vehicleType'),
 ('vehicleFullName', backport.text(R.strings.ingame_gui.players_panel.unknown_vehicle()), 'vehicleName'),
 ('tankIcon', '../maps/icons/vehicle/small/noImage.png', 'vehicleIcon'),
 ('vehicleName', backport.text(R.strings.ingame_gui.players_panel.unknown_vehicle()), 'vehicleShortName'),
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
 ('statValues', AllRegularVehicleStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'),
 ('resourceCount', 0, 'fortResource'),
 ('rank', 0, 'rank'),
 ('rankIcon', '', 'rankIcon'),
 ('hasSelectedBadge', False, 'hasSelectedBadge'),
 ('badgeID', 0, 'badgeID'),
 ('playerRank', 0, 'playerRank'),
 ('respawns', 0, 'respawns'),
 ('suffixBadgeIcon', '', 'suffixBadgeIcon'),
 ('suffixBadgeStripIcon', '', 'suffixBadgeStripIcon'),
 ('hwXP', 0, 'hwXP'),
 ('fairplayViolations', False, 'fairplayViolations'),
 ('isPremiumIGR', False, 'isPremiumIGR')))
HW_TEAM_ITEM_VO_META.bind(HWBattleVehicleStatsBlock)
HW_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
HW_TEAMS_STATS_BLOCK.addNextComponent(HWBattleTeamStatsBlock(meta=base.ListMeta(), field='team1'))
HW_TEAMS_STATS_BLOCK.addNextComponent(HWBattleTeamStatsBlock(meta=base.ListMeta(), field='team2'))
FINISH_RESULT_VO_META = base.PropertyMeta((('finishReasonStr', '', 'finishReasonLabel'), ('resultShortStr', '', 'shortResultLabel'), ('resultStr', '', 'fullResultLabel')))
FINISH_RESULT_VO_META.bind(HalloweenFinishResultBlock)
HW_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(0, 3, 7)
HW_COMMON_STATS_BLOCK.addComponent(0, HWSortingBlock())
HW_COMMON_STATS_BLOCK.addComponent(3, HWArenaFullNameItem('arenaStr'))
HW_COMMON_STATS_BLOCK.addComponent(7, HalloweenFinishResultBlock())
HW_BASE_VO_META = base.PropertyMeta((('baseLetter', '', 'baseLetter'), ('baseState', BaseStateEnum.NEUTRAL, 'baseState')))
HW_BASE_VO_META.bind(BaseStatValuesBlock)
HW_TOTAL_RESULTS_BLOCK.addNextComponent(AllBasesStatValuesBlock(base.ListMeta(), 'bases', _RECORD.PERSONAL))
HW_QUESTS_PROGRESS_STATS_BLOCK = QuestsProgressBlock(base.ListMeta(), 'quests', _RECORD.PERSONAL)

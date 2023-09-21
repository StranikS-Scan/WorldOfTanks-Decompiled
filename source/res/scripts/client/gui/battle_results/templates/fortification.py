# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/fortification.py
from gui.battle_results.components import common
from gui.battle_results.components import base
from gui.battle_results.templates import regular
from gui.battle_results.components import style
from gui.battle_results.components import vehicles
from gui.battle_results.br_constants import BattleResultsRecord as _RECORD
regular.FINISH_RESULT_VO_META.bind(common.StrongholdBattleFinishResultBlock)
STRONGHOLD_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
STRONGHOLD_BATTLE_COMMON_STATS_BLOCK.addNextComponent(common.StrongholdBattleFinishResultBlock(None, '', _RECORD.PERSONAL, _RECORD.PERSONAL_AVATAR))
STRONGHOLD_VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shots', 0, 'shots'),
 ('hits', style.SlashedValuesBlock('hits'), 'hits'),
 ('explosionHits', 0, 'explosionHits'),
 ('damageDealt', 0, 'damageDealt'),
 ('sniperDamageDealt', 0, 'sniperDamageDealt'),
 ('artilleryFortEquipDamageDealt', 0, 'artilleryFortEquipDamageDealt'),
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
 ('mileage', style.MetersToKillometersItem('mileage'), 'mileage')))
STRONGHOLD_VEHICLE_STATS_BLOCK_VO_META.bind(vehicles.StrongholdVehicleStatValuesBlock)
STRONGHOLD_TEAM_ITEM_VO_META = regular.TEAM_ITEM_VO_META.replace(('statValues', vehicles.AllStrongholdVehicleStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'))
STRONGHOLD_TEAM_ITEM_VO_META.bind(vehicles.StrongholdVehicleStatsBlock)
STRONGHOLD_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
STRONGHOLD_TEAMS_STATS_BLOCK.addComponent(0, vehicles.StrongholdTeamStatsBlock(base.ListMeta(), field='team1'))
STRONGHOLD_TEAMS_STATS_BLOCK.addComponent(1, vehicles.StrongholdTeamStatsBlock(base.ListMeta(), field='team2'))
STRONGHOLD_PERSONAL_STATS_BLOCK = regular.REGULAR_PERSONAL_STATS_BLOCK.clone(8)
STRONGHOLD_PERSONAL_STATS_BLOCK.addComponent(8, vehicles.PersonalVehiclesStrongholdStatsBlock(base.ListMeta(), 'statValues', _RECORD.PERSONAL))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/rts_battles.py
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_results.templates import regular
from gui.battle_results.components import base
from gui.battle_results.components import rts_battles
from gui.battle_results.components import style
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.battle_results.templates.regular import _TOTAL_EFFICIENCY_HEADER_META
_TOTAL_EFFICIENCY_HEADER_META.bind(rts_battles.SupplyTotalEfficiencyDetailsHeader)
RTS_TEXT_STATS_BLOCK = regular.REGULAR_TEXT_STATS_BLOCK.clone()
RTS_TEXT_STATS_BLOCK.addComponent(0, rts_battles.AllyTeamTitle('ownTitle'))
RTS_TEXT_STATS_BLOCK.addComponent(1, rts_battles.EnemyTeamTitle('enemyTitle'))
RTS_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone(7, 9, 10)
RTS_COMMON_STATS_BLOCK.addComponent(7, rts_battles.FinishResultBlock())
RTS_COMMON_STATS_BLOCK.addComponent(9, rts_battles.PersonalVehicleNamesBlock(base.ListMeta(), 'playerVehicleNames'))
RTS_COMMON_STATS_BLOCK.addComponent(10, rts_battles.PersonalVehiclesBlock(base.ListMeta(), 'playerVehicles', _RECORD.PERSONAL))
_EFFICIENCY_DETAILS_VO_META = base.PropertyMeta((('deathReason', -1, 'deathReason'),
 ('spotted', 0, 'spotted'),
 ('piercings', 0, 'piercings'),
 ('damageDealt', 0, 'damageDealt'),
 ('killCount', 0, 'killCount'),
 ('tankIcon', '../maps/icons/vehicle/small/noImage.png', 'vehicleIcon'),
 ('vehicleName', backport.text(R.strings.ingame_gui.players_panel.unknown_vehicle()), 'vehicleName'),
 ('isUserNameHidden', False, 'isUserNameHidden')))
_EFFICIENCY_DETAILS_VO_META.bind(rts_battles.RTSEnemyDetailsBlock)
RTS_PERSONAL_STATS_BLOCK = regular.REGULAR_PERSONAL_STATS_BLOCK.clone(1, 4, 6, 7, 8, 11)
RTS_PERSONAL_STATS_BLOCK.addComponent(1, rts_battles.TotalEfficiencyDetailsBlock(base.ListMeta(), 'details'))
RTS_PERSONAL_STATS_BLOCK.addComponent(4, rts_battles.GainCreditsInBattleItem('creditsStr'))
RTS_PERSONAL_STATS_BLOCK.addComponent(6, rts_battles.TotalMoneyDetailsBlock(base.ListMeta(), 'creditsData'))
RTS_PERSONAL_STATS_BLOCK.addComponent(7, rts_battles.TotalXPDetailsBlock(base.ListMeta(), 'xpData'))
RTS_PERSONAL_STATS_BLOCK.addComponent(8, rts_battles.PersonalVehiclesRTSStatsBlock(base.ListMeta(), 'statValues'))
RTS_PERSONAL_STATS_BLOCK.addComponent(11, rts_battles.TotalCrystalDetailsBlock(base.ListMeta(), 'crystalData'))
RTS_PERSONAL_STATS_BLOCK.addNextComponent(rts_battles.IsCommanderBlock('isCommander'))
RTS_PERSONAL_STATS_BLOCK.addNextComponent(rts_battles.EfficiencyTitle('efficiencyTitle'))
RTS_PERSONAL_STATS_BLOCK.addNextComponent(rts_battles.SupplyTotalEfficiencyDetailsHeader(_TOTAL_EFFICIENCY_HEADER_META, 'supplyEfficiencyHeader'))
RTS_PERSONAL_STATS_BLOCK.addNextComponent(rts_battles.RTSSpecialCurrencyDetailsBlock(base.ListMeta(), 'specialCurrencyData'))
RTS_PERSONAL_STATS_BLOCK.addNextComponent(rts_battles.CanBeFadedFlag('canBeFaded'))
RTS_PERSONAL_STATS_BLOCK.addNextComponent(rts_battles.RTS1x7CurrencyBalanceChange('rts1x7CurrencyStr'))
RTS_PERSONAL_STATS_BLOCK.addNextComponent(rts_battles.RTS1x1CurrencyBalanceChange('rts1x1CurrencyStr'))
RTS_TANKMAN_VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shots', 0, 'shots'),
 ('hits', style.SlashedValuesBlock('hits'), 'hits'),
 ('explosionHits', 0, 'explosionHits'),
 ('damageDealt', 0, 'damageDealt'),
 ('sniperDamageDealt', 0, 'sniperDamageDealt'),
 ('directHitsReceived', 0, 'directHitsReceived'),
 ('piercingsReceived', 0, 'piercingsReceived'),
 ('noDamageDirectHitsReceived', 0, 'noDamageDirectHitsReceived'),
 ('explosionHitsReceived', 0, 'explosionHitsReceived'),
 ('damageBlockedByArmor', 0, 'damageBlockedByArmor'),
 ('teamHitsDamage', style.RedSlashedValuesBlock('teamHitsDamage'), 'teamHitsDamage'),
 ('spottedStrategistItems', 0, 'spotted'),
 ('damagedKilled', style.SlashedValuesBlock('damagedKilled'), 'damagedKilled'),
 ('spottedSupplies', 0, 'spottedSupplies'),
 ('damagedKilledSupplies', style.SlashedValuesBlock('damagedKilledSupplies'), 'damagedKilledSupplies'),
 ('damageAssisted', 0, 'damageAssisted'),
 ('tankmanDamageToSupplies', 0, 'tankmanDamageToSupplies'),
 ('supplyDamageToTankman', 0, 'supplyDamageToTankman'),
 ('stunDuration', 0.0, 'stunDuration'),
 ('damageAssistedStun', 0, 'damageAssistedStun'),
 ('stunNum', 0, 'stunNum'),
 ('capturePointsVal', style.SlashedValuesBlock('capturePointsVal'), 'capturePoints'),
 ('mileage', style.MetersToKillometersItem('mileage'), 'mileage')))
RTS_TANKMAN_VEHICLE_STATS_BLOCK_VO_META.bind(rts_battles.RTSVehicleStatValuesBlock)
RTS1x7_TANKMAN_VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shotsByTanksSupplies', style.SlashedValuesBlock('shotsByTanksSupplies'), 'shotsByTanksSupplies'),
 ('hitsByTanks', style.SlashedValuesBlock('hitsByTanks'), 'hitsByTanks'),
 ('hitsBySupplies', style.SlashedValuesBlock('hitsBySupplies'), 'hitsBySupplies'),
 ('explosionHits', style.SlashedValuesBlock('explosionHits'), 'explosionHits'),
 ('damageDealtByTanksSupplies', style.SlashedValuesBlock('damageDealtByTanksSupplies'), 'damageDealtByTanksSupplies'),
 ('sniperDamageDealt', style.SlashedValuesBlock('sniperDamageDealt'), 'sniperDamageDealt'),
 ('directHitsReceived', 0, 'directHitsReceived'),
 ('piercingsReceived', 0, 'piercingsReceived'),
 ('noDamageDirectHitsReceived', 0, 'noDamageDirectHitsReceived'),
 ('explosionHitsReceived', 0, 'explosionHitsReceived'),
 ('damageBlockedByTanksSupplies', style.SlashedValuesBlock('damageBlockedByTanksSupplies'), 'damageBlockedByTanksSupplies'),
 ('teamHitsDamage', style.RedSlashedValuesBlock('teamHitsDamage'), 'teamHitsDamage'),
 ('spottedStrategistItems', 0, 'spotted'),
 ('damagedKilled', style.SlashedValuesBlock('damagedKilled'), 'damagedKilled'),
 ('damageAssisted', 0, 'damageAssisted'),
 ('stunDuration', 0.0, 'stunDuration'),
 ('damageAssistedStun', 0, 'damageAssistedStun'),
 ('stunNum', 0, 'stunNum'),
 ('capturePointsVal', style.SlashedValuesBlock('capturePointsVal'), 'capturePoints'),
 ('mileage', style.MetersToKillometersItem('mileage'), 'mileage')))
RTS1x7_TANKMAN_VEHICLE_STATS_BLOCK_VO_META.bind(rts_battles.RTS1x7VehicleStatValuesBlock)
RTS1x1_VEHICLE_STATS_BLOCK_VO_META = base.PropertyMeta((('shotsByTanksSupplies', style.SlashedValuesBlock('shotsByTanksSupplies'), 'shotsByTanksSupplies'),
 ('hitsByTanks', style.SlashedValuesBlock('hitsByTanks'), 'hitsByTanks'),
 ('hitsBySupplies', style.SlashedValuesBlock('hitsBySupplies'), 'hitsBySupplies'),
 ('explosionHits', style.SlashedValuesBlock('explosionHits'), 'explosionHits'),
 ('damageDealtByTanksSupplies', style.SlashedValuesBlock('damageDealtByTanksSupplies'), 'damageDealtByTanksSupplies'),
 ('sniperDamageDealt', style.SlashedValuesBlock('sniperDamageDealt'), 'sniperDamageDealt'),
 ('directHitsReceived', 0, 'directHitsReceived'),
 ('piercingsReceived', 0, 'piercingsReceived'),
 ('noDamageDirectHitsReceived', 0, 'noDamageDirectHitsReceived'),
 ('explosionHitsReceived', 0, 'explosionHitsReceived'),
 ('damageBlockedByTanksSupplies', style.SlashedValuesBlock('damageBlockedByTanksSupplies'), 'damageBlockedByTanksSupplies'),
 ('teamHitsDamage', style.RedSlashedValuesBlock('teamHitsDamage'), 'teamHitsDamage'),
 ('spottedStrategistItems', 0, 'spotted'),
 ('damagedKilled', style.SlashedValuesBlock('damagedKilled'), 'damagedKilled'),
 ('spottedSupplies', 0, 'spottedSupplies'),
 ('damagedKilledSupplies', style.SlashedValuesBlock('damagedKilledSupplies'), 'damagedKilledSupplies'),
 ('damageAssisted', 0, 'damageAssisted'),
 ('tankmanDamageToSupplies', 0, 'tankmanDamageToSupplies'),
 ('supplyDamageToTankman', 0, 'supplyDamageToTankman'),
 ('stunDuration', 0.0, 'stunDuration'),
 ('damageAssistedStun', 0, 'damageAssistedStun'),
 ('stunNum', 0, 'stunNum'),
 ('capturePointsVal', style.SlashedValuesBlock('capturePointsVal'), 'capturePoints'),
 ('mileage', style.MetersToKillometersItem('mileage'), 'mileage')))
RTS1x1_VEHICLE_STATS_BLOCK_VO_META.bind(rts_battles.RTS1x1VehicleStatValuesBlock)
RTS_COMMANDER_ALL_VEHICLES_STATS_BLOCK_VO_META = base.PropertyMeta((('shots', 0, 'shots'),
 ('hits', style.SlashedValuesBlock('hits'), 'hits'),
 ('explosionHits', 0, 'explosionHits'),
 ('damageDealt', 0, 'damageDealt'),
 ('sniperDamageDealt', 0, 'sniperDamageDealt'),
 ('directHitsReceived', 0, 'directHitsReceived'),
 ('piercingsReceived', 0, 'piercingsReceived'),
 ('noDamageDirectHitsReceived', 0, 'noDamageDirectHitsReceived'),
 ('explosionHitsReceived', 0, 'explosionHitsReceived'),
 ('damageBlockedByArmor', 0, 'damageBlockedByArmor'),
 ('spotted', 0, 'spotted'),
 ('damagedKilled', style.SlashedValuesBlock('damagedKilled'), 'damagedKilled'),
 ('damageAssisted', 0, 'damageAssisted'),
 ('commanderSupplyDamage', 0, 'commanderSupplyDamage'),
 ('damageToCommanderSupplies', 0, 'damageToCommanderSupplies'),
 ('stunDuration', 0.0, 'stunDuration'),
 ('damageAssistedStun', 0, 'damageAssistedStun'),
 ('stunNum', 0, 'stunNum'),
 ('capturePointsVal', style.SlashedValuesBlock('capturePointsVal'), 'capturePoints'),
 ('mileage', style.MetersToKillometersItem('mileage'), 'mileage')))
RTS_COMMANDER_ALL_VEHICLES_STATS_BLOCK_VO_META.bind(rts_battles.RTSCommanderAllVehiclesStatValuesBlock)
RTS_SUPPLY_STATS_BLOCK_VO_META = base.PropertyMeta((('shotsBySupplies', 0, 'shotsBySupplies'),
 ('hits', style.SlashedValuesBlock('hits'), 'hits'),
 ('damageDealtBySupplies', 0, 'damageDealtBySupplies'),
 ('sniperDamageDealtBySupplies', 0, 'sniperDamageDealtBySupplies'),
 ('directHitsReceivedBySupplies', 0, 'directHitsReceivedBySupplies'),
 ('piercingsReceivedBySupplies', 0, 'piercingsReceivedBySupplies'),
 ('noDamageDirectHitsReceivedBySupplies', 0, 'noDamageDirectHitsReceivedBySupplies'),
 ('spottedTanksBySupplies', 0, 'spottedTanksBySupplies'),
 ('damagedKilledTanksBySupplies', style.SlashedValuesBlock('damagedKilledTanksBySupplies'), 'damagedKilledTanksBySupplies')))
RTS_SUPPLY_STATS_BLOCK_VO_META.bind(rts_battles.RTSSupplyStatValuesBlock)
RTS_BARRICADES_SUPPLY_STATS_BLOCK_VO_META = base.PropertyMeta((('totalDamagedByBarricades', 0, 'totalDamagedByBarricades'), ('killedTanksByBarricades', 0, 'killedTanksByBarricades')))
RTS_BARRICADES_SUPPLY_STATS_BLOCK_VO_META.bind(rts_battles.RTSBarricadesSupplyStatValuesBlock)
RTS_WATCHTOWER_SUPPLY_STATS_BLOCK_VO_META = base.PropertyMeta((('spottedEnemiesByWatchtowers', 0, 'spottedEnemiesByWatchtowers'), ('damagedByWatchtowers', 0, 'damagedByWatchtowers')))
RTS_WATCHTOWER_SUPPLY_STATS_BLOCK_VO_META.bind(rts_battles.RTSWatchTowerSupplyStatValuesBlock)
RTS_VEHICLE_TEAM_ITEM_VO_META = regular.TEAM_ITEM_VO_META.replace(('statValues', rts_battles.AllTankmansVehicleStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'))
RTS_VEHICLE_TEAM_ITEM_VO_META.bind(rts_battles.RTSVehicleStatsBlock)
RTS_SUPPLY_TEAM_ITEM_VO_META = regular.TEAM_ITEM_VO_META.replace(('statValues', rts_battles.RTSAllSupplyStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'))
RTS_SUPPLY_TEAM_ITEM_VO_META.bind(rts_battles.RTSSupplyStatsBlock)
RTS_TEAMS_STATS_BLOCK = rts_battles.RTSTwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
RTS_TEAMS_STATS_BLOCK.addNextComponent(rts_battles.RTSAllyTeamStatsBlock(meta=base.ListMeta(), field='team1'))
RTS_TEAMS_STATS_BLOCK.addNextComponent(rts_battles.RTSEnemyTeamStatsBlock(meta=base.ListMeta(), field='team2'))
RTS_COMMANDER_VEH_DATA = rts_battles.RTSCommanderUserVehicleStatsBlock(field='enemyCommander')

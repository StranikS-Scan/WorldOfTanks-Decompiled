# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/halloween_battles.py
from gui.battle_results.components import base
from gui.battle_results.components import common
from gui.battle_results.components import details
from gui.battle_results.components import personal
from gui.battle_results.components import shared
from gui.battle_results.components import style
from gui.battle_results.components import vehicles
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.battle_results.templates import regular
from helpers import i18n
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
HALLOWEEN_PERSONAL_STATS_BLOCK = base.StatsBlock(regular._PERSONAL_VO_META, 'personal')
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(0, personal.TotalEfficiencyDetailsHeader(regular._TOTAL_EFFICIENCY_HEADER_META, 'efficiencyHeader', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(1, personal.TotalEfficiencyDetailsBlock(base.ListMeta(), 'details', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(2, regular._PERSONAL_ACHIEVEMENTS_BLOCK)
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(3, personal.PremiumAccountFlag('isPremium'))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(4, personal.CanUpgradeToPremiumFlag('hasGetPremBtn'))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(5, personal.PremiumBuyBlock(field='getPremVO'))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(6, details.GainCreditsInBattleItem('creditsStr'))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(7, details.GainXPInBattleItem('xpStr'))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(8, details.BaseCreditsBlock(base.ListMeta(), 'creditsNoPremValues', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(9, details.PremiumCreditsBlock(base.ListMeta(), 'creditsPremValues', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(10, details.TotalMoneyDetailsBlock(base.ListMeta(), 'creditsData', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(11, details.XPTitleBlock(base.ListMeta(), 'xpTitleStrings', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(12, details.BaseXPBlock(base.ListMeta(), 'xpNoPremValues', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(13, details.PremiumXPBlock(base.ListMeta(), 'xpPremValues', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(14, details.TotalXPDetailsBlock(base.ListMeta(), 'xpData', _RECORD.PERSONAL))
HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(15, vehicles.PersonalVehiclesHalloweenStatsBlock(base.ListMeta(), 'statValues', _RECORD.PERSONAL))
(HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(16, personal.StunDataFlag('isStunDataEnabled')),)
(HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(17, details.GainCrystalInBattleItem('crystalStr')),)
(HALLOWEEN_PERSONAL_STATS_BLOCK.addComponent(18, details.TotalCrystalDetailsBlock(base.ListMeta(), 'crystalData', _RECORD.PERSONAL)),)
HALLOWEEN_VEHICLE_STATS_BLOCK_VO_META = regular.VEHICLE_STATS_BLOCK_VO_META.merge(('shots', 0, 'shots'), ('hits', style.SlashedValuesBlock('hits'), 'hits'), ('secondaryTurretHits', style.SlashedValuesBlock('secondaryTurretHits'), 'secondaryTurretHits'), ('explosionHits', 0, 'explosionHits'), ('damageDealt', 0, 'damageDealt'), ('multiTurretDamageDealt', style.SlashedValuesBlock('multiTurretDamageDealt'), 'multiTurretDamageDealt'), ('bossDamageDealt', 0, 'bossDamageDealt'), ('directHitsReceived', 0, 'directHitsReceived'), ('piercingsReceived', 0, 'piercingsReceived'), ('noDamageDirectHitsReceived', 0, 'noDamageDirectHitsReceived'), ('explosionHitsReceived', 0, 'explosionHitsReceived'), ('damageBlockedByArmor', 0, 'damageBlockedByArmor'), ('bossDamageTurretHazardReceived', style.SlashedValuesBlock('bossDamageTurretHazardReceived'), 'bossDamageTurretHazardReceived'), ('damagedKilled', style.SlashedValuesBlock('damagedKilled'), 'damagedKilled'), ('damageAssisted', 0, 'damageAssisted'), ('healthPackStats', style.SlashedValuesBlock('healthPackStats'), 'healthPackStats'))
HALLOWEEN_VEHICLE_STATS_BLOCK_VO_META.bind(vehicles.HalloweenVehicleStatValuesBlock)
HALLOWEEN_TEAM_ITEM_VO_META = base.PropertyMeta((('achievements', shared.AchievementsBlock(base.ListMeta(), 'achievements'), 'achievements'),
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
 ('statValues', vehicles.AllHalloweenVehicleStatValuesBlock(base.ListMeta(), 'statValues'), 'statValues'),
 ('resourceCount', 0, 'fortResource'),
 ('rank', 0, 'rank'),
 ('rankIcon', '', 'rankIcon'),
 ('badge', 0, 'badge'),
 ('badgeIcon', '', 'badgeIcon')))
HALLOWEEN_TEAM_ITEM_VO_META.bind(vehicles.HalloweenVehicleStatsBlock)
HALLOWEEN_TEAMS_STATS_BLOCK = vehicles.TwoTeamsStatsBlock(regular.TEAMS_VO_META.clone(), '', _RECORD.VEHICLES)
HALLOWEEN_TEAMS_STATS_BLOCK.addNextComponent(vehicles.HalloweenTeamStatsBlock(meta=base.ListMeta(), field='team1'))
HALLOWEEN_TEAMS_STATS_BLOCK.addNextComponent(vehicles.HalloweenTeamStatsBlock(meta=base.ListMeta(), field='team2'))

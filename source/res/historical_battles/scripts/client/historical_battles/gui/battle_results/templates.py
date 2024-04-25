# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_results/templates.py
from gui.battle_results.templates import regular
from gui.battle_results.components import base
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from historical_battles.gui.battle_results import components as hb
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_result_view_model import FairplayStatus
HB_TOTAL_VO_META = base.DictMeta({'common': {},
 'details': {},
 'isWin': False,
 'battleResultType': '',
 'finishReason': '',
 'deathReason': '',
 'duration': 0,
 'players': [],
 'tankIcon': '',
 'damageDone': 0,
 'kills': 0,
 'damageBlocked': 0,
 'damageAssisted': 0,
 'killerInfo': {},
 'isKilled': False,
 'fairplayStatus': FairplayStatus.PLAYER,
 'map': {},
 'playerName': '',
 'playerClan': '',
 'tankName': '',
 'isHeroVehicle': False,
 'tankType': '',
 'frontman': {},
 'frontCoupon': '',
 'earnings': {},
 'frontName': '',
 'arenaPhases': {},
 'roleAbility': {}})
_HB_EARNINGS_VO_META = base.DictMeta({'amount': 0,
 'type': ''})
_HB_FRONTMAN_VO_META = base.DictMeta({'id': 0,
 'role': '',
 'name': ''})
_HB_MAP_INFO_VO_META = base.DictMeta({'name': '',
 'id': ''})
_HB_KILLER_INFO_VO_META = base.DictMeta({'name': '',
 'type': ''})
_HB_ARENA_PHASES_VO_META = base.DictMeta({'current': 0,
 'total': 0})
_HB_ROLE_ABILITY_VO_META = base.DictMeta({'obtained': False,
 'name': '',
 'icon': '',
 'id': 0})
_HB_PLAYER_INFO_VO_META_TUPLE = regular.TEAM_ITEM_VO_META_TUPLE + (('damageBlocked', 0, 'damageBlockedByArmor'),
 ('damageAssisted', 0, 'damageAssisted'),
 ('tankType', 0, 'tankType'),
 ('role', None, 'role'),
 ('badgeID', 0, 'badgeID'))
_HB_PLAYER_INFO_VO_META = base.PropertyMeta(_HB_PLAYER_INFO_VO_META_TUPLE)
_HB_PLAYER_INFO_VO_META.bind(hb.EventVehicleStatsBlock)
HB_BATTLE_COMMON_STATS_BLOCK = regular.REGULAR_COMMON_STATS_BLOCK.clone()
HB_TOTAL_RESULTS_BLOCK = base.StatsBlock(HB_TOTAL_VO_META, 'victoryData')
_components = (HB_BATTLE_COMMON_STATS_BLOCK,
 hb.HBTeamStatsBlock(base.ListMeta(), 'players', _RECORD.VEHICLES),
 hb.CommonStatsBlock(base.DictMeta(), 'details', _RECORD.PERSONAL),
 hb.IsWinItem('isWin', _RECORD.PERSONAL),
 hb.BattleResultTypeItem('battleResultType', _RECORD.PERSONAL),
 hb.FinishReasonItem('finishReason', _RECORD.COMMON),
 hb.DeathReason('deathReason', _RECORD.PERSONAL),
 hb.ArenaDurationItem('duration', _RECORD.COMMON),
 hb.DamageItem('damageDone', _RECORD.PERSONAL),
 hb.KillsItem('kills', _RECORD.PERSONAL),
 hb.DamageAssistedItem('damageAssisted', _RECORD.PERSONAL),
 hb.DamageBlockedItem('damageBlocked', _RECORD.PERSONAL),
 hb.KillerVehicleBlock(_HB_KILLER_INFO_VO_META, 'killerInfo', _RECORD.PERSONAL),
 hb.IsKilledItem('isKilled', _RECORD.PERSONAL),
 hb.FairplayItem('fairplayStatus', _RECORD.PERSONAL),
 hb.MapInfoBlock(_HB_MAP_INFO_VO_META, 'map', _RECORD.PERSONAL),
 hb.PlayerNameItem('playerName', _RECORD.PERSONAL),
 hb.PlayerClanItem('playerClan', _RECORD.PERSONAL),
 hb.TankNameItem('tankName', _RECORD.PERSONAL),
 hb.HeroVehicleItem('isHeroVehicle', _RECORD.PERSONAL),
 hb.TankTypeItem('tankType', _RECORD.PERSONAL),
 hb.FrontCouponUsedItem('frontCoupon', _RECORD.PERSONAL),
 hb.EarningsBlock(_HB_EARNINGS_VO_META, 'earnings'),
 hb.FrontManBlock(_HB_FRONTMAN_VO_META, 'frontman'),
 hb.FrontItem('frontName', _RECORD.PERSONAL),
 hb.ArenaPhasesBlock(_HB_ARENA_PHASES_VO_META, 'arenaPhases', _RECORD.PERSONAL),
 hb.RoleAbilityBlock(_HB_ROLE_ABILITY_VO_META, 'roleAbility', _RECORD.PERSONAL))
for component in _components:
    HB_TOTAL_RESULTS_BLOCK.addNextComponent(component)

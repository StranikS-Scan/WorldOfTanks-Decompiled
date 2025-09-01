# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/team/stats_params_settings.py
from collections import namedtuple
from gui.battle_results.pbs_helpers.team_stats_helpers import getStatsParamValue, getMileageValue, isPersonalBattleResult, isNotPersonalBattleResult, hasStunEfficiency
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.simple_stats_parameter_model import RegularParamType, ValueType
_Parameter = namedtuple('_Parameter', ('path', 'stringId', 'fields', 'valueType', 'conditions', 'extractor', 'details'))
_STR_PATH = R.strings.battle_results.team.stats.parameter
REGULAR_PARAMETERS = {RegularParamType.SHOTS: _Parameter(path=_STR_PATH.shots, stringId='shots', fields=('shots',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=(RegularParamType.HITS, RegularParamType.EXPLOSIONHITS)),
 RegularParamType.HITS: _Parameter(path=_STR_PATH.hits, stringId='hits', fields=('directEnemyHits', 'piercingEnemyHits'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.EXPLOSIONHITS: _Parameter(path=_STR_PATH.explosionHits, stringId='explosionHits', fields=('explosionHits',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEDEALT: _Parameter(path=_STR_PATH.damageDealt, stringId='damageDealt', fields=('damageDealt',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=(RegularParamType.SNIPERDAMAGEDEALT,)),
 RegularParamType.SNIPERDAMAGEDEALT: _Parameter(path=_STR_PATH.sniperDamageDealt, stringId='sniperDamageDealt', fields=('sniperDamageDealt',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DIRECTHITSRECEIVED: _Parameter(path=_STR_PATH.directHitsReceived, stringId='directHitsReceived', fields=('directHitsReceived',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=(RegularParamType.PIERCINGSRECEIVED, RegularParamType.NODAMAGEDIRECTHITSRECEIVED)),
 RegularParamType.PIERCINGSRECEIVED: _Parameter(path=_STR_PATH.piercingsReceived, stringId='piercingsReceived', fields=('piercingsReceived',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.NODAMAGEDIRECTHITSRECEIVED: _Parameter(path=_STR_PATH.noDamageDirectHitsReceived, stringId='noDamageDirectHitsReceived', fields=('noDamageDirectHitsReceived',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.EXPLOSIONHITSRECEIVED: _Parameter(path=_STR_PATH.explosionHitsReceived, stringId='explosionHitsReceived', fields=('explosionHitsReceived',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEBLOCKEDBYARMOR: _Parameter(path=_STR_PATH.damageBlockedByArmor, stringId='damageBlockedByArmor', fields=('damageBlockedByArmor',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.TEAMHITSDAMAGE: _Parameter(path=_STR_PATH.teamHitsDamage, stringId='teamHitsDamage', fields=('tkills', 'tdamageDealt'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.SPOTTED: _Parameter(path=_STR_PATH.spotted, stringId='spotted', fields=('spotted',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEDKILLED: _Parameter(path=_STR_PATH.damagedKilled, stringId='damagedKilled', fields=('damaged', 'kills'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEASSISTED: _Parameter(path=_STR_PATH.damageAssisted, stringId='damageAssisted', fields=('damageAssisted',), valueType=ValueType.INTEGER, conditions=(isNotPersonalBattleResult,), extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEASSISTEDSELF: _Parameter(path=_STR_PATH.damageAssistedSelf, stringId='damageAssistedSelf', fields=('damageAssisted',), valueType=ValueType.INTEGER, conditions=(isPersonalBattleResult,), extractor=getStatsParamValue, details=()),
 RegularParamType.STUNDURATION: _Parameter(path=_STR_PATH.stunDuration, stringId='stunDuration', fields=('stunDuration',), valueType=ValueType.FLOAT, conditions=(hasStunEfficiency,), extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEASSISTEDSTUN: _Parameter(path=_STR_PATH.damageAssistedStun, stringId='damageAssistedStun', fields=('damageAssistedStun',), valueType=ValueType.INTEGER, conditions=(hasStunEfficiency, isNotPersonalBattleResult), extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEASSISTEDSTUNSELF: _Parameter(path=_STR_PATH.damageAssistedStunSelf, stringId='damageAssistedStunSelf', fields=('damageAssistedStun',), valueType=ValueType.INTEGER, conditions=(hasStunEfficiency, isPersonalBattleResult), extractor=getStatsParamValue, details=()),
 RegularParamType.STUNNUM: _Parameter(path=_STR_PATH.stunNum, stringId='stunNum', fields=('stunNum',), valueType=ValueType.INTEGER, conditions=(hasStunEfficiency,), extractor=getStatsParamValue, details=()),
 RegularParamType.CAPTUREPOINTSVAL: _Parameter(path=_STR_PATH.capturePointsVal, stringId='capturePointsVal', fields=('capturePoints', 'droppedCapturePoints'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.MILEAGE: _Parameter(path=_STR_PATH.mileage, stringId='mileage', fields=('mileage',), valueType=ValueType.FLOAT, conditions=None, extractor=getMileageValue, details=())}

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/team/stats_params_settings.py
from collections import namedtuple
from gui.battle_results.presenters.packers.team.stats_params_getters import getStatsParamValue, getMileageValue, isPersonalBattleResult, isNotPersonalBattleResult, hasStunEfficiency
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.simple_stats_parameter_model import RegularParamType, ValueType
_Parameter = namedtuple('_Parameter', ('stringId', 'fields', 'valueType', 'conditions', 'extractor', 'details'))
_STR_PATH = R.strings.battle_results.team.stats.parameter
REGULAR_PARAMETERS = {RegularParamType.SHOTS: _Parameter(stringId=_STR_PATH.shots, fields=('shots',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=(RegularParamType.HITS, RegularParamType.EXPLOSIONHITS)),
 RegularParamType.HITS: _Parameter(stringId=_STR_PATH.hits, fields=('directEnemyHits', 'piercingEnemyHits'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.EXPLOSIONHITS: _Parameter(stringId=_STR_PATH.explosionHits, fields=('explosionHits',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEDEALT: _Parameter(stringId=_STR_PATH.damageDealt, fields=('damageDealt',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=(RegularParamType.SNIPERDAMAGEDEALT,)),
 RegularParamType.SNIPERDAMAGEDEALT: _Parameter(stringId=_STR_PATH.sniperDamageDealt, fields=('sniperDamageDealt',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DIRECTHITSRECEIVED: _Parameter(stringId=_STR_PATH.directHitsReceived, fields=('directHitsReceived',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=(RegularParamType.PIERCINGSRECEIVED, RegularParamType.NODAMAGEDIRECTHITSRECEIVED)),
 RegularParamType.PIERCINGSRECEIVED: _Parameter(stringId=_STR_PATH.piercingsReceived, fields=('piercingsReceived',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.NODAMAGEDIRECTHITSRECEIVED: _Parameter(stringId=_STR_PATH.noDamageDirectHitsReceived, fields=('noDamageDirectHitsReceived',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.EXPLOSIONHITSRECEIVED: _Parameter(stringId=_STR_PATH.explosionHitsReceived, fields=('explosionHitsReceived',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEBLOCKEDBYARMOR: _Parameter(stringId=_STR_PATH.damageBlockedByArmor, fields=('damageBlockedByArmor',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.TEAMHITSDAMAGE: _Parameter(stringId=_STR_PATH.teamHitsDamage, fields=('tkills', 'tdamageDealt'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.SPOTTED: _Parameter(stringId=_STR_PATH.spotted, fields=('spotted',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEDKILLED: _Parameter(stringId=_STR_PATH.damagedKilled, fields=('damaged', 'kills'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEASSISTED: _Parameter(stringId=_STR_PATH.damageAssisted, fields=('damageAssisted',), valueType=ValueType.INTEGER, conditions=(isNotPersonalBattleResult,), extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEASSISTEDSELF: _Parameter(stringId=_STR_PATH.damageAssistedSelf, fields=('damageAssisted',), valueType=ValueType.INTEGER, conditions=(isPersonalBattleResult,), extractor=getStatsParamValue, details=()),
 RegularParamType.STUNDURATION: _Parameter(stringId=_STR_PATH.stunDuration, fields=('stunDuration',), valueType=ValueType.FLOAT, conditions=(hasStunEfficiency,), extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEASSISTEDSTUN: _Parameter(stringId=_STR_PATH.damageAssistedStun, fields=('damageAssistedStun',), valueType=ValueType.INTEGER, conditions=(hasStunEfficiency, isNotPersonalBattleResult), extractor=getStatsParamValue, details=()),
 RegularParamType.DAMAGEASSISTEDSTUNSELF: _Parameter(stringId=_STR_PATH.damageAssistedStunSelf, fields=('damageAssistedStun',), valueType=ValueType.INTEGER, conditions=(hasStunEfficiency, isPersonalBattleResult), extractor=getStatsParamValue, details=()),
 RegularParamType.STUNNUM: _Parameter(stringId=_STR_PATH.stunNum, fields=('stunNum',), valueType=ValueType.INTEGER, conditions=(hasStunEfficiency,), extractor=getStatsParamValue, details=()),
 RegularParamType.CAPTUREPOINTSVAL: _Parameter(stringId=_STR_PATH.capturePointsVal, fields=('capturePoints', 'droppedCapturePoints'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 RegularParamType.MILEAGE: _Parameter(stringId=_STR_PATH.mileage, fields=('mileage',), valueType=ValueType.FLOAT, conditions=None, extractor=getMileageValue, details=())}

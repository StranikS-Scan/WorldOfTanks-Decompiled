# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/comp7_team_stats_params_settings.py
from __future__ import absolute_import
import typing
from ValueReplay import BattleResults
from gui.battle_results.presenters.packers.team.stats_params_settings import _Parameter
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_detailed_stats_parameter_model import Comp7ParamType
from constants import EntityCaptured
from gui.battle_results.pbs_helpers.team_stats_helpers import getStatsParamValue
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.simple_stats_parameter_model import ValueType, RegularParamType
if typing.TYPE_CHECKING:
    from comp7_core.gui.battle_results.reusable.shared import Comp7CoreVehicleSummarizeInfo

def getPoiCapturable(summarizeInfo, fields, _):
    return (getattr(summarizeInfo, field).get(EntityCaptured.POI_CAPTURABLE, 0) for field in fields)


COMP7_PARAMETERS_UPDATE = {RegularParamType.DAMAGEDEALT: _Parameter(path=R.strings.battle_results.team.stats.parameter.damageDealt, stringId='damageDealt', fields=('damageDealt',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=(RegularParamType.SNIPERDAMAGEDEALT, RegularParamType.ARTILLERYSTRIKE, Comp7ParamType.DAMAGEDEALTBYSKILLS)),
 Comp7ParamType.DAMAGEDEALTBYSKILLS: _Parameter(path=R.strings.battle_results.team.stats.labels_damageDealtBySkills, stringId='damageDealtBySkills', fields=('equipmentDamageDealt',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 Comp7ParamType.HEALED: _Parameter(path=R.strings.battle_results.team.stats.labels_healed, stringId='healed', fields=('healthRepair', 'alliedHealthRepair'), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=()),
 Comp7ParamType.CAPTUREDPOINTSOFINTEREST: _Parameter(path=R.strings.battle_results.team.stats.labels_capturedPointsOfInterest, stringId='capturedPointsOfInterest', fields=('entityCaptured',), valueType=ValueType.INTEGER, conditions=None, extractor=getPoiCapturable, details=()),
 Comp7ParamType.ROLESKILLUSED: _Parameter(path=R.strings.battle_results.team.stats.labels_roleSkillUsed, stringId='roleSkillUsed', fields=('roleSkillUsed',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=())}

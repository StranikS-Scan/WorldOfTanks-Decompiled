# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/team/statistics_packer.py
from copy import deepcopy
import typing
from gui.battle_results.presenters.packers.team.stats_params_settings import REGULAR_PARAMETERS
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_stats_parameter_model import DetailedStatsParameterModel
from gui.battle_results.presenters.packers.interfaces import IStatisticsPacker
from gui.impl.gen.view_models.views.lobby.battle_results.simple_stats_parameter_model import SimpleStatsParameterModel, RegularParamType
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo

class Statistics(IStatisticsPacker):
    __ALL_PARAMETERS = {}
    _STATS_PARAMETERS = (RegularParamType.SHOTS,
     RegularParamType.DAMAGEDEALT,
     RegularParamType.DIRECTHITSRECEIVED,
     RegularParamType.EXPLOSIONHITSRECEIVED,
     RegularParamType.DAMAGEBLOCKEDBYARMOR,
     RegularParamType.TEAMHITSDAMAGE,
     RegularParamType.SPOTTED,
     RegularParamType.DAMAGEDKILLED,
     RegularParamType.DAMAGEASSISTED,
     RegularParamType.DAMAGEASSISTEDSELF,
     RegularParamType.STUNDURATION,
     RegularParamType.DAMAGEASSISTEDSTUN,
     RegularParamType.DAMAGEASSISTEDSTUNSELF,
     RegularParamType.STUNNUM,
     RegularParamType.CAPTUREPOINTSVAL,
     RegularParamType.MILEAGE)

    @classmethod
    def packModel(cls, model, info, battleResults):
        model.clear()
        for paramType in cls._STATS_PARAMETERS:
            paramSettings = cls._getAllParameters().get(paramType)
            if paramSettings is None:
                raise SoftException('Missing parameter settings for parameter {}'.format(paramType.value))
            conditionCheckers = paramSettings.conditions
            if conditionCheckers and not all((func(info, battleResults) for func in conditionCheckers)):
                continue
            paramModel = DetailedStatsParameterModel()
            cls.__packParameter(paramModel, paramSettings, info, battleResults)
            if paramSettings.details:
                cls.__packDetails(paramModel.getDetails(), paramType, info, battleResults)
            model.addViewModel(paramModel)

        model.invalidate()
        return

    @classmethod
    def _getAllParameters(cls):
        if not cls.__ALL_PARAMETERS:
            cls.__ALL_PARAMETERS = deepcopy(REGULAR_PARAMETERS)
        return cls.__ALL_PARAMETERS

    @classmethod
    def __packDetails(cls, detailsModel, paramType, info, battleResults):
        details = cls._getAllParameters()[paramType].details
        detailsModel.clear()
        for detailedParamType in details:
            paramSettings = cls._getAllParameters().get(detailedParamType)
            if paramSettings is None:
                raise SoftException('Missing parameter settings for parameter {}'.format(detailedParamType.value))
            paramModel = SimpleStatsParameterModel()
            cls.__packParameter(paramModel, paramSettings, info, battleResults)
            detailsModel.addViewModel(paramModel)

        detailsModel.invalidate()
        return

    @classmethod
    def __packParameter(cls, model, paramSettings, info, battleResults):
        model.setLabel(paramSettings.stringId())
        model.setParamValueType(paramSettings.valueType)
        cls.__packValue(model.getValue(), paramSettings.extractor(info, paramSettings.fields, battleResults))

    @classmethod
    def __packValue(cls, model, values):
        model.clear()
        for value in values:
            model.addReal(value)

        model.invalidate()

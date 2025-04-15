# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/personal_efficiency.py
import typing
from gui.battle_results.presenters.packers.interfaces import IBattleResultsPacker
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl.gen.view_models.views.lobby.battle_results.personal_efficiency_model import PersonalEfficiencyModel

class PersonalEfficiency(IBattleResultsPacker):
    __slots__ = ()
    _PARAMETERS = {}
    _DEFAULT_PARAMS = ()
    _VALUE_EXTRACTORS = {}
    _EFFICIENCY_ITEM_MODEL_CLS = PersonalEfficiencyModel

    @classmethod
    def packModel(cls, model, battleResults):
        model.clear()
        info = battleResults.reusable.getPersonalVehiclesInfo(battleResults.results[_RECORD.PERSONAL])
        parameters = cls._getParameterList(info.vehicle, battleResults)
        for parameter in parameters:
            parameterModel = cls._createParameterModel(parameter, info)
            model.addViewModel(parameterModel)

        model.invalidate()

    @classmethod
    def _createParameterModel(cls, parameter, vehicleInfo):
        efficiencyParameter = cls._EFFICIENCY_ITEM_MODEL_CLS()
        efficiencyParameter.setParamType(parameter)
        valueExtractor = cls._VALUE_EXTRACTORS.get(parameter, getattr)
        efficiencyParameter.setValue(valueExtractor(vehicleInfo, parameter))
        return efficiencyParameter

    @classmethod
    def _getParameterList(cls, vehicle, _):
        return cls._PARAMETERS.get(vehicle.type, cls._DEFAULT_PARAMS)

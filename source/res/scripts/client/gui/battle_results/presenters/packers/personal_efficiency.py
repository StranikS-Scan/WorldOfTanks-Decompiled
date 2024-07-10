# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/personal_efficiency.py
import typing
from gui.battle_results.presenters.packers.interfaces import IBattleResultsPacker
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl.gen.view_models.views.lobby.battle_results.personal_efficiency_model import PersonalEfficiencyModel, EfficiencyParameter

class PersonalEfficiency(IBattleResultsPacker):
    __slots__ = ()
    _PARAMETERS = {}
    _DEFAULT_PARAMS = ()

    @classmethod
    def packModel(cls, model, battleResults):
        model.clear()
        info = battleResults.reusable.getPersonalVehiclesInfo(battleResults.results[_RECORD.PERSONAL])
        parameters = cls._getParameterList(info.vehicle, battleResults)
        for parameter in parameters:
            personalEfficiency = PersonalEfficiencyModel()
            personalEfficiency.setParamType(parameter)
            personalEfficiency.setValue(getattr(info, parameter.value))
            model.addViewModel(personalEfficiency)

        model.invalidate()

    @classmethod
    def _getParameterList(cls, vehicle, _):
        return cls._PARAMETERS.get(vehicle.type, cls._DEFAULT_PARAMS)

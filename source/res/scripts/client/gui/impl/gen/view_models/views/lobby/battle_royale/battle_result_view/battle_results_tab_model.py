# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/battle_result_view/battle_results_tab_model.py
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.personal_results_model import PersonalResultsModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.battle_pass_progress import BattlePassProgress

class BattleResultsTabModel(PersonalResultsModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(BattleResultsTabModel, self).__init__(properties=properties, commands=commands)

    @property
    def battlePassProgress(self):
        return self._getViewModel(4)

    def getPlace(self):
        return self._getNumber(5)

    def setPlace(self, value):
        self._setNumber(5, value)

    def getHasPremium(self):
        return self._getBool(6)

    def setHasPremium(self, value):
        self._setBool(6, value)

    def getVehicleType(self):
        return self._getString(7)

    def setVehicleType(self, value):
        self._setString(7, value)

    def getVehicleName(self):
        return self._getString(8)

    def setVehicleName(self, value):
        self._setString(8, value)

    def getQuestCompleted(self):
        return self._getNumber(9)

    def setQuestCompleted(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(BattleResultsTabModel, self)._initialize()
        self._addViewModelProperty('battlePassProgress', BattlePassProgress())
        self._addNumberProperty('place', 0)
        self._addBoolProperty('hasPremium', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('questCompleted', 0)

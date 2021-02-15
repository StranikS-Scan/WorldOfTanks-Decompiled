# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/battle_result_view/battle_results_tab_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.personal_results_model import PersonalResultsModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.battle_pass_progress import BattlePassProgress

class BattleResultsTabModel(PersonalResultsModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(BattleResultsTabModel, self).__init__(properties=properties, commands=commands)

    @property
    def battlePassProgress(self):
        return self._getViewModel(3)

    def getPlace(self):
        return self._getNumber(4)

    def setPlace(self, value):
        self._setNumber(4, value)

    def getNationName(self):
        return self._getString(5)

    def setNationName(self, value):
        self._setString(5, value)

    def getVehicleName(self):
        return self._getString(6)

    def setVehicleName(self, value):
        self._setString(6, value)

    def getBonuses(self):
        return self._getArray(7)

    def setBonuses(self, value):
        self._setArray(7, value)

    def getAchievements(self):
        return self._getArray(8)

    def setAchievements(self, value):
        self._setArray(8, value)

    def getQuestCompleted(self):
        return self._getNumber(9)

    def setQuestCompleted(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(BattleResultsTabModel, self)._initialize()
        self._addViewModelProperty('battlePassProgress', BattlePassProgress())
        self._addNumberProperty('place', 0)
        self._addStringProperty('nationName', '')
        self._addStringProperty('vehicleName', '')
        self._addArrayProperty('bonuses', Array())
        self._addArrayProperty('achievements', Array())
        self._addNumberProperty('questCompleted', 0)

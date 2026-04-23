# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/battle_results/comp7_player_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_stats_efficiency_model import Comp7StatsEfficiencyModel
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_player_model import RandomPlayerModel

class Comp7PlayerModel(RandomPlayerModel):
    __slots__ = ()
    NO_PLATOON_SQUAD_INDEX = 0
    SUPER_PLATOON_SQUAD_INDEX = -1

    def __init__(self, properties=17, commands=0):
        super(Comp7PlayerModel, self).__init__(properties=properties, commands=commands)

    @property
    def efficiencyValues(self):
        return self._getViewModel(13)

    @staticmethod
    def getEfficiencyValuesType():
        return Comp7StatsEfficiencyModel

    def getIsQualification(self):
        return self._getBool(14)

    def setIsQualification(self, value):
        self._setBool(14, value)

    def getRank(self):
        return Rank(self._getNumber(15))

    def setRank(self, value):
        self._setNumber(15, value.value)

    def getDivision(self):
        return Division(self._getNumber(16))

    def setDivision(self, value):
        self._setNumber(16, value.value)

    def _initialize(self):
        super(Comp7PlayerModel, self)._initialize()
        self._addViewModelProperty('efficiencyValues', Comp7StatsEfficiencyModel())
        self._addBoolProperty('isQualification', False)
        self._addNumberProperty('rank')
        self._addNumberProperty('division')

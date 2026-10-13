# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/battle_result/player_results/personal_results_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.player_results.battle_reward_item_model import BattleRewardItemModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.player_results.stat_item_model import StatItemModel

class PersonalResultsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PersonalResultsModel, self).__init__(properties=properties, commands=commands)

    def getStatsList(self):
        return self._getArray(0)

    def setStatsList(self, value):
        self._setArray(0, value)

    @staticmethod
    def getStatsListType():
        return StatItemModel

    def getBattleRewardsList(self):
        return self._getArray(1)

    def setBattleRewardsList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBattleRewardsListType():
        return BattleRewardItemModel

    def _initialize(self):
        super(PersonalResultsModel, self)._initialize()
        self._addArrayProperty('statsList', Array())
        self._addArrayProperty('battleRewardsList', Array())

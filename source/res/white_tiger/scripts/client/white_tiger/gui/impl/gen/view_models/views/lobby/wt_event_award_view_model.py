# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_award_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class WtEventAwardViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(WtEventAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getStatus(self):
        return self._getString(1)

    def setStatus(self, value):
        self._setString(1, value)

    def getIsValuableReward(self):
        return self._getBool(2)

    def setIsValuableReward(self, value):
        self._setBool(2, value)

    def getIsPostBattle(self):
        return self._getBool(3)

    def setIsPostBattle(self, value):
        self._setBool(3, value)

    def getMainRewards(self):
        return self._getArray(4)

    def setMainRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getMainRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(WtEventAwardViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('status', '')
        self._addBoolProperty('isValuableReward', False)
        self._addBoolProperty('isPostBattle', False)
        self._addArrayProperty('mainRewards', Array())

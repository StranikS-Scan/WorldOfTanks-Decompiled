# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_guaranteed_reward_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.common.wt_guaranteed_reward_model import WtGuaranteedRewardModel

class WtGuaranteedRewardTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WtGuaranteedRewardTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def guaranteedReward(self):
        return self._getViewModel(0)

    @staticmethod
    def getGuaranteedRewardType():
        return WtGuaranteedRewardModel

    def getTanks(self):
        return self._getArray(1)

    def setTanks(self, value):
        self._setArray(1, value)

    @staticmethod
    def getTanksType():
        return unicode

    def _initialize(self):
        super(WtGuaranteedRewardTooltipViewModel, self)._initialize()
        self._addViewModelProperty('guaranteedReward', WtGuaranteedRewardModel())
        self._addArrayProperty('tanks', Array())

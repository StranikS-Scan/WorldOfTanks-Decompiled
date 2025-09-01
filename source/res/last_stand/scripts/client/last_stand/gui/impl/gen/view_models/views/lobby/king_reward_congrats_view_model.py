# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/king_reward_congrats_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class KingRewardCongratsViewModel(ViewModel):
    __slots__ = ('onClose', 'onToOutroClick')

    def __init__(self, properties=2, commands=2):
        super(KingRewardCongratsViewModel, self).__init__(properties=properties, commands=commands)

    def getIsTransition(self):
        return self._getBool(0)

    def setIsTransition(self, value):
        self._setBool(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(KingRewardCongratsViewModel, self)._initialize()
        self._addBoolProperty('isTransition', False)
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onToOutroClick = self._addCommand('onToOutroClick')

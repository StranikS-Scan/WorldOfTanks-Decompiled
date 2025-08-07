# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/regular_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class RegularRewardViewModel(ViewModel):
    __slots__ = ('onClose', 'onSetBlur')

    def __init__(self, properties=2, commands=2):
        super(RegularRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(0)

    def setBonuses(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBonusesType():
        return ItemBonusModel

    def getAnimationEnabled(self):
        return self._getBool(1)

    def setAnimationEnabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(RegularRewardViewModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
        self._addBoolProperty('animationEnabled', True)
        self.onClose = self._addCommand('onClose')
        self.onSetBlur = self._addCommand('onSetBlur')

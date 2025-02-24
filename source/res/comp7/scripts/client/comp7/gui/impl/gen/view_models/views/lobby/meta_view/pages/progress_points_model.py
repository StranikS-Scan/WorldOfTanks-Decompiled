# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/progress_points_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.comp7_bonus_model import Comp7BonusModel

class ProgressPointsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ProgressPointsModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return Comp7BonusModel

    def _initialize(self):
        super(ProgressPointsModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addArrayProperty('rewards', Array())

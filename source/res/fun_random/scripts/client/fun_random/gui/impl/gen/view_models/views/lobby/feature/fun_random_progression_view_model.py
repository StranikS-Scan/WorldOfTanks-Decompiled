# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_progression_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_infinite_progression_condition import FunRandomInfiniteProgressionCondition
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_condition import FunRandomProgressionCondition
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_stage import FunRandomProgressionStage
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_state import FunRandomProgressionState

class FunRandomProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onShowInfo', 'onOpenTierList')

    def __init__(self, properties=7, commands=3):
        super(FunRandomProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def state(self):
        return self._getViewModel(0)

    @staticmethod
    def getStateType():
        return FunRandomProgressionState

    @property
    def condition(self):
        return self._getViewModel(1)

    @staticmethod
    def getConditionType():
        return FunRandomProgressionCondition

    @property
    def infiniteCondition(self):
        return self._getViewModel(2)

    @staticmethod
    def getInfiniteConditionType():
        return FunRandomInfiniteProgressionCondition

    @property
    def infiniteStage(self):
        return self._getViewModel(3)

    @staticmethod
    def getInfiniteStageType():
        return FunRandomProgressionStage

    def getStages(self):
        return self._getArray(4)

    def setStages(self, value):
        self._setArray(4, value)

    @staticmethod
    def getStagesType():
        return FunRandomProgressionStage

    def getAssetsPointer(self):
        return self._getString(5)

    def setAssetsPointer(self, value):
        self._setString(5, value)

    def getIsFirstOpen(self):
        return self._getBool(6)

    def setIsFirstOpen(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(FunRandomProgressionViewModel, self)._initialize()
        self._addViewModelProperty('state', FunRandomProgressionState())
        self._addViewModelProperty('condition', FunRandomProgressionCondition())
        self._addViewModelProperty('infiniteCondition', FunRandomInfiniteProgressionCondition())
        self._addViewModelProperty('infiniteStage', FunRandomProgressionStage())
        self._addArrayProperty('stages', Array())
        self._addStringProperty('assetsPointer', 'undefined')
        self._addBoolProperty('isFirstOpen', False)
        self.onClose = self._addCommand('onClose')
        self.onShowInfo = self._addCommand('onShowInfo')
        self.onOpenTierList = self._addCommand('onOpenTierList')

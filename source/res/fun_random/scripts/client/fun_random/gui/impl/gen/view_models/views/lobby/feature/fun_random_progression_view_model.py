# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_progression_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_condition import FunRandomProgressionCondition
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_stage import FunRandomProgressionStage
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_state import FunRandomProgressionState

class FunRandomProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onShowInfo')

    def __init__(self, properties=3, commands=2):
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

    def getStages(self):
        return self._getArray(2)

    def setStages(self, value):
        self._setArray(2, value)

    @staticmethod
    def getStagesType():
        return FunRandomProgressionStage

    def _initialize(self):
        super(FunRandomProgressionViewModel, self)._initialize()
        self._addViewModelProperty('state', FunRandomProgressionState())
        self._addViewModelProperty('condition', FunRandomProgressionCondition())
        self._addArrayProperty('stages', Array())
        self.onClose = self._addCommand('onClose')
        self.onShowInfo = self._addCommand('onShowInfo')

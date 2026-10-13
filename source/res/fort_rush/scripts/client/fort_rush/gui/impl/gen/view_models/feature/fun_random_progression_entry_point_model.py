# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/feature/fun_random_progression_entry_point_model.py
from frameworks.wulf import ViewModel
from fort_rush.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_stage import FunRandomProgressionStage
from fort_rush.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_state import FunRandomProgressionState

class FunRandomProgressionEntryPointModel(ViewModel):
    __slots__ = ('onShowInfo',)

    def __init__(self, properties=2, commands=1):
        super(FunRandomProgressionEntryPointModel, self).__init__(properties=properties, commands=commands)

    @property
    def progressionState(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressionStateType():
        return FunRandomProgressionState

    @property
    def currentProgressionStage(self):
        return self._getViewModel(1)

    @staticmethod
    def getCurrentProgressionStageType():
        return FunRandomProgressionStage

    def _initialize(self):
        super(FunRandomProgressionEntryPointModel, self)._initialize()
        self._addViewModelProperty('progressionState', FunRandomProgressionState())
        self._addViewModelProperty('currentProgressionStage', FunRandomProgressionStage())
        self.onShowInfo = self._addCommand('onShowInfo')

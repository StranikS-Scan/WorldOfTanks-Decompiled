# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_strengths_weaknesses_view_model.py
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_strengths_weaknesses import FunRandomStrengthsWeaknesses

class FunRandomStrengthsWeaknessesViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(FunRandomStrengthsWeaknessesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def parameters(self):
        return self._getViewModel(0)

    @staticmethod
    def getParametersType():
        return FunRandomStrengthsWeaknesses

    def _initialize(self):
        super(FunRandomStrengthsWeaknessesViewModel, self)._initialize()
        self._addViewModelProperty('parameters', FunRandomStrengthsWeaknesses())

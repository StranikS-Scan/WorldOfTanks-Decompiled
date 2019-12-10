# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_mega_toy_bonus_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_bonus_formula_model import NewYearBonusFormulaModel

class NewYearMegaToyBonusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearMegaToyBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def toysTable(self):
        return self._getViewModel(0)

    @property
    def bonusFormula(self):
        return self._getViewModel(1)

    def getBonusValue(self):
        return self._getReal(2)

    def setBonusValue(self, value):
        self._setReal(2, value)

    def _initialize(self):
        super(NewYearMegaToyBonusTooltipModel, self)._initialize()
        self._addViewModelProperty('toysTable', UserListModel())
        self._addViewModelProperty('bonusFormula', NewYearBonusFormulaModel())
        self._addRealProperty('bonusValue', 0.0)

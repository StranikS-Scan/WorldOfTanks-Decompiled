# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_widget_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_bonus_formula_model import NewYearBonusFormulaModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NewYearWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def multipliersTable(self):
        return self._getViewModel(0)

    @property
    def bonusFormula(self):
        return self._getViewModel(1)

    def getCurrentLevel(self):
        return self._getString(2)

    def setCurrentLevel(self, value):
        self._setString(2, value)

    def getNextLevel(self):
        return self._getString(3)

    def setNextLevel(self, value):
        self._setString(3, value)

    def getCurrentPoints(self):
        return self._getNumber(4)

    def setCurrentPoints(self, value):
        self._setNumber(4, value)

    def getNextPoints(self):
        return self._getNumber(5)

    def setNextPoints(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(NewYearWidgetTooltipModel, self)._initialize()
        self._addViewModelProperty('multipliersTable', UserListModel())
        self._addViewModelProperty('bonusFormula', NewYearBonusFormulaModel())
        self._addStringProperty('currentLevel', 'I')
        self._addStringProperty('nextLevel', 'II')
        self._addNumberProperty('currentPoints', 1)
        self._addNumberProperty('nextPoints', 1)

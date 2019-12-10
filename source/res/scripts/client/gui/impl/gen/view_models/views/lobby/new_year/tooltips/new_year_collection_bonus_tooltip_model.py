# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_collection_bonus_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_bonus_formula_model import NewYearBonusFormulaModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearCollectionBonusTooltipModel(ViewModel):
    __slots__ = ()
    NEW_YEAR = 'NewYear'
    XMAS = 'Christmas'
    FAIRYTALE = 'Fairytale'
    ORIENTAL = 'Oriental'

    def __init__(self, properties=3, commands=0):
        super(NewYearCollectionBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def collectionsTable(self):
        return self._getViewModel(0)

    @property
    def bonusFormula(self):
        return self._getViewModel(1)

    def getSelectedCollection(self):
        return self._getString(2)

    def setSelectedCollection(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NewYearCollectionBonusTooltipModel, self)._initialize()
        self._addViewModelProperty('collectionsTable', UserListModel())
        self._addViewModelProperty('bonusFormula', NewYearBonusFormulaModel())
        self._addStringProperty('selectedCollection', 'NewYear')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_mega_collection_bonus_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_bonus_formula_model import NyBonusFormulaModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_single_mega_collection_bonus_model import NySingleMegaCollectionBonusModel

class NyMegaCollectionBonusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyMegaCollectionBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def collectionsTable(self):
        return self._getViewModel(0)

    @property
    def bonusFormula(self):
        return self._getViewModel(1)

    def getBonusValue(self):
        return self._getReal(2)

    def setBonusValue(self, value):
        self._setReal(2, value)

    def _initialize(self):
        super(NyMegaCollectionBonusTooltipModel, self)._initialize()
        self._addViewModelProperty('collectionsTable', UserListModel())
        self._addViewModelProperty('bonusFormula', NyBonusFormulaModel())
        self._addRealProperty('bonusValue', 0.0)

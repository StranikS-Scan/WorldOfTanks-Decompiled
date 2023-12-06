# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_box_with_toys_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.new_year_toy_icon_bonus_model import NewYearToyIconBonusModel

class NyBoxWithToysTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyBoxWithToysTooltipModel, self).__init__(properties=properties, commands=commands)

    def getToys(self):
        return self._getArray(0)

    def setToys(self, value):
        self._setArray(0, value)

    @staticmethod
    def getToysType():
        return NewYearToyIconBonusModel

    def _initialize(self):
        super(NyBoxWithToysTooltipModel, self)._initialize()
        self._addArrayProperty('toys', Array())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_shop_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class FestivalShopViewModel(ViewModel):
    __slots__ = ('onPackageClicked',)

    @property
    def packages(self):
        return self._getViewModel(0)

    def getIsLocked(self):
        return self._getBool(1)

    def setIsLocked(self, value):
        self._setBool(1, value)

    def getPackageCount(self):
        return self._getNumber(2)

    def setPackageCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(FestivalShopViewModel, self)._initialize()
        self._addViewModelProperty('packages', ListModel())
        self._addBoolProperty('isLocked', False)
        self._addNumberProperty('packageCount', 0)
        self.onPackageClicked = self._addCommand('onPackageClicked')

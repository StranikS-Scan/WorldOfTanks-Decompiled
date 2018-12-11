# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/tooltips/new_year_album_bonus_tooltip_model.py
import typing
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearAlbumBonusTooltipModel(ViewModel):
    __slots__ = ()

    @property
    def table(self):
        return self._getViewModel(0)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getBonus(self):
        return self._getNumber(2)

    def setBonus(self, value):
        self._setNumber(2, value)

    def getCurrentDecorations(self):
        return self._getNumber(3)

    def setCurrentDecorations(self, value):
        self._setNumber(3, value)

    def getTotalDecorations(self):
        return self._getNumber(4)

    def setTotalDecorations(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(NewYearAlbumBonusTooltipModel, self)._initialize()
        self._addViewModelProperty('table', UserListModel())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('bonus', 0)
        self._addNumberProperty('currentDecorations', 0)
        self._addNumberProperty('totalDecorations', 0)

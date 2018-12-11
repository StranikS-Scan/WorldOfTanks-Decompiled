# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/tooltips/new_year_album_bonus_tooltip_item_model.py
from frameworks.wulf import ViewModel

class NewYearAlbumBonusTooltipItemModel(ViewModel):
    __slots__ = ()

    def getLeftValue(self):
        return self._getNumber(0)

    def setLeftValue(self, value):
        self._setNumber(0, value)

    def getRightValue(self):
        return self._getNumber(1)

    def setRightValue(self, value):
        self._setNumber(1, value)

    def getBonus(self):
        return self._getNumber(2)

    def setBonus(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NewYearAlbumBonusTooltipItemModel, self)._initialize()
        self._addNumberProperty('leftValue', -1)
        self._addNumberProperty('rightValue', -1)
        self._addNumberProperty('bonus', -1)

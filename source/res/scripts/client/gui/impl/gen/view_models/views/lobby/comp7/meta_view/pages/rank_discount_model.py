# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/rank_discount_model.py
from enum import IntEnum
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import ProgressionItemBaseModel

class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class RankDiscountModel(ProgressionItemBaseModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RankDiscountModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getNumber(4)

    def setValue(self, value):
        self._setNumber(4, value)

    def getWasUnlocked(self):
        return self._getBool(5)

    def setWasUnlocked(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(RankDiscountModel, self)._initialize()
        self._addNumberProperty('value', 0)
        self._addBoolProperty('wasUnlocked', False)

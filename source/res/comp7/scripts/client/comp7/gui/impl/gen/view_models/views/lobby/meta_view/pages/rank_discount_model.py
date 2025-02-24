# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/rank_discount_model.py
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.progression_item_base_model import ProgressionItemBaseModel

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

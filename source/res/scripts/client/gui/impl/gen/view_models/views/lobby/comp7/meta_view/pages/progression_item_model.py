# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/progression_item_model.py
from enum import IntEnum
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import ProgressionItemBaseModel

class Type(IntEnum):
    RANK = 0


class ProgressionItemModel(ProgressionItemBaseModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ProgressionItemModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return Type(self._getNumber(4))

    def setType(self, value):
        self._setNumber(4, value.value)

    def getHasRankInactivity(self):
        return self._getBool(5)

    def setHasRankInactivity(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ProgressionItemModel, self)._initialize()
        self._addNumberProperty('type')
        self._addBoolProperty('hasRankInactivity', False)

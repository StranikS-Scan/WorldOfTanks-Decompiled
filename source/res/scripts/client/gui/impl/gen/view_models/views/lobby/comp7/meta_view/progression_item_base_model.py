# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/progression_item_base_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_division import ProgressionDivision

class Rank(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7


class ProgressionItemBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ProgressionItemBaseModel, self).__init__(properties=properties, commands=commands)

    def getRank(self):
        return Rank(self._getNumber(0))

    def setRank(self, value):
        self._setNumber(0, value.value)

    def getFrom(self):
        return self._getNumber(1)

    def setFrom(self, value):
        self._setNumber(1, value)

    def getTo(self):
        return self._getNumber(2)

    def setTo(self, value):
        self._setNumber(2, value)

    def getDivisions(self):
        return self._getArray(3)

    def setDivisions(self, value):
        self._setArray(3, value)

    @staticmethod
    def getDivisionsType():
        return ProgressionDivision

    def _initialize(self):
        super(ProgressionItemBaseModel, self)._initialize()
        self._addNumberProperty('rank')
        self._addNumberProperty('from', 0)
        self._addNumberProperty('to', 0)
        self._addArrayProperty('divisions', Array())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/progression_crew_book_model.py
from frameworks.wulf import ViewModel

class ProgressionCrewBookModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ProgressionCrewBookModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getCrewBookType(self):
        return self._getString(1)

    def setCrewBookType(self, value):
        self._setString(1, value)

    def getNation(self):
        return self._getString(2)

    def setNation(self, value):
        self._setString(2, value)

    def getExpBonus(self):
        return self._getNumber(3)

    def setExpBonus(self, value):
        self._setNumber(3, value)

    def getAvailableAmount(self):
        return self._getNumber(4)

    def setAvailableAmount(self, value):
        self._setNumber(4, value)

    def getHaveBuyButton(self):
        return self._getBool(5)

    def setHaveBuyButton(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ProgressionCrewBookModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('crewBookType', '')
        self._addStringProperty('nation', '')
        self._addNumberProperty('expBonus', 0)
        self._addNumberProperty('availableAmount', 1)
        self._addBoolProperty('haveBuyButton', False)

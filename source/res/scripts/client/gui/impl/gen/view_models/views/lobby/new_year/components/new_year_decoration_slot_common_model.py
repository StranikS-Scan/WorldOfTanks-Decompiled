# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_decoration_slot_common_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NewYearDecorationSlotCommonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NewYearDecorationSlotCommonModel, self).__init__(properties=properties, commands=commands)

    def getToyID(self):
        return self._getNumber(0)

    def setToyID(self, value):
        self._setNumber(0, value)

    def getDecorationImage(self):
        return self._getResource(1)

    def setDecorationImage(self, value):
        self._setResource(1, value)

    def getRankImage(self):
        return self._getResource(2)

    def setRankImage(self, value):
        self._setResource(2, value)

    def getTitle(self):
        return self._getResource(3)

    def setTitle(self, value):
        self._setResource(3, value)

    def getDescription(self):
        return self._getResource(4)

    def setDescription(self, value):
        self._setResource(4, value)

    def getIsMega(self):
        return self._getBool(5)

    def setIsMega(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NewYearDecorationSlotCommonModel, self)._initialize()
        self._addNumberProperty('toyID', 0)
        self._addResourceProperty('decorationImage', R.invalid())
        self._addResourceProperty('rankImage', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addBoolProperty('isMega', False)

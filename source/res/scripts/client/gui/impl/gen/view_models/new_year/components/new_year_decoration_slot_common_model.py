# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_decoration_slot_common_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NewYearDecorationSlotCommonModel(ViewModel):
    __slots__ = ()

    def getIdx(self):
        return self._getNumber(0)

    def setIdx(self, value):
        self._setNumber(0, value)

    def getToyID(self):
        return self._getNumber(1)

    def setToyID(self, value):
        self._setNumber(1, value)

    def getDecorationImage(self):
        return self._getResource(2)

    def setDecorationImage(self, value):
        self._setResource(2, value)

    def getRankImage(self):
        return self._getResource(3)

    def setRankImage(self, value):
        self._setResource(3, value)

    def getTitle(self):
        return self._getResource(4)

    def setTitle(self, value):
        self._setResource(4, value)

    def getDescription(self):
        return self._getResource(5)

    def setDescription(self, value):
        self._setResource(5, value)

    def _initialize(self):
        super(NewYearDecorationSlotCommonModel, self)._initialize()
        self._addNumberProperty('idx', 0)
        self._addNumberProperty('toyID', 0)
        self._addResourceProperty('decorationImage', Resource.INVALID)
        self._addResourceProperty('rankImage', Resource.INVALID)
        self._addResourceProperty('title', Resource.INVALID)
        self._addResourceProperty('description', Resource.INVALID)

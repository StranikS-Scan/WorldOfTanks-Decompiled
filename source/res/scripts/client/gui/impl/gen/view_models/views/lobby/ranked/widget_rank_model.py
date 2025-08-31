# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/widget_rank_model.py
from frameworks.wulf import ViewModel

class WidgetRankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(WidgetRankModel, self).__init__(properties=properties, commands=commands)

    def getDivisionID(self):
        return self._getNumber(0)

    def setDivisionID(self, value):
        self._setNumber(0, value)

    def getRankID(self):
        return self._getNumber(1)

    def setRankID(self, value):
        self._setNumber(1, value)

    def getRankName(self):
        return self._getNumber(2)

    def setRankName(self, value):
        self._setNumber(2, value)

    def getIsUnburnable(self):
        return self._getBool(3)

    def setIsUnburnable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WidgetRankModel, self)._initialize()
        self._addNumberProperty('divisionID', 0)
        self._addNumberProperty('rankID', 0)
        self._addNumberProperty('rankName', 0)
        self._addBoolProperty('isUnburnable', False)

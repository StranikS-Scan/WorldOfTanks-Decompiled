# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_awards_tooltip_model.py
from frameworks.wulf import Array, ViewModel

class SeniorityAwardsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SeniorityAwardsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def getMaxCategory(self):
        return self._getString(1)

    def setMaxCategory(self, value):
        self._setString(1, value)

    def getYears(self):
        return self._getNumber(2)

    def setYears(self, value):
        self._setNumber(2, value)

    def getCategories(self):
        return self._getArray(3)

    def setCategories(self, value):
        self._setArray(3, value)

    @staticmethod
    def getCategoriesType():
        return unicode

    def _initialize(self):
        super(SeniorityAwardsTooltipModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addStringProperty('maxCategory', '')
        self._addNumberProperty('years', 0)
        self._addArrayProperty('categories', Array())

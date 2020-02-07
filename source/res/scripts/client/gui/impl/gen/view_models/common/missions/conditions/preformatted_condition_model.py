# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/conditions/preformatted_condition_model.py
from gui.impl.gen.view_models.common.missions.conditions.condition_base_model import ConditionBaseModel

class PreformattedConditionModel(ConditionBaseModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(PreformattedConditionModel, self).__init__(properties=properties, commands=commands)

    def getTitleData(self):
        return self._getString(1)

    def setTitleData(self, value):
        self._setString(1, value)

    def getDescrData(self):
        return self._getString(2)

    def setDescrData(self, value):
        self._setString(2, value)

    def getIconKey(self):
        return self._getString(3)

    def setIconKey(self, value):
        self._setString(3, value)

    def getCurrent(self):
        return self._getNumber(4)

    def setCurrent(self, value):
        self._setNumber(4, value)

    def getTotal(self):
        return self._getNumber(5)

    def setTotal(self, value):
        self._setNumber(5, value)

    def getEarned(self):
        return self._getNumber(6)

    def setEarned(self, value):
        self._setNumber(6, value)

    def getProgressType(self):
        return self._getString(7)

    def setProgressType(self, value):
        self._setString(7, value)

    def getSortKey(self):
        return self._getString(8)

    def setSortKey(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(PreformattedConditionModel, self)._initialize()
        self._addStringProperty('titleData', '')
        self._addStringProperty('descrData', '')
        self._addStringProperty('iconKey', '')
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
        self._addNumberProperty('earned', 0)
        self._addStringProperty('progressType', '')
        self._addStringProperty('sortKey', '')

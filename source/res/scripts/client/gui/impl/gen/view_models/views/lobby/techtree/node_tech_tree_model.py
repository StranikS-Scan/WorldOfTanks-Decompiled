# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/node_tech_tree_model.py
from frameworks.wulf import ViewModel

class NodeTechTreeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(NodeTechTreeModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getState(self):
        return self._getNumber(1)

    def setState(self, value):
        self._setNumber(1, value)

    def getExtendedState(self):
        return self._getNumber(2)

    def setExtendedState(self, value):
        self._setNumber(2, value)

    def getItemLevel(self):
        return self._getNumber(3)

    def setItemLevel(self, value):
        self._setNumber(3, value)

    def getBlueprintCanConvert(self):
        return self._getBool(4)

    def setBlueprintCanConvert(self, value):
        self._setBool(4, value)

    def getBlueprintMaxCount(self):
        return self._getNumber(5)

    def setBlueprintMaxCount(self, value):
        self._setNumber(5, value)

    def getBlueprintBalance(self):
        return self._getNumber(6)

    def setBlueprintBalance(self, value):
        self._setNumber(6, value)

    def getEarnedXP(self):
        return self._getNumber(7)

    def setEarnedXP(self, value):
        self._setNumber(7, value)

    def getIsRemovable(self):
        return self._getBool(8)

    def setIsRemovable(self, value):
        self._setBool(8, value)

    def getItemType(self):
        return self._getString(9)

    def setItemType(self, value):
        self._setString(9, value)

    def getColumn(self):
        return self._getNumber(10)

    def setColumn(self, value):
        self._setNumber(10, value)

    def getRow(self):
        return self._getNumber(11)

    def setRow(self, value):
        self._setNumber(11, value)

    def getNation(self):
        return self._getString(12)

    def setNation(self, value):
        self._setString(12, value)

    def getEarlyAccessPrice(self):
        return self._getNumber(13)

    def setEarlyAccessPrice(self, value):
        self._setNumber(13, value)

    def getIsEarlyAccessLocked(self):
        return self._getBool(14)

    def setIsEarlyAccessLocked(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(NodeTechTreeModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('state', 0)
        self._addNumberProperty('extendedState', 0)
        self._addNumberProperty('itemLevel', 0)
        self._addBoolProperty('blueprintCanConvert', False)
        self._addNumberProperty('blueprintMaxCount', 0)
        self._addNumberProperty('blueprintBalance', 0)
        self._addNumberProperty('earnedXP', 0)
        self._addBoolProperty('isRemovable', False)
        self._addStringProperty('itemType', '')
        self._addNumberProperty('column', 0)
        self._addNumberProperty('row', 0)
        self._addStringProperty('nation', '')
        self._addNumberProperty('earlyAccessPrice', 0)
        self._addBoolProperty('isEarlyAccessLocked', False)

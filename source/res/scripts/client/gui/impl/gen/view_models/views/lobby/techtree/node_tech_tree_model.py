# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/node_tech_tree_model.py
from frameworks.wulf import ViewModel

class NodeTechTreeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(NodeTechTreeModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getState(self):
        return self._getNumber(1)

    def setState(self, value):
        self._setNumber(1, value)

    def getItemLevel(self):
        return self._getNumber(2)

    def setItemLevel(self, value):
        self._setNumber(2, value)

    def getBlueprintCanConvert(self):
        return self._getBool(3)

    def setBlueprintCanConvert(self, value):
        self._setBool(3, value)

    def getBlueprintMaxCount(self):
        return self._getNumber(4)

    def setBlueprintMaxCount(self, value):
        self._setNumber(4, value)

    def getBlueprintBalance(self):
        return self._getNumber(5)

    def setBlueprintBalance(self, value):
        self._setNumber(5, value)

    def getEarnedXP(self):
        return self._getNumber(6)

    def setEarnedXP(self, value):
        self._setNumber(6, value)

    def getIsRemovable(self):
        return self._getBool(7)

    def setIsRemovable(self, value):
        self._setBool(7, value)

    def getItemType(self):
        return self._getString(8)

    def setItemType(self, value):
        self._setString(8, value)

    def getColumn(self):
        return self._getNumber(9)

    def setColumn(self, value):
        self._setNumber(9, value)

    def getRow(self):
        return self._getNumber(10)

    def setRow(self, value):
        self._setNumber(10, value)

    def getNation(self):
        return self._getString(11)

    def setNation(self, value):
        self._setString(11, value)

    def getEarlyAccessPrice(self):
        return self._getNumber(12)

    def setEarlyAccessPrice(self, value):
        self._setNumber(12, value)

    def getIsEarlyAccessLocked(self):
        return self._getBool(13)

    def setIsEarlyAccessLocked(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(NodeTechTreeModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('state', 0)
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

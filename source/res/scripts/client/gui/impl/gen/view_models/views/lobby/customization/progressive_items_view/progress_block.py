# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progressive_items_view/progress_block.py
from frameworks.wulf import ViewModel

class ProgressBlock(ViewModel):
    __slots__ = ()
    PB_EMPTY = 'empty'
    PB_DISCRETE = 'discrete'
    PB_PLAIN = 'plain'

    def __init__(self, properties=5, commands=0):
        super(ProgressBlock, self).__init__(properties=properties, commands=commands)

    def getProgressBarType(self):
        return self._getString(0)

    def setProgressBarType(self, value):
        self._setString(0, value)

    def getHideProgressBarAndString(self):
        return self._getBool(1)

    def setHideProgressBarAndString(self, value):
        self._setBool(1, value)

    def getUnlockCondition(self):
        return self._getString(2)

    def setUnlockCondition(self, value):
        self._setString(2, value)

    def getProgressionVal(self):
        return self._getNumber(3)

    def setProgressionVal(self, value):
        self._setNumber(3, value)

    def getMaxProgressionVal(self):
        return self._getNumber(4)

    def setMaxProgressionVal(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ProgressBlock, self)._initialize()
        self._addStringProperty('progressBarType', 'PB_EMPTY')
        self._addBoolProperty('hideProgressBarAndString', False)
        self._addStringProperty('unlockCondition', '')
        self._addNumberProperty('progressionVal', 0)
        self._addNumberProperty('maxProgressionVal', 0)

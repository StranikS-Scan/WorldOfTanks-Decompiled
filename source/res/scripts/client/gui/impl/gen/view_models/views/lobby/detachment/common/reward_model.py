# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/reward_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getValue(self):
        return self._getNumber(2)

    def setValue(self, value):
        self._setNumber(2, value)

    def getExtraValue(self):
        return self._getString(3)

    def setExtraValue(self, value):
        self._setString(3, value)

    def getTitle(self):
        return self._getResource(4)

    def setTitle(self, value):
        self._setResource(4, value)

    def getExtraTitle(self):
        return self._getResource(5)

    def setExtraTitle(self, value):
        self._setResource(5, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('value', 0)
        self._addStringProperty('extraValue', '')
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('extraTitle', R.invalid())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_reserves/converted_booster_model.py
from frameworks.wulf import ViewModel

class ConvertedBoosterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ConvertedBoosterModel, self).__init__(properties=properties, commands=commands)

    def getOldCount(self):
        return self._getNumber(0)

    def setOldCount(self, value):
        self._setNumber(0, value)

    def getOldDescription(self):
        return self._getString(1)

    def setOldDescription(self, value):
        self._setString(1, value)

    def getNewCount(self):
        return self._getNumber(2)

    def setNewCount(self, value):
        self._setNumber(2, value)

    def getNewDescription(self):
        return self._getString(3)

    def setNewDescription(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(ConvertedBoosterModel, self)._initialize()
        self._addNumberProperty('oldCount', 0)
        self._addStringProperty('oldDescription', '')
        self._addNumberProperty('newCount', 0)
        self._addStringProperty('newDescription', '')

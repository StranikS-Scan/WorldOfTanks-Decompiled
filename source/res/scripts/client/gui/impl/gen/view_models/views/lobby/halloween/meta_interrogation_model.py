# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/meta_interrogation_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class MetaInterrogationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(MetaInterrogationModel, self).__init__(properties=properties, commands=commands)

    def getVideoIndex(self):
        return self._getNumber(0)

    def setVideoIndex(self, value):
        self._setNumber(0, value)

    def getKeysAmount(self):
        return self._getNumber(1)

    def setKeysAmount(self, value):
        self._setNumber(1, value)

    def getDecodePrice(self):
        return self._getNumber(2)

    def setDecodePrice(self, value):
        self._setNumber(2, value)

    def getSkipPrice(self):
        return self._getNumber(3)

    def setSkipPrice(self, value):
        self._setNumber(3, value)

    def getTaskPhase(self):
        return self._getNumber(4)

    def setTaskPhase(self, value):
        self._setNumber(4, value)

    def getTaskDifficulty(self):
        return self._getNumber(5)

    def setTaskDifficulty(self, value):
        self._setNumber(5, value)

    def getIsTaskDone(self):
        return self._getBool(6)

    def setIsTaskDone(self, value):
        self._setBool(6, value)

    def getBonuses(self):
        return self._getArray(7)

    def setBonuses(self, value):
        self._setArray(7, value)

    def _initialize(self):
        super(MetaInterrogationModel, self)._initialize()
        self._addNumberProperty('videoIndex', 1)
        self._addNumberProperty('keysAmount', 0)
        self._addNumberProperty('decodePrice', 0)
        self._addNumberProperty('skipPrice', 0)
        self._addNumberProperty('taskPhase', 0)
        self._addNumberProperty('taskDifficulty', 0)
        self._addBoolProperty('isTaskDone', False)
        self._addArrayProperty('bonuses', Array())

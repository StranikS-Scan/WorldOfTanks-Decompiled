# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/paragons_unlocked_branch.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ParagonsUnlockedBranch(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ParagonsUnlockedBranch, self).__init__(properties=properties, commands=commands)

    def getParagonsUnlockID(self):
        return self._getNumber(0)

    def setParagonsUnlockID(self, value):
        self._setNumber(0, value)

    def getNation(self):
        return self._getString(1)

    def setNation(self, value):
        self._setString(1, value)

    def getUnlockedVehicleCDs(self):
        return self._getArray(2)

    def setUnlockedVehicleCDs(self, value):
        self._setArray(2, value)

    @staticmethod
    def getUnlockedVehicleCDsType():
        return int

    def _initialize(self):
        super(ParagonsUnlockedBranch, self)._initialize()
        self._addNumberProperty('paragonsUnlockID', 1)
        self._addStringProperty('nation', '')
        self._addArrayProperty('unlockedVehicleCDs', Array())

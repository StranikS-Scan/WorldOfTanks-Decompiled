# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/premium_missions_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class PremiumMissionsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(PremiumMissionsModel, self).__init__(properties=properties, commands=commands)

    def getIsPremiumAccount(self):
        return self._getBool(0)

    def setIsPremiumAccount(self, value):
        self._setBool(0, value)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def getTitle(self):
        return self._getResource(2)

    def setTitle(self, value):
        self._setResource(2, value)

    def getMissions(self):
        return self._getArray(3)

    def setMissions(self, value):
        self._setArray(3, value)

    def getMissionsCompletedVisited(self):
        return self._getArray(4)

    def setMissionsCompletedVisited(self, value):
        self._setArray(4, value)

    def getSyncInitiator(self):
        return self._getNumber(5)

    def setSyncInitiator(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(PremiumMissionsModel, self)._initialize()
        self._addBoolProperty('isPremiumAccount', False)
        self._addBoolProperty('isEnabled', False)
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('missions', Array())
        self._addArrayProperty('missionsCompletedVisited', Array())
        self._addNumberProperty('syncInitiator', 0)

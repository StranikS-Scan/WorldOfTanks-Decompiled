# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/markers/ny_headquarters_marker_model.py
from frameworks.wulf import ViewModel

class NyHeadquartersMarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyHeadquartersMarkerModel, self).__init__(properties=properties, commands=commands)

    def getIsFriendHangar(self):
        return self._getBool(0)

    def setIsFriendHangar(self, value):
        self._setBool(0, value)

    def getSacksCount(self):
        return self._getNumber(1)

    def setSacksCount(self, value):
        self._setNumber(1, value)

    def getIsVisible(self):
        return self._getBool(2)

    def setIsVisible(self, value):
        self._setBool(2, value)

    def getLevelState(self):
        return self._getString(3)

    def setLevelState(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(NyHeadquartersMarkerModel, self)._initialize()
        self._addBoolProperty('isFriendHangar', False)
        self._addNumberProperty('sacksCount', 0)
        self._addBoolProperty('isVisible', True)
        self._addStringProperty('levelState', 'default')

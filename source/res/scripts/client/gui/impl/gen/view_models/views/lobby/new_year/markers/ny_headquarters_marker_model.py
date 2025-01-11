# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/markers/ny_headquarters_marker_model.py
from frameworks.wulf import ViewModel

class NyHeadquartersMarkerModel(ViewModel):
    __slots__ = ('onAnimationEnd',)

    def __init__(self, properties=7, commands=1):
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

    def getIsLobby(self):
        return self._getBool(3)

    def setIsLobby(self, value):
        self._setBool(3, value)

    def getIsHangarReady(self):
        return self._getBool(4)

    def setIsHangarReady(self, value):
        self._setBool(4, value)

    def getSyncInitiator(self):
        return self._getNumber(5)

    def setSyncInitiator(self, value):
        self._setNumber(5, value)

    def getLevelState(self):
        return self._getString(6)

    def setLevelState(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(NyHeadquartersMarkerModel, self)._initialize()
        self._addBoolProperty('isFriendHangar', False)
        self._addNumberProperty('sacksCount', 0)
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('isLobby', False)
        self._addBoolProperty('isHangarReady', False)
        self._addNumberProperty('syncInitiator', 0)
        self._addStringProperty('levelState', 'default')
        self.onAnimationEnd = self._addCommand('onAnimationEnd')

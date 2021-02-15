# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/select_respawn_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SelectRespawnViewModel(ViewModel):
    __slots__ = ('onCompleteBtnClick', 'onSelectPoint')

    def __init__(self, properties=12, commands=2):
        super(SelectRespawnViewModel, self).__init__(properties=properties, commands=commands)

    def getHeader(self):
        return self._getResource(0)

    def setHeader(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def getLeftTime(self):
        return self._getString(2)

    def setLeftTime(self, value):
        self._setString(2, value)

    def getBtnDescription(self):
        return self._getResource(3)

    def setBtnDescription(self, value):
        self._setResource(3, value)

    def getPoints(self):
        return self._getArray(4)

    def setPoints(self, value):
        self._setArray(4, value)

    def getBackground(self):
        return self._getResource(5)

    def setBackground(self, value):
        self._setResource(5, value)

    def getMinimapBG(self):
        return self._getString(6)

    def setMinimapBG(self, value):
        self._setString(6, value)

    def getMapSize(self):
        return self._getNumber(7)

    def setMapSize(self, value):
        self._setNumber(7, value)

    def getSelectedPointID(self):
        return self._getString(8)

    def setSelectedPointID(self, value):
        self._setString(8, value)

    def getIsTimeRunningOut(self):
        return self._getBool(9)

    def setIsTimeRunningOut(self, value):
        self._setBool(9, value)

    def getIsWaitingPlayers(self):
        return self._getBool(10)

    def setIsWaitingPlayers(self, value):
        self._setBool(10, value)

    def getIsReplay(self):
        return self._getBool(11)

    def setIsReplay(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(SelectRespawnViewModel, self)._initialize()
        self._addResourceProperty('header', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addStringProperty('leftTime', '')
        self._addResourceProperty('btnDescription', R.invalid())
        self._addArrayProperty('points', Array())
        self._addResourceProperty('background', R.invalid())
        self._addStringProperty('minimapBG', '')
        self._addNumberProperty('mapSize', 0)
        self._addStringProperty('selectedPointID', '')
        self._addBoolProperty('isTimeRunningOut', False)
        self._addBoolProperty('isWaitingPlayers', False)
        self._addBoolProperty('isReplay', False)
        self.onCompleteBtnClick = self._addCommand('onCompleteBtnClick')
        self.onSelectPoint = self._addCommand('onSelectPoint')

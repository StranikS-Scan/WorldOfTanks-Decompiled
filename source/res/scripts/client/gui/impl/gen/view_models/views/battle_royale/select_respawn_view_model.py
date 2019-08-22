# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/select_respawn_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class SelectRespawnViewModel(ViewModel):
    __slots__ = ('onCompleteBtnClick', 'onSelectPoint')

    def getHeader(self):
        return self._getString(0)

    def setHeader(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getLeftTime(self):
        return self._getString(2)

    def setLeftTime(self, value):
        self._setString(2, value)

    def getBtnDescription(self):
        return self._getString(3)

    def setBtnDescription(self, value):
        self._setString(3, value)

    def getPoints(self):
        return self._getArray(4)

    def setPoints(self, value):
        self._setArray(4, value)

    def getMinimapBG(self):
        return self._getString(5)

    def setMinimapBG(self, value):
        self._setString(5, value)

    def getMapSize(self):
        return self._getNumber(6)

    def setMapSize(self, value):
        self._setNumber(6, value)

    def getSelectedPointID(self):
        return self._getString(7)

    def setSelectedPointID(self, value):
        self._setString(7, value)

    def getIsTimeRunningOut(self):
        return self._getBool(8)

    def setIsTimeRunningOut(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(SelectRespawnViewModel, self)._initialize()
        self._addStringProperty('header', '')
        self._addStringProperty('description', '')
        self._addStringProperty('leftTime', '')
        self._addStringProperty('btnDescription', '')
        self._addArrayProperty('points', Array())
        self._addStringProperty('minimapBG', '')
        self._addNumberProperty('mapSize', 0)
        self._addStringProperty('selectedPointID', '')
        self._addBoolProperty('isTimeRunningOut', False)
        self.onCompleteBtnClick = self._addCommand('onCompleteBtnClick')
        self.onSelectPoint = self._addCommand('onSelectPoint')

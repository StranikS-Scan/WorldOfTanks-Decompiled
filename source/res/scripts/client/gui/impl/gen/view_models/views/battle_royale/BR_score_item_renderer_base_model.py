# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/BR_score_item_renderer_base_model.py
from frameworks.wulf import ViewModel

class BRScoreItemRendererBaseModel(ViewModel):
    __slots__ = ()

    def getUserCurrent(self):
        return self._getBool(0)

    def setUserCurrent(self, value):
        self._setBool(0, value)

    def getUserName(self):
        return self._getString(1)

    def setUserName(self, value):
        self._setString(1, value)

    def getUserPlace(self):
        return self._getString(2)

    def setUserPlace(self, value):
        self._setString(2, value)

    def getCountChevrones(self):
        return self._getNumber(3)

    def setCountChevrones(self, value):
        self._setNumber(3, value)

    def getTextColor(self):
        return self._getNumber(4)

    def setTextColor(self, value):
        self._setNumber(4, value)

    def getIsLeaver(self):
        return self._getBool(5)

    def setIsLeaver(self, value):
        self._setBool(5, value)

    def getIsWinner(self):
        return self._getBool(6)

    def setIsWinner(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(BRScoreItemRendererBaseModel, self)._initialize()
        self._addBoolProperty('userCurrent', False)
        self._addStringProperty('userName', '')
        self._addStringProperty('userPlace', '')
        self._addNumberProperty('countChevrones', -2)
        self._addNumberProperty('textColor', 15327935)
        self._addBoolProperty('isLeaver', False)
        self._addBoolProperty('isWinner', False)

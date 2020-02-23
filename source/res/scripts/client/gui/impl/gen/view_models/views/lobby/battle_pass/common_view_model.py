# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/common_view_model.py
from frameworks.wulf import ViewModel

class CommonViewModel(ViewModel):
    __slots__ = ('onClosed',)

    def __init__(self, properties=7, commands=1):
        super(CommonViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getCurrentLevel(self):
        return self._getNumber(1)

    def setCurrentLevel(self, value):
        self._setNumber(1, value)

    def getMaxLevelBase(self):
        return self._getNumber(2)

    def setMaxLevelBase(self, value):
        self._setNumber(2, value)

    def getMaxLevelPost(self):
        return self._getNumber(3)

    def setMaxLevelPost(self, value):
        self._setNumber(3, value)

    def getIsPostProgression(self):
        return self._getBool(4)

    def setIsPostProgression(self, value):
        self._setBool(4, value)

    def getIsBattlePassPurchased(self):
        return self._getBool(5)

    def setIsBattlePassPurchased(self, value):
        self._setBool(5, value)

    def getCanBuy(self):
        return self._getBool(6)

    def setCanBuy(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(CommonViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('maxLevelBase', 1)
        self._addNumberProperty('maxLevelPost', 1)
        self._addBoolProperty('isPostProgression', False)
        self._addBoolProperty('isBattlePassPurchased', False)
        self._addBoolProperty('canBuy', False)
        self.onClosed = self._addCommand('onClosed')

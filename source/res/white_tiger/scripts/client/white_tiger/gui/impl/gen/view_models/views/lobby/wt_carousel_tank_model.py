# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_carousel_tank_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WtCarouselTankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(WtCarouselTankModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getIconSmall(self):
        return self._getResource(2)

    def setIconSmall(self, value):
        self._setResource(2, value)

    def getId(self):
        return self._getNumber(3)

    def setId(self, value):
        self._setNumber(3, value)

    def getQuantity(self):
        return self._getNumber(4)

    def setQuantity(self, value):
        self._setNumber(4, value)

    def getIsHunter(self):
        return self._getBool(5)

    def setIsHunter(self, value):
        self._setBool(5, value)

    def getIsSpecial(self):
        return self._getBool(6)

    def setIsSpecial(self, value):
        self._setBool(6, value)

    def getSelected(self):
        return self._getBool(7)

    def setSelected(self, value):
        self._setBool(7, value)

    def getInBattle(self):
        return self._getBool(8)

    def setInBattle(self, value):
        self._setBool(8, value)

    def getInPlatoon(self):
        return self._getBool(9)

    def setInPlatoon(self, value):
        self._setBool(9, value)

    def getUnsuitable(self):
        return self._getBool(10)

    def setUnsuitable(self, value):
        self._setBool(10, value)

    def getRemainingBattles(self):
        return self._getNumber(11)

    def setRemainingBattles(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(WtCarouselTankModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('iconSmall', R.invalid())
        self._addNumberProperty('id', 0)
        self._addNumberProperty('quantity', 0)
        self._addBoolProperty('isHunter', False)
        self._addBoolProperty('isSpecial', False)
        self._addBoolProperty('selected', False)
        self._addBoolProperty('inBattle', False)
        self._addBoolProperty('inPlatoon', False)
        self._addBoolProperty('unsuitable', False)
        self._addNumberProperty('remainingBattles', 0)

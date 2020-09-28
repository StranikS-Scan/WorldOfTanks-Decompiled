# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/carousel_tank_model.py
from frameworks.wulf import ViewModel

class CarouselTankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(CarouselTankModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getQuantity(self):
        return self._getNumber(2)

    def setQuantity(self, value):
        self._setNumber(2, value)

    def getIsHunter(self):
        return self._getBool(3)

    def setIsHunter(self, value):
        self._setBool(3, value)

    def getIsSpecial(self):
        return self._getBool(4)

    def setIsSpecial(self, value):
        self._setBool(4, value)

    def getSelected(self):
        return self._getBool(5)

    def setSelected(self, value):
        self._setBool(5, value)

    def getInBattle(self):
        return self._getBool(6)

    def setInBattle(self, value):
        self._setBool(6, value)

    def getInPlatoon(self):
        return self._getBool(7)

    def setInPlatoon(self, value):
        self._setBool(7, value)

    def getUnsuitable(self):
        return self._getBool(8)

    def setUnsuitable(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(CarouselTankModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addNumberProperty('id', 0)
        self._addNumberProperty('quantity', 0)
        self._addBoolProperty('isHunter', False)
        self._addBoolProperty('isSpecial', False)
        self._addBoolProperty('selected', False)
        self._addBoolProperty('inBattle', False)
        self._addBoolProperty('inPlatoon', False)
        self._addBoolProperty('unsuitable', False)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_carousel_tank_model.py
from frameworks.wulf import ViewModel

class WtCarouselTankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(WtCarouselTankModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def getQuantity(self):
        return self._getNumber(3)

    def setQuantity(self, value):
        self._setNumber(3, value)

    def getSelected(self):
        return self._getBool(4)

    def setSelected(self, value):
        self._setBool(4, value)

    def getInBattle(self):
        return self._getBool(5)

    def setInBattle(self, value):
        self._setBool(5, value)

    def getInPlatoon(self):
        return self._getBool(6)

    def setInPlatoon(self, value):
        self._setBool(6, value)

    def getUnsuitable(self):
        return self._getBool(7)

    def setUnsuitable(self, value):
        self._setBool(7, value)

    def getWtVehicleType(self):
        return self._getString(8)

    def setWtVehicleType(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(WtCarouselTankModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('id', 0)
        self._addNumberProperty('quantity', 0)
        self._addBoolProperty('selected', False)
        self._addBoolProperty('inBattle', False)
        self._addBoolProperty('inPlatoon', False)
        self._addBoolProperty('unsuitable', False)
        self._addStringProperty('wtVehicleType', 'boss')

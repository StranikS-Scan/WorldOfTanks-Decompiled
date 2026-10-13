# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_carousel_tank_model.py
from frameworks.wulf import ViewModel

class PortalCarouselTankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(PortalCarouselTankModel, self).__init__(properties=properties, commands=commands)

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

    def getSelected(self):
        return self._getBool(3)

    def setSelected(self, value):
        self._setBool(3, value)

    def getInPlatoon(self):
        return self._getBool(4)

    def setInPlatoon(self, value):
        self._setBool(4, value)

    def getInBattle(self):
        return self._getBool(5)

    def setInBattle(self, value):
        self._setBool(5, value)

    def getLevel(self):
        return self._getNumber(6)

    def setLevel(self, value):
        self._setNumber(6, value)

    def getHasUpdate(self):
        return self._getBool(7)

    def setHasUpdate(self, value):
        self._setBool(7, value)

    def getVehicleType(self):
        return self._getString(8)

    def setVehicleType(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(PortalCarouselTankModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('id', 0)
        self._addBoolProperty('selected', False)
        self._addBoolProperty('inPlatoon', False)
        self._addBoolProperty('inBattle', False)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('hasUpdate', False)
        self._addStringProperty('vehicleType', '')

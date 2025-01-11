# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/battle/grinch_hud/tank_panel_model.py
from frameworks.wulf import ViewModel

class TankPanelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(TankPanelModel, self).__init__(properties=properties, commands=commands)

    def getSpeed(self):
        return self._getNumber(0)

    def setSpeed(self, value):
        self._setNumber(0, value)

    def getHealth(self):
        return self._getNumber(1)

    def setHealth(self, value):
        self._setNumber(1, value)

    def getMaxHealth(self):
        return self._getNumber(2)

    def setMaxHealth(self, value):
        self._setNumber(2, value)

    def getLeftTrackDestroyed(self):
        return self._getBool(3)

    def setLeftTrackDestroyed(self, value):
        self._setBool(3, value)

    def getRightTrackDestroyed(self):
        return self._getBool(4)

    def setRightTrackDestroyed(self, value):
        self._setBool(4, value)

    def getRageMode(self):
        return self._getBool(5)

    def setRageMode(self, value):
        self._setBool(5, value)

    def getIsUndead(self):
        return self._getBool(6)

    def setIsUndead(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(TankPanelModel, self)._initialize()
        self._addNumberProperty('speed', 0)
        self._addNumberProperty('health', 0)
        self._addNumberProperty('maxHealth', 0)
        self._addBoolProperty('leftTrackDestroyed', False)
        self._addBoolProperty('rightTrackDestroyed', False)
        self._addBoolProperty('rageMode', False)
        self._addBoolProperty('isUndead', False)

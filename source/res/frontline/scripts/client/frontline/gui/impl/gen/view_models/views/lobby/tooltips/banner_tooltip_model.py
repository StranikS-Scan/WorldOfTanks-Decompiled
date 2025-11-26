# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/tooltips/banner_tooltip_model.py
from frameworks.wulf import ViewModel

class BannerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(BannerTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getEventStartDate(self):
        return self._getNumber(1)

    def setEventStartDate(self, value):
        self._setNumber(1, value)

    def getEventEndDate(self):
        return self._getNumber(2)

    def setEventEndDate(self, value):
        self._setNumber(2, value)

    def getRewardsCount(self):
        return self._getNumber(3)

    def setRewardsCount(self, value):
        self._setNumber(3, value)

    def getCurLevel(self):
        return self._getNumber(4)

    def setCurLevel(self, value):
        self._setNumber(4, value)

    def getMaxLevel(self):
        return self._getNumber(5)

    def setMaxLevel(self, value):
        self._setNumber(5, value)

    def getCurPoints(self):
        return self._getNumber(6)

    def setCurPoints(self, value):
        self._setNumber(6, value)

    def getMaxPoints(self):
        return self._getNumber(7)

    def setMaxPoints(self, value):
        self._setNumber(7, value)

    def getVehiclesLevel(self):
        return self._getString(8)

    def setVehiclesLevel(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(BannerTooltipModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addNumberProperty('eventStartDate', 0)
        self._addNumberProperty('eventEndDate', 0)
        self._addNumberProperty('rewardsCount', 0)
        self._addNumberProperty('curLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addNumberProperty('curPoints', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addStringProperty('vehiclesLevel', '')

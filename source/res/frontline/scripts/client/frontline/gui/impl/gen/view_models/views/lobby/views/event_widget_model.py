# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/event_widget_model.py
from frameworks.wulf import ViewModel

class EventWidgetModel(ViewModel):
    __slots__ = ('goToProgressionScreen', 'goToCombatReservesScreen', 'goToSpecialVehicleRentScreen')

    def __init__(self, properties=12, commands=3):
        super(EventWidgetModel, self).__init__(properties=properties, commands=commands)

    def getTotalProgress(self):
        return self._getNumber(0)

    def setTotalProgress(self, value):
        self._setNumber(0, value)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getCurrentTier(self):
        return self._getNumber(2)

    def setCurrentTier(self, value):
        self._setNumber(2, value)

    def getRewardsHash(self):
        return self._getNumber(3)

    def setRewardsHash(self, value):
        self._setNumber(3, value)

    def getLastSeenRewardsHash(self):
        return self._getNumber(4)

    def setLastSeenRewardsHash(self, value):
        self._setNumber(4, value)

    def getIsRentHighlighted(self):
        return self._getBool(5)

    def setIsRentHighlighted(self, value):
        self._setBool(5, value)

    def getIsCurrentCycleActive(self):
        return self._getBool(6)

    def setIsCurrentCycleActive(self, value):
        self._setBool(6, value)

    def getIsCycleStateFinished(self):
        return self._getBool(7)

    def setIsCycleStateFinished(self, value):
        self._setBool(7, value)

    def getRentalVehicleLevel(self):
        return self._getString(8)

    def setRentalVehicleLevel(self, value):
        self._setString(8, value)

    def getCombatReservesPoints(self):
        return self._getNumber(9)

    def setCombatReservesPoints(self, value):
        self._setNumber(9, value)

    def getIsMaxLevel(self):
        return self._getBool(10)

    def setIsMaxLevel(self, value):
        self._setBool(10, value)

    def getIsSelectedSuitableVehicle(self):
        return self._getBool(11)

    def setIsSelectedSuitableVehicle(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(EventWidgetModel, self)._initialize()
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('currentTier', 0)
        self._addNumberProperty('rewardsHash', 0)
        self._addNumberProperty('lastSeenRewardsHash', 0)
        self._addBoolProperty('isRentHighlighted', False)
        self._addBoolProperty('isCurrentCycleActive', False)
        self._addBoolProperty('isCycleStateFinished', False)
        self._addStringProperty('rentalVehicleLevel', '')
        self._addNumberProperty('combatReservesPoints', 0)
        self._addBoolProperty('isMaxLevel', False)
        self._addBoolProperty('isSelectedSuitableVehicle', False)
        self.goToProgressionScreen = self._addCommand('goToProgressionScreen')
        self.goToCombatReservesScreen = self._addCommand('goToCombatReservesScreen')
        self.goToSpecialVehicleRentScreen = self._addCommand('goToSpecialVehicleRentScreen')

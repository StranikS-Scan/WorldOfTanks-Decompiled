# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/mapbox_progression_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class MapboxProgressionModel(ViewModel):
    __slots__ = ('onShowInfo', 'onSelectMapboxBattle', 'onShowSurvey', 'onTakeReward', 'onRemoveBubble', 'onClose', 'onAnimationEnded')

    def __init__(self, properties=12, commands=7):
        super(MapboxProgressionModel, self).__init__(properties=properties, commands=commands)

    def getIsOverlapped(self):
        return self._getBool(0)

    def setIsOverlapped(self, value):
        self._setBool(0, value)

    def getIsDataSynced(self):
        return self._getBool(1)

    def setIsDataSynced(self, value):
        self._setBool(1, value)

    def getMaps(self):
        return self._getArray(2)

    def setMaps(self, value):
        self._setArray(2, value)

    def getProgressionRewards(self):
        return self._getArray(3)

    def setProgressionRewards(self, value):
        self._setArray(3, value)

    def getIsMapboxModeSelected(self):
        return self._getBool(4)

    def setIsMapboxModeSelected(self, value):
        self._setBool(4, value)

    def getIsError(self):
        return self._getBool(5)

    def setIsError(self, value):
        self._setBool(5, value)

    def getPrevTotalBattlesPlayed(self):
        return self._getNumber(6)

    def setPrevTotalBattlesPlayed(self, value):
        self._setNumber(6, value)

    def getTotalBattlesPlayed(self):
        return self._getNumber(7)

    def setTotalBattlesPlayed(self, value):
        self._setNumber(7, value)

    def getTotalBattles(self):
        return self._getNumber(8)

    def setTotalBattles(self, value):
        self._setNumber(8, value)

    def getStartEvent(self):
        return self._getNumber(9)

    def setStartEvent(self, value):
        self._setNumber(9, value)

    def getEndEvent(self):
        return self._getNumber(10)

    def setEndEvent(self, value):
        self._setNumber(10, value)

    def getTimeTillProgressionRestart(self):
        return self._getString(11)

    def setTimeTillProgressionRestart(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(MapboxProgressionModel, self)._initialize()
        self._addBoolProperty('isOverlapped', False)
        self._addBoolProperty('isDataSynced', False)
        self._addArrayProperty('maps', Array())
        self._addArrayProperty('progressionRewards', Array())
        self._addBoolProperty('isMapboxModeSelected', False)
        self._addBoolProperty('isError', False)
        self._addNumberProperty('prevTotalBattlesPlayed', 0)
        self._addNumberProperty('totalBattlesPlayed', 0)
        self._addNumberProperty('totalBattles', 0)
        self._addNumberProperty('startEvent', 0)
        self._addNumberProperty('endEvent', 0)
        self._addStringProperty('timeTillProgressionRestart', '')
        self.onShowInfo = self._addCommand('onShowInfo')
        self.onSelectMapboxBattle = self._addCommand('onSelectMapboxBattle')
        self.onShowSurvey = self._addCommand('onShowSurvey')
        self.onTakeReward = self._addCommand('onTakeReward')
        self.onRemoveBubble = self._addCommand('onRemoveBubble')
        self.onClose = self._addCommand('onClose')
        self.onAnimationEnded = self._addCommand('onAnimationEnded')

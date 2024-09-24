# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/mapbox_progression_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class MapboxProgressionModel(ViewModel):
    __slots__ = ('onShowInfo', 'onSelectMapboxBattle', 'onShowSurvey', 'onRemoveBubble', 'onClose', 'onAnimationEnded')

    def __init__(self, properties=14, commands=6):
        super(MapboxProgressionModel, self).__init__(properties=properties, commands=commands)

    def getIsOverlapped(self):
        return self._getBool(0)

    def setIsOverlapped(self, value):
        self._setBool(0, value)

    def getIsDataSynced(self):
        return self._getBool(1)

    def setIsDataSynced(self, value):
        self._setBool(1, value)

    def getIsMapboxModeSelected(self):
        return self._getBool(2)

    def setIsMapboxModeSelected(self, value):
        self._setBool(2, value)

    def getIsError(self):
        return self._getBool(3)

    def setIsError(self, value):
        self._setBool(3, value)

    def getHasInfoPage(self):
        return self._getBool(4)

    def setHasInfoPage(self, value):
        self._setBool(4, value)

    def getMaps(self):
        return self._getArray(5)

    def setMaps(self, value):
        self._setArray(5, value)

    def getProgressionRewards(self):
        return self._getArray(6)

    def setProgressionRewards(self, value):
        self._setArray(6, value)

    def getRating(self):
        return self._getNumber(7)

    def setRating(self, value):
        self._setNumber(7, value)

    def getPrevTotalBattlesPlayed(self):
        return self._getNumber(8)

    def setPrevTotalBattlesPlayed(self, value):
        self._setNumber(8, value)

    def getTotalBattlesPlayed(self):
        return self._getNumber(9)

    def setTotalBattlesPlayed(self, value):
        self._setNumber(9, value)

    def getTotalBattles(self):
        return self._getNumber(10)

    def setTotalBattles(self, value):
        self._setNumber(10, value)

    def getStartEvent(self):
        return self._getNumber(11)

    def setStartEvent(self, value):
        self._setNumber(11, value)

    def getEndEvent(self):
        return self._getNumber(12)

    def setEndEvent(self, value):
        self._setNumber(12, value)

    def getTimeTillProgressionRestart(self):
        return self._getString(13)

    def setTimeTillProgressionRestart(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(MapboxProgressionModel, self)._initialize()
        self._addBoolProperty('isOverlapped', False)
        self._addBoolProperty('isDataSynced', False)
        self._addBoolProperty('isMapboxModeSelected', False)
        self._addBoolProperty('isError', False)
        self._addBoolProperty('hasInfoPage', False)
        self._addArrayProperty('maps', Array())
        self._addArrayProperty('progressionRewards', Array())
        self._addNumberProperty('rating', 0)
        self._addNumberProperty('prevTotalBattlesPlayed', 0)
        self._addNumberProperty('totalBattlesPlayed', 0)
        self._addNumberProperty('totalBattles', 0)
        self._addNumberProperty('startEvent', 0)
        self._addNumberProperty('endEvent', 0)
        self._addStringProperty('timeTillProgressionRestart', '')
        self.onShowInfo = self._addCommand('onShowInfo')
        self.onSelectMapboxBattle = self._addCommand('onSelectMapboxBattle')
        self.onShowSurvey = self._addCommand('onShowSurvey')
        self.onRemoveBubble = self._addCommand('onRemoveBubble')
        self.onClose = self._addCommand('onClose')
        self.onAnimationEnded = self._addCommand('onAnimationEnded')

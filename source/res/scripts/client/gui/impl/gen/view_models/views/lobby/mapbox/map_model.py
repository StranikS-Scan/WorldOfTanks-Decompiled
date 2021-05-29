# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/map_model.py
from frameworks.wulf import ViewModel

class MapModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(MapModel, self).__init__(properties=properties, commands=commands)

    def getMapName(self):
        return self._getString(0)

    def setMapName(self, value):
        self._setString(0, value)

    def getMapBattles(self):
        return self._getNumber(1)

    def setMapBattles(self, value):
        self._setNumber(1, value)

    def getMapBattlesPlayed(self):
        return self._getNumber(2)

    def setMapBattlesPlayed(self, value):
        self._setNumber(2, value)

    def getMapSurveyPassed(self):
        return self._getBool(3)

    def setMapSurveyPassed(self, value):
        self._setBool(3, value)

    def getIsSurveyAvailable(self):
        return self._getBool(4)

    def setIsSurveyAvailable(self, value):
        self._setBool(4, value)

    def getRating(self):
        return self._getNumber(5)

    def setRating(self, value):
        self._setNumber(5, value)

    def getIsBubble(self):
        return self._getBool(6)

    def setIsBubble(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(MapModel, self)._initialize()
        self._addStringProperty('mapName', '')
        self._addNumberProperty('mapBattles', 0)
        self._addNumberProperty('mapBattlesPlayed', 0)
        self._addBoolProperty('mapSurveyPassed', False)
        self._addBoolProperty('isSurveyAvailable', False)
        self._addNumberProperty('rating', 0)
        self._addBoolProperty('isBubble', False)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/events/ranked/event_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel

class EventModel(BaseEventModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=1):
        super(EventModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(2)

    def setState(self, value):
        self._setString(2, value)

    def getStateTitle(self):
        return self._getResource(3)

    def setStateTitle(self, value):
        self._setResource(3, value)

    def getSeparatedStateTitle(self):
        return self._getResource(4)

    def setSeparatedStateTitle(self, value):
        self._setResource(4, value)

    def getDescription(self):
        return self._getString(5)

    def setDescription(self, value):
        self._setString(5, value)

    def getDescriptionIcon(self):
        return self._getResource(6)

    def setDescriptionIcon(self, value):
        self._setResource(6, value)

    def getStageState(self):
        return self._getString(7)

    def setStageState(self, value):
        self._setString(7, value)

    def getRankID(self):
        return self._getNumber(8)

    def setRankID(self, value):
        self._setNumber(8, value)

    def getShieldHP(self):
        return self._getNumber(9)

    def setShieldHP(self, value):
        self._setNumber(9, value)

    def getIsUnburnable(self):
        return self._getBool(10)

    def setIsUnburnable(self, value):
        self._setBool(10, value)

    def getDivisionID(self):
        return self._getNumber(11)

    def setDivisionID(self, value):
        self._setNumber(11, value)

    def getStepsBonusBattles(self):
        return self._getNumber(12)

    def setStepsBonusBattles(self, value):
        self._setNumber(12, value)

    def getEfficiencyBonusBattles(self):
        return self._getNumber(13)

    def setEfficiencyBonusBattles(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(EventModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addResourceProperty('stateTitle', R.invalid())
        self._addResourceProperty('separatedStateTitle', R.invalid())
        self._addStringProperty('description', '')
        self._addResourceProperty('descriptionIcon', R.invalid())
        self._addStringProperty('stageState', '')
        self._addNumberProperty('rankID', 0)
        self._addNumberProperty('shieldHP', 0)
        self._addBoolProperty('isUnburnable', False)
        self._addNumberProperty('divisionID', 0)
        self._addNumberProperty('stepsBonusBattles', 0)
        self._addNumberProperty('efficiencyBonusBattles', 0)

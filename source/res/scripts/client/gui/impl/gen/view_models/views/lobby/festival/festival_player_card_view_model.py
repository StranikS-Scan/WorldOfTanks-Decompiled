# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_player_card_view_model.py
from frameworks.wulf import ViewModel

class FestivalPlayerCardViewModel(ViewModel):
    __slots__ = ()

    def getBasisID(self):
        return self._getString(0)

    def setBasisID(self, value):
        self._setString(0, value)

    def getTitleID(self):
        return self._getString(1)

    def setTitleID(self, value):
        self._setString(1, value)

    def getRankID(self):
        return self._getNumber(2)

    def setRankID(self, value):
        self._setNumber(2, value)

    def getEmblemID(self):
        return self._getString(3)

    def setEmblemID(self, value):
        self._setString(3, value)

    def getDefaultEmblemID(self):
        return self._getString(4)

    def setDefaultEmblemID(self, value):
        self._setString(4, value)

    def getTriggerEmblemAnimation(self):
        return self._getBool(5)

    def setTriggerEmblemAnimation(self, value):
        self._setBool(5, value)

    def getUserName(self):
        return self._getString(6)

    def setUserName(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(FestivalPlayerCardViewModel, self)._initialize()
        self._addStringProperty('basisID', '')
        self._addStringProperty('titleID', '')
        self._addNumberProperty('rankID', 0)
        self._addStringProperty('emblemID', '')
        self._addStringProperty('defaultEmblemID', '')
        self._addBoolProperty('triggerEmblemAnimation', False)
        self._addStringProperty('userName', '')

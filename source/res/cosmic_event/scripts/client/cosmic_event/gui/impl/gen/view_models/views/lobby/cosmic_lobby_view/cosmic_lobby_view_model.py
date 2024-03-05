# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/cosmic_lobby_view/cosmic_lobby_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.progression_model import ProgressionModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringModel
from gui.impl.gen.view_models.views.lobby.missions.widget.widget_quest_model import WidgetQuestModel

class LobbyRouteEnum(Enum):
    MAIN = 'main'
    ARTEFACT = 'artefact'
    VEHICLE = 'vehicle'
    PICKUPS = 'pickups'


class CosmicLobbyViewModel(ViewModel):
    __slots__ = ('onLobbyRouteChange', 'onClose', 'onAboutEvent', 'onShopClicked')

    def __init__(self, properties=12, commands=4):
        super(CosmicLobbyViewModel, self).__init__(properties=properties, commands=commands)

    def getFadeOut(self):
        return self._getBool(0)

    def setFadeOut(self, value):
        self._setBool(0, value)

    def getCurrentProgressSectionIndex(self):
        return self._getNumber(1)

    def setCurrentProgressSectionIndex(self, value):
        self._setNumber(1, value)

    def getMarsPoints(self):
        return self._getNumber(2)

    def setMarsPoints(self, value):
        self._setNumber(2, value)

    def getMarsPointsLimit(self):
        return self._getNumber(3)

    def setMarsPointsLimit(self, value):
        self._setNumber(3, value)

    def getArtefactProgressDeltaFrom(self):
        return self._getNumber(4)

    def setArtefactProgressDeltaFrom(self, value):
        self._setNumber(4, value)

    def getMarsPointsEarnedToday(self):
        return self._getNumber(5)

    def setMarsPointsEarnedToday(self, value):
        self._setNumber(5, value)

    def getMarsPointsTodaysLimit(self):
        return self._getNumber(6)

    def setMarsPointsTodaysLimit(self, value):
        self._setNumber(6, value)

    def getLobbyRoute(self):
        return LobbyRouteEnum(self._getString(7))

    def setLobbyRoute(self, value):
        self._setString(7, value.value)

    def getIsVehicleInBattle(self):
        return self._getBool(8)

    def setIsVehicleInBattle(self, value):
        self._setBool(8, value)

    def getScoring(self):
        return self._getArray(9)

    def setScoring(self, value):
        self._setArray(9, value)

    @staticmethod
    def getScoringType():
        return ScoringModel

    def getMissions(self):
        return self._getArray(10)

    def setMissions(self, value):
        self._setArray(10, value)

    @staticmethod
    def getMissionsType():
        return WidgetQuestModel

    def getProgression(self):
        return self._getArray(11)

    def setProgression(self, value):
        self._setArray(11, value)

    @staticmethod
    def getProgressionType():
        return ProgressionModel

    def _initialize(self):
        super(CosmicLobbyViewModel, self)._initialize()
        self._addBoolProperty('fadeOut', False)
        self._addNumberProperty('currentProgressSectionIndex', 0)
        self._addNumberProperty('marsPoints', 0)
        self._addNumberProperty('marsPointsLimit', 0)
        self._addNumberProperty('artefactProgressDeltaFrom', 0)
        self._addNumberProperty('marsPointsEarnedToday', 0)
        self._addNumberProperty('marsPointsTodaysLimit', 0)
        self._addStringProperty('lobbyRoute', LobbyRouteEnum.MAIN.value)
        self._addBoolProperty('isVehicleInBattle', False)
        self._addArrayProperty('scoring', Array())
        self._addArrayProperty('missions', Array())
        self._addArrayProperty('progression', Array())
        self.onLobbyRouteChange = self._addCommand('onLobbyRouteChange')
        self.onClose = self._addCommand('onClose')
        self.onAboutEvent = self._addCommand('onAboutEvent')
        self.onShopClicked = self._addCommand('onShopClicked')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/cosmic_lobby_view/cosmic_lobby_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.medal_model import MedalModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.progression_model import ProgressionModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.rovers_model import RoversModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringModel
from gui.impl.gen.view_models.views.lobby.daily.widget_quest_model import WidgetQuestModel

class LobbyRouteEnum(Enum):
    MAIN = 'main'
    ARTEFACT = 'artefact'
    RULES = 'rules'
    PICKUPS = 'pickups'


class RoverEnum(IntEnum):
    OLD = 1
    NEW = 2


class CosmicLobbyViewModel(ViewModel):
    __slots__ = ('onLobbyRouteChange', 'onClose', 'onAboutEvent', 'onShopClicked', 'onVehicleChange')

    def __init__(self, properties=19, commands=5):
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

    def getSelectedVehicle(self):
        return RoverEnum(self._getNumber(9))

    def setSelectedVehicle(self, value):
        self._setNumber(9, value.value)

    def getSelectedVehicleResource(self):
        return self._getString(10)

    def setSelectedVehicleResource(self, value):
        self._setString(10, value)

    def getIsSomethingHappeningWithArtefact(self):
        return self._getBool(11)

    def setIsSomethingHappeningWithArtefact(self, value):
        self._setBool(11, value)

    def getLastVisitedProgressionLevel(self):
        return self._getNumber(12)

    def setLastVisitedProgressionLevel(self, value):
        self._setNumber(12, value)

    def getIsProgressionFinished(self):
        return self._getBool(13)

    def setIsProgressionFinished(self, value):
        self._setBool(13, value)

    def getMedals(self):
        return self._getArray(14)

    def setMedals(self, value):
        self._setArray(14, value)

    @staticmethod
    def getMedalsType():
        return MedalModel

    def getScoring(self):
        return self._getArray(15)

    def setScoring(self, value):
        self._setArray(15, value)

    @staticmethod
    def getScoringType():
        return ScoringModel

    def getMissions(self):
        return self._getArray(16)

    def setMissions(self, value):
        self._setArray(16, value)

    @staticmethod
    def getMissionsType():
        return WidgetQuestModel

    def getProgression(self):
        return self._getArray(17)

    def setProgression(self, value):
        self._setArray(17, value)

    @staticmethod
    def getProgressionType():
        return ProgressionModel

    def getRovers(self):
        return self._getArray(18)

    def setRovers(self, value):
        self._setArray(18, value)

    @staticmethod
    def getRoversType():
        return RoversModel

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
        self._addNumberProperty('selectedVehicle', RoverEnum.OLD.value)
        self._addStringProperty('selectedVehicleResource', '')
        self._addBoolProperty('isSomethingHappeningWithArtefact', False)
        self._addNumberProperty('lastVisitedProgressionLevel', 0)
        self._addBoolProperty('isProgressionFinished', False)
        self._addArrayProperty('medals', Array())
        self._addArrayProperty('scoring', Array())
        self._addArrayProperty('missions', Array())
        self._addArrayProperty('progression', Array())
        self._addArrayProperty('rovers', Array())
        self.onLobbyRouteChange = self._addCommand('onLobbyRouteChange')
        self.onClose = self._addCommand('onClose')
        self.onAboutEvent = self._addCommand('onAboutEvent')
        self.onShopClicked = self._addCommand('onShopClicked')
        self.onVehicleChange = self._addCommand('onVehicleChange')

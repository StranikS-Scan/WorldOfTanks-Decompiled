# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_progression_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.ranked.division_model import DivisionModel
from gui.impl.gen.view_models.views.lobby.ranked.ranked_statistics_model import RankedStatisticsModel

class States(IntEnum):
    PROGRESSION = 0
    FINAL = 1


class RankedProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onAbout', 'onSelectDivision', 'onOpenFinalState', 'onSelectReward')

    def __init__(self, properties=14, commands=5):
        super(RankedProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def divisions(self):
        return self._getViewModel(0)

    @staticmethod
    def getDivisionsType():
        return DivisionModel

    @property
    def statistics(self):
        return self._getViewModel(1)

    @staticmethod
    def getStatisticsType():
        return RankedStatisticsModel

    def getStartTimestamp(self):
        return self._getNumber(2)

    def setStartTimestamp(self, value):
        self._setNumber(2, value)

    def getEndTimestamp(self):
        return self._getNumber(3)

    def setEndTimestamp(self, value):
        self._setNumber(3, value)

    def getServerTimestamp(self):
        return self._getNumber(4)

    def setServerTimestamp(self, value):
        self._setNumber(4, value)

    def getCurrentDivisionID(self):
        return self._getNumber(5)

    def setCurrentDivisionID(self, value):
        self._setNumber(5, value)

    def getCurrentRank(self):
        return self._getNumber(6)

    def setCurrentRank(self, value):
        self._setNumber(6, value)

    def getCurrentStep(self):
        return self._getNumber(7)

    def setCurrentStep(self, value):
        self._setNumber(7, value)

    def getMaxRank(self):
        return self._getNumber(8)

    def setMaxRank(self, value):
        self._setNumber(8, value)

    def getSelectedDivision(self):
        return self._getNumber(9)

    def setSelectedDivision(self, value):
        self._setNumber(9, value)

    def getSelectedState(self):
        return States(self._getNumber(10))

    def setSelectedState(self, value):
        self._setNumber(10, value.value)

    def getIsFinalStateAvailable(self):
        return self._getBool(11)

    def setIsFinalStateAvailable(self, value):
        self._setBool(11, value)

    def getBonusBattles(self):
        return self._getNumber(12)

    def setBonusBattles(self, value):
        self._setNumber(12, value)

    def getHasRewardToSelect(self):
        return self._getBool(13)

    def setHasRewardToSelect(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(RankedProgressionViewModel, self)._initialize()
        self._addViewModelProperty('divisions', UserListModel())
        self._addViewModelProperty('statistics', RankedStatisticsModel())
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addNumberProperty('serverTimestamp', 0)
        self._addNumberProperty('currentDivisionID', 0)
        self._addNumberProperty('currentRank', 0)
        self._addNumberProperty('currentStep', 0)
        self._addNumberProperty('maxRank', 0)
        self._addNumberProperty('selectedDivision', 0)
        self._addNumberProperty('selectedState')
        self._addBoolProperty('isFinalStateAvailable', True)
        self._addNumberProperty('bonusBattles', 0)
        self._addBoolProperty('hasRewardToSelect', False)
        self.onClose = self._addCommand('onClose')
        self.onAbout = self._addCommand('onAbout')
        self.onSelectDivision = self._addCommand('onSelectDivision')
        self.onOpenFinalState = self._addCommand('onOpenFinalState')
        self.onSelectReward = self._addCommand('onSelectReward')

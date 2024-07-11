# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_progression_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from races.gui.impl.gen.view_models.views.lobby.progress_level_model import ProgressLevelModel
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.quests_view_model import QuestsViewModel

class RacesProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutEvent')

    def __init__(self, properties=5, commands=2):
        super(RacesProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def quests(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestsType():
        return QuestsViewModel

    def getCurProgressPoints(self):
        return self._getNumber(1)

    def setCurProgressPoints(self, value):
        self._setNumber(1, value)

    def getPrevProgressPoints(self):
        return self._getNumber(2)

    def setPrevProgressPoints(self, value):
        self._setNumber(2, value)

    def getPointsForLevel(self):
        return self._getNumber(3)

    def setPointsForLevel(self, value):
        self._setNumber(3, value)

    def getProgressLevels(self):
        return self._getArray(4)

    def setProgressLevels(self, value):
        self._setArray(4, value)

    @staticmethod
    def getProgressLevelsType():
        return ProgressLevelModel

    def _initialize(self):
        super(RacesProgressionViewModel, self)._initialize()
        self._addViewModelProperty('quests', QuestsViewModel())
        self._addNumberProperty('curProgressPoints', 0)
        self._addNumberProperty('prevProgressPoints', 0)
        self._addNumberProperty('pointsForLevel', 0)
        self._addArrayProperty('progressLevels', Array())
        self.onClose = self._addCommand('onClose')
        self.onAboutEvent = self._addCommand('onAboutEvent')

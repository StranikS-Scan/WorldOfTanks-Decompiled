# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/entry_point_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_model import ChapterModel

class ProgressState(Enum):
    ACTIVE = 'active'
    NORESETTEDBRANCHES = 'noResettedBranches'
    NEEDVEHICLETORESET = 'needVehicleToReset'
    CHAPTERNOTCHOSEN = 'chapterNotChosen'
    ALLCHAPTERSCOMPLETED = 'allChaptersCompleted'
    PAUSED = 'paused'
    NOTAVAILABLE = 'notAvailable'


class EntryPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(EntryPointTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentChapter(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentChapterType():
        return ChapterModel

    def getIsFirstEntry(self):
        return self._getBool(1)

    def setIsFirstEntry(self, value):
        self._setBool(1, value)

    def getPoints(self):
        return self._getNumber(2)

    def setPoints(self, value):
        self._setNumber(2, value)

    def getVehicleToReset(self):
        return self._getNumber(3)

    def setVehicleToReset(self, value):
        self._setNumber(3, value)

    def getVehicleCount(self):
        return self._getNumber(4)

    def setVehicleCount(self, value):
        self._setNumber(4, value)

    def getProgressState(self):
        return ProgressState(self._getString(5))

    def setProgressState(self, value):
        self._setString(5, value.value)

    def _initialize(self):
        super(EntryPointTooltipModel, self)._initialize()
        self._addViewModelProperty('currentChapter', ChapterModel())
        self._addBoolProperty('isFirstEntry', False)
        self._addNumberProperty('points', 0)
        self._addNumberProperty('vehicleToReset', 0)
        self._addNumberProperty('vehicleCount', 0)
        self._addStringProperty('progressState', ProgressState.ACTIVE.value)

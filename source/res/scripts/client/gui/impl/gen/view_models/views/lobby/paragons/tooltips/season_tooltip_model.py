# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/season_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_status_model import ChapterStatusModel

class SeasonTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SeasonTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def chapterStatus(self):
        return self._getViewModel(0)

    @staticmethod
    def getChapterStatusType():
        return ChapterStatusModel

    def getChapterId(self):
        return self._getNumber(1)

    def setChapterId(self, value):
        self._setNumber(1, value)

    def getVehicleCount(self):
        return self._getNumber(2)

    def setVehicleCount(self, value):
        self._setNumber(2, value)

    def getNecessaryVehicleCount(self):
        return self._getNumber(3)

    def setNecessaryVehicleCount(self, value):
        self._setNumber(3, value)

    def getIsAllRewardsClaimed(self):
        return self._getBool(4)

    def setIsAllRewardsClaimed(self, value):
        self._setBool(4, value)

    def getTimeStamp(self):
        return self._getNumber(5)

    def setTimeStamp(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(SeasonTooltipModel, self)._initialize()
        self._addViewModelProperty('chapterStatus', ChapterStatusModel())
        self._addNumberProperty('chapterId', 1)
        self._addNumberProperty('vehicleCount', 0)
        self._addNumberProperty('necessaryVehicleCount', 0)
        self._addBoolProperty('isAllRewardsClaimed', False)
        self._addNumberProperty('timeStamp', 0)

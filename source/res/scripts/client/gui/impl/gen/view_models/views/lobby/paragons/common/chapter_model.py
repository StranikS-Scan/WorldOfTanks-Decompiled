# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/common/chapter_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_status_model import ChapterStatusModel
from gui.impl.gen.view_models.views.lobby.paragons.common.level_model import LevelModel

class ChapterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(ChapterModel, self).__init__(properties=properties, commands=commands)

    @property
    def chapterStatus(self):
        return self._getViewModel(0)

    @staticmethod
    def getChapterStatusType():
        return ChapterStatusModel

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIsCompleted(self):
        return self._getBool(3)

    def setIsCompleted(self, value):
        self._setBool(3, value)

    def getChapterLevel(self):
        return self._getNumber(4)

    def setChapterLevel(self, value):
        self._setNumber(4, value)

    def getPoints(self):
        return self._getNumber(5)

    def setPoints(self, value):
        self._setNumber(5, value)

    def getIsAllRewardsClaimed(self):
        return self._getBool(6)

    def setIsAllRewardsClaimed(self, value):
        self._setBool(6, value)

    def getFinalVehicleCDs(self):
        return self._getArray(7)

    def setFinalVehicleCDs(self, value):
        self._setArray(7, value)

    @staticmethod
    def getFinalVehicleCDsType():
        return int

    def getLevels(self):
        return self._getArray(8)

    def setLevels(self, value):
        self._setArray(8, value)

    @staticmethod
    def getLevelsType():
        return LevelModel

    def _initialize(self):
        super(ChapterModel, self)._initialize()
        self._addViewModelProperty('chapterStatus', ChapterStatusModel())
        self._addNumberProperty('id', 1)
        self._addStringProperty('name', '')
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('chapterLevel', 0)
        self._addNumberProperty('points', 0)
        self._addBoolProperty('isAllRewardsClaimed', False)
        self._addArrayProperty('finalVehicleCDs', Array())
        self._addArrayProperty('levels', Array())

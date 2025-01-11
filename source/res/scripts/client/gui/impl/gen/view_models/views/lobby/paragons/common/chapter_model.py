# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/common/chapter_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.level_model import LevelModel

class StatusList(Enum):
    DEFAULT = 'default'
    DISABLED = 'disabled'
    ACTIVE = 'active'
    FINISHED = 'finished'
    ANNOUNCEMENT = 'announcement'


class ChapterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(ChapterModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getStatus(self):
        return StatusList(self._getString(2))

    def setStatus(self, value):
        self._setString(2, value.value)

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

    def getLevels(self):
        return self._getArray(7)

    def setLevels(self, value):
        self._setArray(7, value)

    @staticmethod
    def getLevelsType():
        return LevelModel

    def _initialize(self):
        super(ChapterModel, self)._initialize()
        self._addNumberProperty('id', 1)
        self._addStringProperty('name', '')
        self._addStringProperty('status', StatusList.DEFAULT.value)
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('chapterLevel', 0)
        self._addNumberProperty('points', 0)
        self._addBoolProperty('isAllRewardsClaimed', False)
        self._addArrayProperty('levels', Array())

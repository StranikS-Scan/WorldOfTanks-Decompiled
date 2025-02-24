# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/chapter_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class ChapterStates(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    NOTSTARTED = 'notStarted'
    DISABLED = 'disabled'


class ChapterType(Enum):
    DEFAULT = 'default'
    MARATHON = 'marathon'
    RESOURCE = 'resource'


class ChapterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(ChapterModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getChapterID(self):
        return self._getNumber(1)

    def setChapterID(self, value):
        self._setNumber(1, value)

    def getStyleName(self):
        return self._getString(2)

    def setStyleName(self, value):
        self._setString(2, value)

    def getTankman(self):
        return self._getString(3)

    def setTankman(self, value):
        self._setString(3, value)

    def getCurrentLevel(self):
        return self._getNumber(4)

    def setCurrentLevel(self, value):
        self._setNumber(4, value)

    def getChapterState(self):
        return ChapterStates(self._getString(5))

    def setChapterState(self, value):
        self._setString(5, value.value)

    def getIsVehicleInHangar(self):
        return self._getBool(6)

    def setIsVehicleInHangar(self, value):
        self._setBool(6, value)

    def getIsBought(self):
        return self._getBool(7)

    def setIsBought(self, value):
        self._setBool(7, value)

    def getLevelProgression(self):
        return self._getNumber(8)

    def setLevelProgression(self, value):
        self._setNumber(8, value)

    def getFinalReward(self):
        return self._getString(9)

    def setFinalReward(self, value):
        self._setString(9, value)

    def getChapterType(self):
        return ChapterType(self._getString(10))

    def setChapterType(self, value):
        self._setString(10, value.value)

    def _initialize(self):
        super(ChapterModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('styleName', '')
        self._addStringProperty('tankman', '')
        self._addNumberProperty('currentLevel', 0)
        self._addStringProperty('chapterState')
        self._addBoolProperty('isVehicleInHangar', False)
        self._addBoolProperty('isBought', False)
        self._addNumberProperty('levelProgression', 0)
        self._addStringProperty('finalReward', '')
        self._addStringProperty('chapterType')

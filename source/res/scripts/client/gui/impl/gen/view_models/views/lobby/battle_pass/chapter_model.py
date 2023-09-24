# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/chapter_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class ChapterStates(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    NOTSTARTED = 'notStarted'


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

    def getCurrentLevel(self):
        return self._getNumber(3)

    def setCurrentLevel(self, value):
        self._setNumber(3, value)

    def getChapterState(self):
        return ChapterStates(self._getString(4))

    def setChapterState(self, value):
        self._setString(4, value.value)

    def getIsVehicleInHangar(self):
        return self._getBool(5)

    def setIsVehicleInHangar(self, value):
        self._setBool(5, value)

    def getIsBought(self):
        return self._getBool(6)

    def setIsBought(self, value):
        self._setBool(6, value)

    def getLevelProgression(self):
        return self._getNumber(7)

    def setLevelProgression(self, value):
        self._setNumber(7, value)

    def getIsExtra(self):
        return self._getBool(8)

    def setIsExtra(self, value):
        self._setBool(8, value)

    def getFreeFinalRewards(self):
        return self._getArray(9)

    def setFreeFinalRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getFreeFinalRewardsType():
        return unicode

    def getPaidFinalRewards(self):
        return self._getArray(10)

    def setPaidFinalRewards(self, value):
        self._setArray(10, value)

    @staticmethod
    def getPaidFinalRewardsType():
        return unicode

    def _initialize(self):
        super(ChapterModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('styleName', '')
        self._addNumberProperty('currentLevel', 0)
        self._addStringProperty('chapterState')
        self._addBoolProperty('isVehicleInHangar', False)
        self._addBoolProperty('isBought', False)
        self._addNumberProperty('levelProgression', 0)
        self._addBoolProperty('isExtra', False)
        self._addArrayProperty('freeFinalRewards', Array())
        self._addArrayProperty('paidFinalRewards', Array())

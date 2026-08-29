# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/chapter_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class ChapterStates(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    NOTSTARTED = 'notStarted'


class FinalRewardTypes(Enum):
    VEHICLE = 'vehicle'
    VEHICLESTYLE = 'vehicleStyle'
    STYLE = 'style'
    TANKMAN = 'tankman'
    ATTACHMENTSSET = 'attachmentsSet'
    POSTPROGRESSION = 'postProgression'


class ChapterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
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

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getMaxLevel(self):
        return self._getNumber(3)

    def setMaxLevel(self, value):
        self._setNumber(3, value)

    def getCyclesCompletedCount(self):
        return self._getNumber(4)

    def setCyclesCompletedCount(self, value):
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

    def getIsExtra(self):
        return self._getBool(9)

    def setIsExtra(self, value):
        self._setBool(9, value)

    def getIsPostProgression(self):
        return self._getBool(10)

    def setIsPostProgression(self, value):
        self._setBool(10, value)

    def getTankmenScreenID(self):
        return self._getNumber(11)

    def setTankmenScreenID(self, value):
        self._setNumber(11, value)

    def getFinalRewardType(self):
        return FinalRewardTypes(self._getString(12))

    def setFinalRewardType(self, value):
        self._setString(12, value.value)

    def getStyleName(self):
        return self._getString(13)

    def setStyleName(self, value):
        self._setString(13, value)

    def getTankmanNames(self):
        return self._getArray(14)

    def setTankmanNames(self, value):
        self._setArray(14, value)

    @staticmethod
    def getTankmanNamesType():
        return unicode

    def getAttachmentsSetName(self):
        return self._getString(15)

    def setAttachmentsSetName(self, value):
        self._setString(15, value)

    def getExpireTime(self):
        return self._getNumber(16)

    def setExpireTime(self, value):
        self._setNumber(16, value)

    def getTimeLeft(self):
        return self._getNumber(17)

    def setTimeLeft(self, value):
        self._setNumber(17, value)

    def getChapterRewardsCount(self):
        return self._getNumber(18)

    def setChapterRewardsCount(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(ChapterModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('chapterID', 0)
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addNumberProperty('cyclesCompletedCount', 0)
        self._addStringProperty('chapterState')
        self._addBoolProperty('isVehicleInHangar', False)
        self._addBoolProperty('isBought', False)
        self._addNumberProperty('levelProgression', 0)
        self._addBoolProperty('isExtra', False)
        self._addBoolProperty('isPostProgression', False)
        self._addNumberProperty('tankmenScreenID', 0)
        self._addStringProperty('finalRewardType')
        self._addStringProperty('styleName', '')
        self._addArrayProperty('tankmanNames', Array())
        self._addStringProperty('attachmentsSetName', '')
        self._addNumberProperty('expireTime', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('chapterRewardsCount', 0)

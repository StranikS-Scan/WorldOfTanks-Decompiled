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


class FinalRewardTypes(Enum):
    VEHICLE = 'vehicle'
    STYLE = 'style'
    TANKMAN = 'tankman'


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

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getChapterState(self):
        return ChapterStates(self._getString(3))

    def setChapterState(self, value):
        self._setString(3, value.value)

    def getIsVehicleInHangar(self):
        return self._getBool(4)

    def setIsVehicleInHangar(self, value):
        self._setBool(4, value)

    def getIsBought(self):
        return self._getBool(5)

    def setIsBought(self, value):
        self._setBool(5, value)

    def getLevelProgression(self):
        return self._getNumber(6)

    def setLevelProgression(self, value):
        self._setNumber(6, value)

    def getIsExtra(self):
        return self._getBool(7)

    def setIsExtra(self, value):
        self._setBool(7, value)

    def getFinalRewardType(self):
        return FinalRewardTypes(self._getString(8))

    def setFinalRewardType(self, value):
        self._setString(8, value.value)

    def getStyleName(self):
        return self._getString(9)

    def setStyleName(self, value):
        self._setString(9, value)

    def getTankmanNames(self):
        return self._getArray(10)

    def setTankmanNames(self, value):
        self._setArray(10, value)

    @staticmethod
    def getTankmanNamesType():
        return unicode

    def _initialize(self):
        super(ChapterModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('chapterID', 0)
        self._addNumberProperty('currentLevel', 0)
        self._addStringProperty('chapterState')
        self._addBoolProperty('isVehicleInHangar', False)
        self._addBoolProperty('isBought', False)
        self._addNumberProperty('levelProgression', 0)
        self._addBoolProperty('isExtra', False)
        self._addStringProperty('finalRewardType')
        self._addStringProperty('styleName', '')
        self._addArrayProperty('tankmanNames', Array())

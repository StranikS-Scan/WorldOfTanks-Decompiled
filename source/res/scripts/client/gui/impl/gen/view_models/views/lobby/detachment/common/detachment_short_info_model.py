# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_short_info_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_instructor_model import DetachmentShortInfoInstructorModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class DetachmentShortInfoModel(ViewModel):
    __slots__ = ('onProgressBarAnimComplete',)

    def __init__(self, properties=31, commands=1):
        super(DetachmentShortInfoModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getCommanderIcon(self):
        return self._getResource(2)

    def setCommanderIcon(self, value):
        self._setResource(2, value)

    def getCommanderIconName(self):
        return self._getString(3)

    def setCommanderIconName(self, value):
        self._setString(3, value)

    def getIsUnique(self):
        return self._getBool(4)

    def setIsUnique(self, value):
        self._setBool(4, value)

    def getHasCrewSkin(self):
        return self._getBool(5)

    def setHasCrewSkin(self, value):
        self._setBool(5, value)

    def getTeamMembersIcon(self):
        return self._getResource(6)

    def setTeamMembersIcon(self, value):
        self._setResource(6, value)

    def getLevel(self):
        return self._getNumber(7)

    def setLevel(self, value):
        self._setNumber(7, value)

    def getNextLevel(self):
        return self._getNumber(8)

    def setNextLevel(self, value):
        self._setNumber(8, value)

    def getPrevLevel(self):
        return self._getNumber(9)

    def setPrevLevel(self, value):
        self._setNumber(9, value)

    def getMaxLevel(self):
        return self._getNumber(10)

    def setMaxLevel(self, value):
        self._setNumber(10, value)

    def getLevelIconId(self):
        return self._getString(11)

    def setLevelIconId(self, value):
        self._setString(11, value)

    def getNextLevelIconId(self):
        return self._getString(12)

    def setNextLevelIconId(self, value):
        self._setString(12, value)

    def getPrevLevelIconId(self):
        return self._getString(13)

    def setPrevLevelIconId(self, value):
        self._setString(13, value)

    def getName(self):
        return self._getString(14)

    def setName(self, value):
        self._setString(14, value)

    def getRank(self):
        return self._getString(15)

    def setRank(self, value):
        self._setString(15, value)

    def getMastery(self):
        return self._getResource(16)

    def setMastery(self, value):
        self._setResource(16, value)

    def getPrevMastery(self):
        return self._getResource(17)

    def setPrevMastery(self, value):
        self._setResource(17, value)

    def getIsXpDown(self):
        return self._getBool(18)

    def setIsXpDown(self, value):
        self._setBool(18, value)

    def getProgressValue(self):
        return self._getNumber(19)

    def setProgressValue(self, value):
        self._setNumber(19, value)

    def getProgressMax(self):
        return self._getNumber(20)

    def setProgressMax(self, value):
        self._setNumber(20, value)

    def getProgressDeltaFrom(self):
        return self._getNumber(21)

    def setProgressDeltaFrom(self, value):
        self._setNumber(21, value)

    def getStripeIcon(self):
        return self._getResource(22)

    def setStripeIcon(self, value):
        self._setResource(22, value)

    def getIsMaxLevel(self):
        return self._getBool(23)

    def setIsMaxLevel(self, value):
        self._setBool(23, value)

    def getIsElite(self):
        return self._getBool(24)

    def setIsElite(self, value):
        self._setBool(24, value)

    def getNextLevelIsElite(self):
        return self._getBool(25)

    def setNextLevelIsElite(self, value):
        self._setBool(25, value)

    def getHasDog(self):
        return self._getBool(26)

    def setHasDog(self, value):
        self._setBool(26, value)

    def getDogTooltipHeader(self):
        return self._getString(27)

    def setDogTooltipHeader(self, value):
        self._setString(27, value)

    def getDogTooltipText(self):
        return self._getString(28)

    def setDogTooltipText(self, value):
        self._setString(28, value)

    def getNation(self):
        return self._getString(29)

    def setNation(self, value):
        self._setString(29, value)

    def getInstructorsList(self):
        return self._getArray(30)

    def setInstructorsList(self, value):
        self._setArray(30, value)

    def _initialize(self):
        super(DetachmentShortInfoModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addNumberProperty('id', 0)
        self._addResourceProperty('commanderIcon', R.invalid())
        self._addStringProperty('commanderIconName', '')
        self._addBoolProperty('isUnique', False)
        self._addBoolProperty('hasCrewSkin', False)
        self._addResourceProperty('teamMembersIcon', R.invalid())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('nextLevel', 0)
        self._addNumberProperty('prevLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addStringProperty('levelIconId', '')
        self._addStringProperty('nextLevelIconId', '')
        self._addStringProperty('prevLevelIconId', '')
        self._addStringProperty('name', '')
        self._addStringProperty('rank', '')
        self._addResourceProperty('mastery', R.invalid())
        self._addResourceProperty('prevMastery', R.invalid())
        self._addBoolProperty('isXpDown', False)
        self._addNumberProperty('progressValue', 0)
        self._addNumberProperty('progressMax', 0)
        self._addNumberProperty('progressDeltaFrom', -1)
        self._addResourceProperty('stripeIcon', R.invalid())
        self._addBoolProperty('isMaxLevel', False)
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('nextLevelIsElite', False)
        self._addBoolProperty('hasDog', False)
        self._addStringProperty('dogTooltipHeader', '')
        self._addStringProperty('dogTooltipText', '')
        self._addStringProperty('nation', '')
        self._addArrayProperty('instructorsList', Array())
        self.onProgressBarAnimComplete = self._addCommand('onProgressBarAnimComplete')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_rewards_renderer_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearRewardsRendererModel(NyWithRomanNumbersModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(NewYearRewardsRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardsGroup(self):
        return self._getViewModel(1)

    def getIdx(self):
        return self._getNumber(2)

    def setIdx(self, value):
        self._setNumber(2, value)

    def getLevelText(self):
        return self._getString(3)

    def setLevelText(self, value):
        self._setString(3, value)

    def getIsLevelAchieved(self):
        return self._getBool(4)

    def setIsLevelAchieved(self, value):
        self._setBool(4, value)

    def getIsCurrentLevel(self):
        return self._getBool(5)

    def setIsCurrentLevel(self, value):
        self._setBool(5, value)

    def getIsLastLevel(self):
        return self._getBool(6)

    def setIsLastLevel(self, value):
        self._setBool(6, value)

    def getIsNextAfterCurrentLevel(self):
        return self._getBool(7)

    def setIsNextAfterCurrentLevel(self, value):
        self._setBool(7, value)

    def getShowTalisman(self):
        return self._getBool(8)

    def setShowTalisman(self, value):
        self._setBool(8, value)

    def getShowTankwoman(self):
        return self._getBool(9)

    def setShowTankwoman(self, value):
        self._setBool(9, value)

    def getIsTankwomanApplied(self):
        return self._getBool(10)

    def setIsTankwomanApplied(self, value):
        self._setBool(10, value)

    def getIsTankwomanLocked(self):
        return self._getBool(11)

    def setIsTankwomanLocked(self, value):
        self._setBool(11, value)

    def getIsTalismanApplied(self):
        return self._getBool(12)

    def setIsTalismanApplied(self, value):
        self._setBool(12, value)

    def getIsTalismanLocked(self):
        return self._getBool(13)

    def setIsTalismanLocked(self, value):
        self._setBool(13, value)

    def getIsNewYearEnabled(self):
        return self._getBool(14)

    def setIsNewYearEnabled(self, value):
        self._setBool(14, value)

    def getIsMaxReachedLevel(self):
        return self._getBool(15)

    def setIsMaxReachedLevel(self, value):
        self._setBool(15, value)

    def getShowTank(self):
        return self._getBool(16)

    def setShowTank(self, value):
        self._setBool(16, value)

    def getTankLevel(self):
        return self._getNumber(17)

    def setTankLevel(self, value):
        self._setNumber(17, value)

    def getTalismanImg(self):
        return self._getString(18)

    def setTalismanImg(self, value):
        self._setString(18, value)

    def _initialize(self):
        super(NewYearRewardsRendererModel, self)._initialize()
        self._addViewModelProperty('rewardsGroup', UserListModel())
        self._addNumberProperty('idx', 0)
        self._addStringProperty('levelText', '')
        self._addBoolProperty('isLevelAchieved', False)
        self._addBoolProperty('isCurrentLevel', False)
        self._addBoolProperty('isLastLevel', False)
        self._addBoolProperty('isNextAfterCurrentLevel', False)
        self._addBoolProperty('showTalisman', False)
        self._addBoolProperty('showTankwoman', False)
        self._addBoolProperty('isTankwomanApplied', False)
        self._addBoolProperty('isTankwomanLocked', False)
        self._addBoolProperty('isTalismanApplied', False)
        self._addBoolProperty('isTalismanLocked', False)
        self._addBoolProperty('isNewYearEnabled', True)
        self._addBoolProperty('isMaxReachedLevel', False)
        self._addBoolProperty('showTank', False)
        self._addNumberProperty('tankLevel', 0)
        self._addStringProperty('talismanImg', '')

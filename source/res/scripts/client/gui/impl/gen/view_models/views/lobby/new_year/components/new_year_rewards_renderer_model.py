# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_rewards_renderer_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearRewardsRendererModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(NewYearRewardsRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardsGroup(self):
        return self._getViewModel(0)

    def getIdx(self):
        return self._getNumber(1)

    def setIdx(self, value):
        self._setNumber(1, value)

    def getLevelText(self):
        return self._getString(2)

    def setLevelText(self, value):
        self._setString(2, value)

    def getIsLevelAchieved(self):
        return self._getBool(3)

    def setIsLevelAchieved(self, value):
        self._setBool(3, value)

    def getIsCurrentLevel(self):
        return self._getBool(4)

    def setIsCurrentLevel(self, value):
        self._setBool(4, value)

    def getIsLastLevel(self):
        return self._getBool(5)

    def setIsLastLevel(self, value):
        self._setBool(5, value)

    def getIsNextAfterCurrentLevel(self):
        return self._getBool(6)

    def setIsNextAfterCurrentLevel(self, value):
        self._setBool(6, value)

    def getShowTankwomanTalisman(self):
        return self._getBool(7)

    def setShowTankwomanTalisman(self, value):
        self._setBool(7, value)

    def getIsTankwomanApplied(self):
        return self._getBool(8)

    def setIsTankwomanApplied(self, value):
        self._setBool(8, value)

    def getIsTankwomanLocked(self):
        return self._getBool(9)

    def setIsTankwomanLocked(self, value):
        self._setBool(9, value)

    def getIsTalismanApplied(self):
        return self._getBool(10)

    def setIsTalismanApplied(self, value):
        self._setBool(10, value)

    def getIsTalismanLocked(self):
        return self._getBool(11)

    def setIsTalismanLocked(self, value):
        self._setBool(11, value)

    def getIsNewYearEnabled(self):
        return self._getBool(12)

    def setIsNewYearEnabled(self, value):
        self._setBool(12, value)

    def getIsMaxReachedLevel(self):
        return self._getBool(13)

    def setIsMaxReachedLevel(self, value):
        self._setBool(13, value)

    def getShowTank(self):
        return self._getBool(14)

    def setShowTank(self, value):
        self._setBool(14, value)

    def getTankLevel(self):
        return self._getNumber(15)

    def setTankLevel(self, value):
        self._setNumber(15, value)

    def getTalismanImg(self):
        return self._getString(16)

    def setTalismanImg(self, value):
        self._setString(16, value)

    def _initialize(self):
        super(NewYearRewardsRendererModel, self)._initialize()
        self._addViewModelProperty('rewardsGroup', UserListModel())
        self._addNumberProperty('idx', 0)
        self._addStringProperty('levelText', '')
        self._addBoolProperty('isLevelAchieved', False)
        self._addBoolProperty('isCurrentLevel', False)
        self._addBoolProperty('isLastLevel', False)
        self._addBoolProperty('isNextAfterCurrentLevel', False)
        self._addBoolProperty('showTankwomanTalisman', False)
        self._addBoolProperty('isTankwomanApplied', False)
        self._addBoolProperty('isTankwomanLocked', False)
        self._addBoolProperty('isTalismanApplied', False)
        self._addBoolProperty('isTalismanLocked', False)
        self._addBoolProperty('isNewYearEnabled', True)
        self._addBoolProperty('isMaxReachedLevel', False)
        self._addBoolProperty('showTank', False)
        self._addNumberProperty('tankLevel', 0)
        self._addStringProperty('talismanImg', '')

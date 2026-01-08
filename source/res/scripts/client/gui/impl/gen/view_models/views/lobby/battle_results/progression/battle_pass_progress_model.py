# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/battle_pass_progress_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattlePassProgressModel(ViewModel):
    __slots__ = ('onNavigate',)
    PATH = 'coui://gui/gameface/_dist/production/mono/plugins/post_battle/battle_pass/battle_pass.js'

    def __init__(self, properties=27, commands=1):
        super(BattlePassProgressModel, self).__init__(properties=properties, commands=commands)

    def getPreviousChapterID(self):
        return self._getNumber(0)

    def setPreviousChapterID(self, value):
        self._setNumber(0, value)

    def getCurrentChapterID(self):
        return self._getNumber(1)

    def setCurrentChapterID(self, value):
        self._setNumber(1, value)

    def getHasBattlePass(self):
        return self._getBool(2)

    def setHasBattlePass(self, value):
        self._setBool(2, value)

    def getBattlePassComplete(self):
        return self._getBool(3)

    def setBattlePassComplete(self, value):
        self._setBool(3, value)

    def getAvailablePoints(self):
        return self._getNumber(4)

    def setAvailablePoints(self, value):
        self._setNumber(4, value)

    def getBpTopPoints(self):
        return self._getNumber(5)

    def setBpTopPoints(self, value):
        self._setNumber(5, value)

    def getPointsAux(self):
        return self._getNumber(6)

    def setPointsAux(self, value):
        self._setNumber(6, value)

    def getQuestPoints(self):
        return self._getNumber(7)

    def setQuestPoints(self, value):
        self._setNumber(7, value)

    def getBonusCapPoints(self):
        return self._getNumber(8)

    def setBonusCapPoints(self, value):
        self._setNumber(8, value)

    def getCurrentLevelPoints(self):
        return self._getNumber(9)

    def setCurrentLevelPoints(self, value):
        self._setNumber(9, value)

    def getMaxLevelPoints(self):
        return self._getNumber(10)

    def setMaxLevelPoints(self, value):
        self._setNumber(10, value)

    def getCurrentLevel(self):
        return self._getNumber(11)

    def setCurrentLevel(self, value):
        self._setNumber(11, value)

    def getPreviousLevel(self):
        return self._getNumber(12)

    def setPreviousLevel(self, value):
        self._setNumber(12, value)

    def getPointsDiff(self):
        return self._getNumber(13)

    def setPointsDiff(self, value):
        self._setNumber(13, value)

    def getLevelReached(self):
        return self._getBool(14)

    def setLevelReached(self, value):
        self._setBool(14, value)

    def getLevelMax(self):
        return self._getBool(15)

    def setLevelMax(self, value):
        self._setBool(15, value)

    def getNavigationEnabled(self):
        return self._getBool(16)

    def setNavigationEnabled(self, value):
        self._setBool(16, value)

    def getHolidayBattlePass(self):
        return self._getBool(17)

    def setHolidayBattlePass(self, value):
        self._setBool(17, value)

    def getLevelsInPostProgression(self):
        return self._getNumber(18)

    def setLevelsInPostProgression(self, value):
        self._setNumber(18, value)

    def getPreviousMaxLevelPoints(self):
        return self._getNumber(19)

    def setPreviousMaxLevelPoints(self, value):
        self._setNumber(19, value)

    def getLevelsInPreviousChapter(self):
        return self._getNumber(20)

    def setLevelsInPreviousChapter(self, value):
        self._setNumber(20, value)

    def getExtraChapter(self):
        return self._getBool(21)

    def setExtraChapter(self, value):
        self._setBool(21, value)

    def getPreviousChapterBought(self):
        return self._getBool(22)

    def setPreviousChapterBought(self, value):
        self._setBool(22, value)

    def getCurrentFreeAwards(self):
        return self._getArray(23)

    def setCurrentFreeAwards(self, value):
        self._setArray(23, value)

    @staticmethod
    def getCurrentFreeAwardsType():
        return RewardItemModel

    def getCurrentPaidAwards(self):
        return self._getArray(24)

    def setCurrentPaidAwards(self, value):
        self._setArray(24, value)

    @staticmethod
    def getCurrentPaidAwardsType():
        return RewardItemModel

    def getPreviousFreeAwards(self):
        return self._getArray(25)

    def setPreviousFreeAwards(self, value):
        self._setArray(25, value)

    @staticmethod
    def getPreviousFreeAwardsType():
        return UserListModel

    def getPreviousPaidAwards(self):
        return self._getArray(26)

    def setPreviousPaidAwards(self, value):
        self._setArray(26, value)

    @staticmethod
    def getPreviousPaidAwardsType():
        return UserListModel

    def _initialize(self):
        super(BattlePassProgressModel, self)._initialize()
        self._addNumberProperty('previousChapterID', 0)
        self._addNumberProperty('currentChapterID', 0)
        self._addBoolProperty('hasBattlePass', False)
        self._addBoolProperty('battlePassComplete', False)
        self._addNumberProperty('availablePoints', 0)
        self._addNumberProperty('bpTopPoints', 0)
        self._addNumberProperty('pointsAux', 0)
        self._addNumberProperty('questPoints', 0)
        self._addNumberProperty('bonusCapPoints', 0)
        self._addNumberProperty('currentLevelPoints', 0)
        self._addNumberProperty('maxLevelPoints', 0)
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('previousLevel', 0)
        self._addNumberProperty('pointsDiff', 0)
        self._addBoolProperty('levelReached', False)
        self._addBoolProperty('levelMax', False)
        self._addBoolProperty('navigationEnabled', False)
        self._addBoolProperty('holidayBattlePass', False)
        self._addNumberProperty('levelsInPostProgression', 0)
        self._addNumberProperty('previousMaxLevelPoints', 0)
        self._addNumberProperty('levelsInPreviousChapter', 0)
        self._addBoolProperty('extraChapter', False)
        self._addBoolProperty('previousChapterBought', False)
        self._addArrayProperty('currentFreeAwards', Array())
        self._addArrayProperty('currentPaidAwards', Array())
        self._addArrayProperty('previousFreeAwards', Array())
        self._addArrayProperty('previousPaidAwards', Array())
        self.onNavigate = self._addCommand('onNavigate')

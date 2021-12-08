# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quest_model import NewYearQuestModel

class NewYearChallengeModel(ViewModel):
    __slots__ = ('onLeaveIntroScreen', 'onOpenIntroScreen', 'onChangeAllQuestsVisibility', 'onExit', 'onStylePreviewShow', 'onUpdateTimeTill', 'onSimplify', 'onVisited', 'onSimplificationAnimationEnd', 'onCompletedAnimationShown')

    def __init__(self, properties=16, commands=10):
        super(NewYearChallengeModel, self).__init__(properties=properties, commands=commands)

    def getIsChallengeVisited(self):
        return self._getBool(0)

    def setIsChallengeVisited(self, value):
        self._setBool(0, value)

    def getIsDisplayIntro(self):
        return self._getBool(1)

    def setIsDisplayIntro(self, value):
        self._setBool(1, value)

    def getIsAllQuestsVisible(self):
        return self._getBool(2)

    def setIsAllQuestsVisible(self, value):
        self._setBool(2, value)

    def getIsChallengeCompleted(self):
        return self._getBool(3)

    def setIsChallengeCompleted(self, value):
        self._setBool(3, value)

    def getQuestsCompleted(self):
        return self._getNumber(4)

    def setQuestsCompleted(self, value):
        self._setNumber(4, value)

    def getMaxQuestsQuantity(self):
        return self._getNumber(5)

    def setMaxQuestsQuantity(self, value):
        self._setNumber(5, value)

    def getQuestsQuantityBeforeReward(self):
        return self._getNumber(6)

    def setQuestsQuantityBeforeReward(self, value):
        self._setNumber(6, value)

    def getMaxSimplificationQuantity(self):
        return self._getNumber(7)

    def setMaxSimplificationQuantity(self, value):
        self._setNumber(7, value)

    def getVehicleInBattle(self):
        return self._getBool(8)

    def setVehicleInBattle(self, value):
        self._setBool(8, value)

    def getTimeTill(self):
        return self._getNumber(9)

    def setTimeTill(self, value):
        self._setNumber(9, value)

    def getRealm(self):
        return self._getString(10)

    def setRealm(self, value):
        self._setString(10, value)

    def getQuests(self):
        return self._getArray(11)

    def setQuests(self, value):
        self._setArray(11, value)

    def getProgressRewards(self):
        return self._getArray(12)

    def setProgressRewards(self, value):
        self._setArray(12, value)

    def getFinalRewards(self):
        return self._getArray(13)

    def setFinalRewards(self, value):
        self._setArray(13, value)

    def getSyncInitiator(self):
        return self._getNumber(14)

    def setSyncInitiator(self, value):
        self._setNumber(14, value)

    def getIsDiscountPopoverOpened(self):
        return self._getBool(15)

    def setIsDiscountPopoverOpened(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(NewYearChallengeModel, self)._initialize()
        self._addBoolProperty('isChallengeVisited', False)
        self._addBoolProperty('isDisplayIntro', True)
        self._addBoolProperty('isAllQuestsVisible', False)
        self._addBoolProperty('isChallengeCompleted', False)
        self._addNumberProperty('questsCompleted', 0)
        self._addNumberProperty('maxQuestsQuantity', 0)
        self._addNumberProperty('questsQuantityBeforeReward', 0)
        self._addNumberProperty('maxSimplificationQuantity', 0)
        self._addBoolProperty('vehicleInBattle', False)
        self._addNumberProperty('timeTill', 0)
        self._addStringProperty('realm', '')
        self._addArrayProperty('quests', Array())
        self._addArrayProperty('progressRewards', Array())
        self._addArrayProperty('finalRewards', Array())
        self._addNumberProperty('syncInitiator', 0)
        self._addBoolProperty('isDiscountPopoverOpened', False)
        self.onLeaveIntroScreen = self._addCommand('onLeaveIntroScreen')
        self.onOpenIntroScreen = self._addCommand('onOpenIntroScreen')
        self.onChangeAllQuestsVisibility = self._addCommand('onChangeAllQuestsVisibility')
        self.onExit = self._addCommand('onExit')
        self.onStylePreviewShow = self._addCommand('onStylePreviewShow')
        self.onUpdateTimeTill = self._addCommand('onUpdateTimeTill')
        self.onSimplify = self._addCommand('onSimplify')
        self.onVisited = self._addCommand('onVisited')
        self.onSimplificationAnimationEnd = self._addCommand('onSimplificationAnimationEnd')
        self.onCompletedAnimationShown = self._addCommand('onCompletedAnimationShown')

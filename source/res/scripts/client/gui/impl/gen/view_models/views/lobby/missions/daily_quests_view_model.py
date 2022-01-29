# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/daily_quests_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.missions.daily_quests_model import DailyQuestsModel
from gui.impl.gen.view_models.views.lobby.missions.epic_quest_model import EpicQuestModel
from gui.impl.gen.view_models.views.lobby.missions.lootboxes_intro_model import LootboxesIntroModel
from gui.impl.gen.view_models.views.lobby.missions.premium_missions_model import PremiumMissionsModel

class DailyQuestsViewModel(ViewModel):
    __slots__ = ('onClose', 'onReroll', 'onTabClick', 'onInfoToggle', 'onBuyPremiumBtnClick', 'onRerollEnabled', 'onLootboxesIntroClosed', 'onLunarNYDailyQuestIntroClosed')

    def __init__(self, properties=14, commands=8):
        super(DailyQuestsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def dailyQuests(self):
        return self._getViewModel(0)

    @property
    def premiumMissions(self):
        return self._getViewModel(1)

    @property
    def epicQuest(self):
        return self._getViewModel(2)

    @property
    def lootboxesIntro(self):
        return self._getViewModel(3)

    def getCurrentTabIdx(self):
        return self._getNumber(4)

    def setCurrentTabIdx(self, value):
        self._setNumber(4, value)

    def getCountDown(self):
        return self._getNumber(5)

    def setCountDown(self, value):
        self._setNumber(5, value)

    def getInfoVisible(self):
        return self._getBool(6)

    def setInfoVisible(self, value):
        self._setBool(6, value)

    def getIsLootboxesIntroVisible(self):
        return self._getBool(7)

    def setIsLootboxesIntroVisible(self, value):
        self._setBool(7, value)

    def getPremMissionsTabDiscovered(self):
        return self._getBool(8)

    def setPremMissionsTabDiscovered(self, value):
        self._setBool(8, value)

    def getIsBattlePassActive(self):
        return self._getBool(9)

    def setIsBattlePassActive(self, value):
        self._setBool(9, value)

    def getIsLunarNYActive(self):
        return self._getBool(10)

    def setIsLunarNYActive(self, value):
        self._setBool(10, value)

    def getIsLunarNYDailyQuestIntroVisible(self):
        return self._getBool(11)

    def setIsLunarNYDailyQuestIntroVisible(self, value):
        self._setBool(11, value)

    def getIsGiftSystemDisabled(self):
        return self._getBool(12)

    def setIsGiftSystemDisabled(self, value):
        self._setBool(12, value)

    def getIsNewYearAvailable(self):
        return self._getBool(13)

    def setIsNewYearAvailable(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(DailyQuestsViewModel, self)._initialize()
        self._addViewModelProperty('dailyQuests', DailyQuestsModel())
        self._addViewModelProperty('premiumMissions', PremiumMissionsModel())
        self._addViewModelProperty('epicQuest', EpicQuestModel())
        self._addViewModelProperty('lootboxesIntro', LootboxesIntroModel())
        self._addNumberProperty('currentTabIdx', 0)
        self._addNumberProperty('countDown', 0)
        self._addBoolProperty('infoVisible', False)
        self._addBoolProperty('isLootboxesIntroVisible', False)
        self._addBoolProperty('premMissionsTabDiscovered', False)
        self._addBoolProperty('isBattlePassActive', False)
        self._addBoolProperty('isLunarNYActive', False)
        self._addBoolProperty('isLunarNYDailyQuestIntroVisible', False)
        self._addBoolProperty('isGiftSystemDisabled', False)
        self._addBoolProperty('isNewYearAvailable', False)
        self.onClose = self._addCommand('onClose')
        self.onReroll = self._addCommand('onReroll')
        self.onTabClick = self._addCommand('onTabClick')
        self.onInfoToggle = self._addCommand('onInfoToggle')
        self.onBuyPremiumBtnClick = self._addCommand('onBuyPremiumBtnClick')
        self.onRerollEnabled = self._addCommand('onRerollEnabled')
        self.onLootboxesIntroClosed = self._addCommand('onLootboxesIntroClosed')
        self.onLunarNYDailyQuestIntroClosed = self._addCommand('onLunarNYDailyQuestIntroClosed')

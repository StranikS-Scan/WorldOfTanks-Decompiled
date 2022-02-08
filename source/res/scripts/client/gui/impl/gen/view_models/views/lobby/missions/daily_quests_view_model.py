# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/daily_quests_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.missions.daily_quests_model import DailyQuestsModel
from gui.impl.gen.view_models.views.lobby.missions.epic_quest_model import EpicQuestModel
from gui.impl.gen.view_models.views.lobby.missions.premium_missions_model import PremiumMissionsModel

class DailyQuestsViewModel(ViewModel):
    __slots__ = ('onClose', 'onReroll', 'onTabClick', 'onInfoToggle', 'onBuyPremiumBtnClick', 'onRerollEnabled')

    def __init__(self, properties=8, commands=6):
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

    def getCurrentTabIdx(self):
        return self._getNumber(3)

    def setCurrentTabIdx(self, value):
        self._setNumber(3, value)

    def getCountDown(self):
        return self._getNumber(4)

    def setCountDown(self, value):
        self._setNumber(4, value)

    def getInfoVisible(self):
        return self._getBool(5)

    def setInfoVisible(self, value):
        self._setBool(5, value)

    def getPremMissionsTabDiscovered(self):
        return self._getBool(6)

    def setPremMissionsTabDiscovered(self, value):
        self._setBool(6, value)

    def getIsBattlePassActive(self):
        return self._getBool(7)

    def setIsBattlePassActive(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(DailyQuestsViewModel, self)._initialize()
        self._addViewModelProperty('dailyQuests', DailyQuestsModel())
        self._addViewModelProperty('premiumMissions', PremiumMissionsModel())
        self._addViewModelProperty('epicQuest', EpicQuestModel())
        self._addNumberProperty('currentTabIdx', 0)
        self._addNumberProperty('countDown', 0)
        self._addBoolProperty('infoVisible', False)
        self._addBoolProperty('premMissionsTabDiscovered', False)
        self._addBoolProperty('isBattlePassActive', False)
        self.onClose = self._addCommand('onClose')
        self.onReroll = self._addCommand('onReroll')
        self.onTabClick = self._addCommand('onTabClick')
        self.onInfoToggle = self._addCommand('onInfoToggle')
        self.onBuyPremiumBtnClick = self._addCommand('onBuyPremiumBtnClick')
        self.onRerollEnabled = self._addCommand('onRerollEnabled')

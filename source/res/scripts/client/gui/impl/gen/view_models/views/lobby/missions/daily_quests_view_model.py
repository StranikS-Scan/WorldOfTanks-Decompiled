# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/daily_quests_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.missions.daily_quests_model import DailyQuestsModel
from gui.impl.gen.view_models.views.lobby.missions.epic_quest_model import EpicQuestModel
from gui.impl.gen.view_models.views.lobby.missions.lootboxes_intro_model import LootboxesIntroModel
from gui.impl.gen.view_models.views.lobby.missions.premium_missions_model import PremiumMissionsModel
from gui.impl.gen.view_models.views.lobby.missions.winback_progression_model import WinbackProgressionModel

class DailyTypes(Enum):
    DEFAULT = 'default'
    WINBACK = 'winback'


class OffersState(Enum):
    AVAILABLE = 'available'
    DISABLED = 'disabled'
    NO_OFFERS = 'no_offers'


class DailyQuestsViewModel(ViewModel):
    __slots__ = ('onClose', 'onReroll', 'onTabClick', 'onInfoToggle', 'onBuyPremiumBtnClick', 'onRerollEnabled', 'onClaimRewards', 'onLootboxesIntroClosed')

    def __init__(self, properties=17, commands=8):
        super(DailyQuestsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def dailyQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getDailyQuestsType():
        return DailyQuestsModel

    @property
    def premiumMissions(self):
        return self._getViewModel(1)

    @staticmethod
    def getPremiumMissionsType():
        return PremiumMissionsModel

    @property
    def epicQuest(self):
        return self._getViewModel(2)

    @staticmethod
    def getEpicQuestType():
        return EpicQuestModel

    @property
    def winbackProgression(self):
        return self._getViewModel(3)

    @staticmethod
    def getWinbackProgressionType():
        return WinbackProgressionModel

    @property
    def lootboxesIntro(self):
        return self._getViewModel(4)

    @staticmethod
    def getLootboxesIntroType():
        return LootboxesIntroModel

    def getDailyType(self):
        return DailyTypes(self._getString(5))

    def setDailyType(self, value):
        self._setString(5, value.value)

    def getGetRewardsTimeLeft(self):
        return self._getNumber(6)

    def setGetRewardsTimeLeft(self, value):
        self._setNumber(6, value)

    def getOffersState(self):
        return OffersState(self._getString(7))

    def setOffersState(self, value):
        self._setString(7, value.value)

    def getCurrentTabIdx(self):
        return self._getNumber(8)

    def setCurrentTabIdx(self, value):
        self._setNumber(8, value)

    def getCountDown(self):
        return self._getNumber(9)

    def setCountDown(self, value):
        self._setNumber(9, value)

    def getInfoVisible(self):
        return self._getBool(10)

    def setInfoVisible(self, value):
        self._setBool(10, value)

    def getIsLootboxesIntroVisible(self):
        return self._getBool(11)

    def setIsLootboxesIntroVisible(self, value):
        self._setBool(11, value)

    def getPremMissionsTabDiscovered(self):
        return self._getBool(12)

    def setPremMissionsTabDiscovered(self, value):
        self._setBool(12, value)

    def getIsBattlePassActive(self):
        return self._getBool(13)

    def setIsBattlePassActive(self, value):
        self._setBool(13, value)

    def getIsComp7Active(self):
        return self._getBool(14)

    def setIsComp7Active(self, value):
        self._setBool(14, value)

    def getIsGiftSystemDisabled(self):
        return self._getBool(15)

    def setIsGiftSystemDisabled(self, value):
        self._setBool(15, value)

    def getIsNewYearAvailable(self):
        return self._getBool(16)

    def setIsNewYearAvailable(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(DailyQuestsViewModel, self)._initialize()
        self._addViewModelProperty('dailyQuests', DailyQuestsModel())
        self._addViewModelProperty('premiumMissions', PremiumMissionsModel())
        self._addViewModelProperty('epicQuest', EpicQuestModel())
        self._addViewModelProperty('winbackProgression', WinbackProgressionModel())
        self._addViewModelProperty('lootboxesIntro', LootboxesIntroModel())
        self._addStringProperty('dailyType')
        self._addNumberProperty('getRewardsTimeLeft', 0)
        self._addStringProperty('offersState')
        self._addNumberProperty('currentTabIdx', 0)
        self._addNumberProperty('countDown', 0)
        self._addBoolProperty('infoVisible', False)
        self._addBoolProperty('isLootboxesIntroVisible', False)
        self._addBoolProperty('premMissionsTabDiscovered', False)
        self._addBoolProperty('isBattlePassActive', False)
        self._addBoolProperty('isComp7Active', False)
        self._addBoolProperty('isGiftSystemDisabled', False)
        self._addBoolProperty('isNewYearAvailable', False)
        self.onClose = self._addCommand('onClose')
        self.onReroll = self._addCommand('onReroll')
        self.onTabClick = self._addCommand('onTabClick')
        self.onInfoToggle = self._addCommand('onInfoToggle')
        self.onBuyPremiumBtnClick = self._addCommand('onBuyPremiumBtnClick')
        self.onRerollEnabled = self._addCommand('onRerollEnabled')
        self.onClaimRewards = self._addCommand('onClaimRewards')
        self.onLootboxesIntroClosed = self._addCommand('onLootboxesIntroClosed')

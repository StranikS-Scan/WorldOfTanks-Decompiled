# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/premium_quests_feature.py
from Event import Event
from constants import PremiumConfigs, PREMIUM_TYPE
from gui.impl.gen.view_models.views.lobby.account_dashboard.premium_quests_model import PremiumQuestsModel
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showDailyQuests
from gui.server_events.events_helpers import isPremiumQuestsEnable, premMissionsSortFunc
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class PremQuestsController(object):
    eventsCache = dependency.descriptor(IEventsCache)
    gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self):
        self.onPremiumQuestsStageChange = Event()
        self._completedQuestsCount = 0

    def getCompletedQuestsCount(self):
        return self._completedQuestsCount

    def initialise(self):
        self.eventsCache.onProgressUpdated += self.update
        self.eventsCache.onSyncCompleted += self.update
        self.gameSession.onPremiumNotify += self.update

    def finalize(self):
        self.eventsCache.onProgressUpdated -= self.update
        self.eventsCache.onSyncCompleted -= self.update
        self.gameSession.onPremiumNotify -= self.update

    def update(self, *args):
        quests = self.eventsCache.getPremiumQuests().values()
        newCompletedQuestsCount = 0
        for quest in sorted(quests, cmp=premMissionsSortFunc):
            if quest.isCompleted():
                newCompletedQuestsCount += 1

        if newCompletedQuestsCount != self._completedQuestsCount:
            self._completedQuestsCount = newCompletedQuestsCount
            self.onPremiumQuestsStageChange()


class PremiumQuestsFeature(FeatureItem):
    NO_PREMIUM = -1
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self, viewModel):
        super(PremiumQuestsFeature, self).__init__(viewModel)
        self._questController = PremQuestsController()

    def initialize(self, *args, **kwargs):
        super(PremiumQuestsFeature, self).initialize(*args, **kwargs)
        self._questController.initialise()
        self._questController.onPremiumQuestsStageChange += self.__updateModel
        self._gameSession.onPremiumNotify += self.__onPremiumChange
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._viewModel.premiumQuests.onClick += self.onClick

    def finalize(self):
        self._gameSession.onPremiumNotify -= self.__onPremiumChange
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self._viewModel.premiumQuests.onClick -= self.onClick
        self._questController.onPremiumQuestsStageChange -= self.__updateModel
        self._questController.finalize()
        self._questController = None
        super(PremiumQuestsFeature, self).finalize()
        return

    def _fillModel(self, model):
        self._questController.update()
        self.__updateModel(model=model)

    @replaceNoneKwargsModel
    def __updateModel(self, model=None):
        submodel = model.premiumQuests
        submodel.setIsEnabled(isPremiumQuestsEnable())
        hasPremium = self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        status = self._questController.getCompletedQuestsCount() if hasPremium else self.NO_PREMIUM
        submodel.setCompletedMissionsCount(status)

    def __onPremiumChange(self, *_):
        self.__updateModel()

    def __onServerSettingsChange(self, diff=None):
        if PremiumConfigs.PREM_QUESTS not in diff:
            return
        diffConfig = diff.get(PremiumConfigs.PREM_QUESTS)
        if 'enabled' in diffConfig:
            self.__updateModel()

    @staticmethod
    def onClick():
        if isPremiumQuestsEnable():
            showDailyQuests(subTab=DailyTabs.PREMIUM_MISSIONS)

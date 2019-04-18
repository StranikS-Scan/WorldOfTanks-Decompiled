# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/prem_dashboard_quests_card.py
from Event import Event
from constants import PREMIUM_TYPE, PremiumConfigs
from frameworks.wulf import ViewFlags
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.card_quests_tasks_model import CardQuestsTasksModel
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_quests_card_model import PremDashboardQuestsCardModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissions
from gui.server_events.events_helpers import premMissionsSortFunc, isPremiumQuestsEnable, getPremiumGroup
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class PremQuestsController(object):
    eventsCache = dependency.descriptor(IEventsCache)
    gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self):
        self.onPremiumQuestsStatesChange = Event()
        self._questsStates = [MISSIONS_STATES.DISABLED, MISSIONS_STATES.DISABLED, MISSIONS_STATES.DISABLED]

    def getQuestsStates(self):
        return self._questsStates

    def getQuestsCount(self):
        return len(self._questsStates)

    def initialise(self):
        self.eventsCache.onProgressUpdated += self._update
        self.eventsCache.onSyncCompleted += self._update
        self.gameSession.onPremiumNotify += self._update
        self._update()

    def finalize(self):
        self.eventsCache.onProgressUpdated -= self._update
        self.eventsCache.onSyncCompleted -= self._update
        self.gameSession.onPremiumNotify -= self._update

    def _getPersonalQuestsStates(self):
        quests = self.eventsCache.getPremiumQuests().values()
        result = []
        for quest in sorted(quests, cmp=premMissionsSortFunc):
            if quest.isCompleted():
                result.append(MISSIONS_STATES.COMPLETED)
            if quest.isAvailable()[0]:
                result.append(MISSIONS_STATES.IN_PROGRESS)
            result.append(MISSIONS_STATES.DISABLED)

        return result

    def _update(self, *args):
        if self._getPersonalQuestsStates() != self._questsStates:
            self._questsStates = self._getPersonalQuestsStates()
            self.onPremiumQuestsStatesChange()


class PremDashboardQuestsCard(ViewImpl):
    __slots__ = ('_questController', '_modelConstantsMap')
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self, *args, **kwargs):
        super(PremDashboardQuestsCard, self).__init__(R.views.premDashboardQuestsCard(), ViewFlags.VIEW, PremDashboardQuestsCardModel, *args, **kwargs)
        self._questController = PremQuestsController()
        self._modelConstantsMap = {MISSIONS_STATES.COMPLETED: self.viewModel.COMPLETED,
         MISSIONS_STATES.IN_PROGRESS: self.viewModel.IN_PROGRESS}

    @property
    def viewModel(self):
        return super(PremDashboardQuestsCard, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PremDashboardQuestsCard, self)._initialize(*args, **kwargs)
        self._questController.initialise()
        self._questController.onPremiumQuestsStatesChange += self.__onPremiumQuestsStatesChange
        self._gameSession.onPremiumNotify += self.__updateIsTankPremiumActive
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.viewModel.onGoToQuestsView += self.__onGoToQuestsView
        self.__addPremQuestModel()
        self.__updateQuestsStates()
        self.__updateIsAvailable()
        self.__updateIsTankPremiumActive()

    def _finalize(self):
        self._gameSession.onPremiumNotify -= self.__updateIsTankPremiumActive
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.viewModel.onGoToQuestsView -= self.__onGoToQuestsView
        self._questController.onPremiumQuestsStatesChange -= self.__onPremiumQuestsStatesChange
        self._questController.finalize()
        self._questController = None
        super(PremDashboardQuestsCard, self)._finalize()
        return

    def __updateQuestsStates(self):
        newStates = self._questController.getQuestsStates()
        newStates = [ self._modelConstantsMap.get(state, self.viewModel.DISABLED) for state in newStates ]
        premiumQuestsArray = self.viewModel.premiumQuests.getItems()
        for newState, taskModel in zip(newStates, premiumQuestsArray):
            if taskModel.getState() != newState:
                taskModel.setState(newState)

    def __onServerSettingsChange(self, diff=None):
        if PremiumConfigs.PREM_QUESTS not in diff:
            return
        diffConfig = diff.get(PremiumConfigs.PREM_QUESTS)
        if 'enabled' in diffConfig:
            self.__updateIsAvailable()

    def __onPremiumQuestsStatesChange(self):
        self.__updateQuestsStates()
        self.__updateIsAvailable()

    def __updateIsTankPremiumActive(self, *args):
        isPremium = self.__isTankPremiumActive()
        self.viewModel.setIsTankPremiumActive(isPremium)

    def __updateIsAvailable(self, *args):
        isAvailable = isPremiumQuestsEnable()
        self.viewModel.setIsAvailable(isAvailable)

    def __addPremQuestModel(self):
        listArray = self.viewModel.premiumQuests.getItems()
        questCount = self._questController.getQuestsCount()
        for id_ in range(questCount):
            model = CardQuestsTasksModel()
            model.setState(self.viewModel.DISABLED)
            if id_ != questCount - 1:
                model.setShowLine(True)
            listArray.addViewModel(model)

    def __isTankPremiumActive(self):
        return self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)

    def __onGoToQuestsView(self):
        if isPremiumQuestsEnable():
            group = getPremiumGroup()
            showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, groupID=group.getID())

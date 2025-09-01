# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/daily_section/presenters/premium_daily_missions_block_presenter.py
from constants import PremiumConfigs
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.premium_daily.premium_daily_mission_model import PremiumDailyMissionModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.premium_daily.premium_daily_missions_block_model import PremiumDailyMissionsBlockModel
from gui.impl.lobby.missions.missions_helpers import isPremiumPlusAccount, markQuestProgressAsViewed
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModelByIds
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.presenters.base_missions_block_presenter import BaseMissionsBlockPresenter
from gui.server_events.events_helpers import isPremiumQuestsEnable, premMissionsSortFunc
from gui.server_events.settings import visitEventsGUI
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class PremiumDailyMissionsBlockPresenter(BaseMissionsBlockPresenter[PremiumDailyMissionsBlockModel]):
    eventsCache = dependency.descriptor(IEventsCache)
    gameSession = dependency.descriptor(IGameSessionController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(PremiumDailyMissionsBlockPresenter, self).__init__(model=PremiumDailyMissionsBlockModel)

    @property
    def viewModel(self):
        return super(PremiumDailyMissionsBlockPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PremiumDailyMissionsBlockPresenter, self)._onLoading()
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)

    def _markQuestsAsVisited(self):
        if isPremiumPlusAccount() and self._isBlockEnabled:
            seenQuests = self.eventsCache.getPremiumQuests().values()
            markQuestProgressAsViewed(seenQuests)
            visitEventsGUI(seenQuests)

    def _onSyncCompleted(self, *_):
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)
        super(PremiumDailyMissionsBlockPresenter, self)._onSyncCompleted(*_)

    def _getEvents(self):
        vm = self.viewModel
        eventsTuple = super(PremiumDailyMissionsBlockPresenter, self)._getEvents()
        return eventsTuple + ((vm.onPurchasePremium, self.__onBuyPremiumBtn), (self.gameSession.onPremiumTypeChanged, self._onPremiumTypeChanged), (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged))

    def _updateModel(self, model):
        isPremAcc = isPremiumPlusAccount()
        self._isBlockEnabled = isPremiumQuestsEnable()
        model.setIsAvailable(isPremAcc)
        if not isPremAcc or not self._isBlockEnabled:
            return
        else:
            quests = sorted(self.eventsCache.getPremiumQuests().values(), cmp=premMissionsSortFunc)
            missionsList = model.getMissionsList()
            questIdsInModel = [ m.getId() for m in missionsList ]
            if not needToUpdateQuestsInModelByIds(quests, questIdsInModel):
                return
            for i in questIdsInModel:
                self._tooltipData.pop(i, None)

            missionsList.clear()
            for quest in quests:
                mm = PremiumDailyMissionModel()
                self._fillMissionModel(mm, quest)
                mm.setIsLocked(not quest.isCompleted() and not quest.isAvailable().isValid)
                missionsList.addViewModel(mm)

            missionsList.invalidate()
            return

    def _onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if PremiumConfigs.PREM_QUESTS in diff:
            premDiff = diff[PremiumConfigs.PREM_QUESTS]
            stateChanged = 'enabled' in premDiff and premDiff['enabled'] is not self._isBlockEnabled
            if stateChanged:
                with self.viewModel.transaction() as tx:
                    self._updateModel(tx)

    def _onPremiumTypeChanged(self, *_):
        if self.isInRequiredTab:
            self._markQuestsAsVisited()
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)

    def __onBuyPremiumBtn(self, *args):
        showShop(getBuyPremiumUrl())

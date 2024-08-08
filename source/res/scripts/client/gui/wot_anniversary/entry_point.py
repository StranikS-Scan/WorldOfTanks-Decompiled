# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/entry_point.py
from itertools import chain
import typing
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.entry_point_model import EntryPointModel, State
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsWotAnniversary
from gui.wot_anniversary.utils import isTokenQuestUnlocked, isMascotQuestRewardAvailable
from gui.wot_anniversary.wot_anniversary_constants import WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IWalletController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.wot_anniversary import IWotAnniversaryController

class WotAnniversaryEntryPointInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return WotAnniversaryEntryPointWidget()


class WotAnniversaryEntryPointWidget(ViewImpl):
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wot_anniversary.EntryPoint(), flags=ViewFlags.VIEW, model=EntryPointModel())
        super(WotAnniversaryEntryPointWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotAnniversaryEntryPointWidget, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onEnterEventLobby, self.__onEnterEventLobby),
         (self.__wotAnniversaryCtrl.onSettingsChanged, self.__onSettingChanged),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self.__eventsCache.onSyncCompleted, self.__onEventsCacheUpdated))

    def _getCallbacks(self):
        return (('stats.eventCoin', self.__onEventCoinUpdate),)

    def _onLoaded(self, *args, **kwargs):
        super(WotAnniversaryEntryPointWidget, self)._onLoaded(*args, **kwargs)
        self.__updateModel()

    def __updateModel(self):
        if not self.__wotAnniversaryCtrl.isAvailableAndActivePhase():
            return
        with self.viewModel.transaction() as tx:
            tx.setState(self.__getState())
            self.__updateBalance(model=tx)

    @replaceNoneKwargsModel
    def __updateBalance(self, model=None):
        eventCoins = self.__itemsCache.items.stats.eventCoin if self.__wallet.isAvailable else -1
        model.setBalance(eventCoins)

    @staticmethod
    def __onEnterEventLobby():
        showMissionsWotAnniversary()

    def __getState(self):
        loginQuests = self.__wotAnniversaryCtrl.getLoginQuests().values()
        hasAvailableLoginReward = bool(findFirst(lambda q: isTokenQuestUnlocked(q, WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN) and not q.isCompleted(), loginQuests))
        mascotBattleQuests = self.__wotAnniversaryCtrl.getMascotBattleQuests().values()
        mascotRewardQuests = self.__wotAnniversaryCtrl.getMascotRewardQuests().values()
        hasAvailableMascotRewards = False
        for quest in mascotRewardQuests:
            hasAvailableMascotRewards |= isMascotQuestRewardAvailable(quest)

        dailyQuests = self.__wotAnniversaryCtrl.getDailyQuests().values()
        allBattleQuestsCompleted = all([ q.isCompleted() for q in chain(dailyQuests, mascotBattleQuests) ])
        if hasAvailableMascotRewards or hasAvailableLoginReward:
            state = State.CLAIMREWARDS
        elif allBattleQuestsCompleted:
            state = State.COMPLETED if self.__wotAnniversaryCtrl.isLastDayNow() else State.WAITQUESTS
        else:
            state = State.INPROGRESS
        return state

    def __onSettingChanged(self):
        self.__updateModel()

    def __onEventsCacheUpdated(self):
        self.__updateModel()

    def __onEventCoinUpdate(self, _):
        self.__updateBalance()

    def __onWalletStatusChanged(self, _):
        self.__updateBalance()

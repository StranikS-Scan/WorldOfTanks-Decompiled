# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_storage_boxes_view.py
from adisp import process
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from constants import LOOTBOX_TOKEN_PREFIX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_storage_boxes_view_model import WtEventStorageBoxesViewModel
from gui.impl.gen.view_models.views.lobby.wt_event.box_card_model import BoxCardModel
from gui.impl.gen.view_models.views.lobby.wt_event.reward_model import RewardModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.server_events.events_constants import WT_GROUP_PREFIX
from gui.server_events.events_dispatcher import showMissionsCategories
from gui.shared.event_dispatcher import showWtEventLootboxOpenWindow
from gui.Scaleform.Waiting import Waiting
from gui.shop import showLootBoxBuyWindow
from gui.wt_event.wt_event_helpers import getLootBoxRewardTooltipData, getLootBoxButtonTooltipData, getNoLootBoxButtonTooltipData
from helpers import dependency
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IEventLootBoxesController

class WTEventStorageBoxesView(ViewImpl):
    __slots__ = ('__tooltipItems',)
    __gameEventController = dependency.descriptor(IGameEventController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __lootBoxesController = dependency.descriptor(IEventLootBoxesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventStorageBoxes(), flags=ViewFlags.OVERLAY_VIEW, model=WtEventStorageBoxesViewModel())
        self.__tooltipItems = {}
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventStorageBoxesView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTEventStorageBoxesView, self).getViewModel()

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId')
        tooltipData = None
        if tooltipId in ('random', 'collection', 'gold', 'vehicles'):
            boxId = event.getArgument('box')
            tooltipData = getLootBoxRewardTooltipData(tooltipId, boxId, gameEventController=self.__gameEventController)
        elif tooltipId == 'button':
            boxId = event.getArgument('boxId')
            if not self.__lobbyContext.getServerSettings().isLootBoxesEnabled():
                tooltipData = getLootBoxButtonTooltipData()
            elif not self.__getBoxCount(boxId):
                tooltipData = getNoLootBoxButtonTooltipData()
        if tooltipData is not None:
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow(), event=event)
            window.load()
            return window
        else:
            return super(WTEventStorageBoxesView, self).createToolTip(event)

    def _onLoaded(self):
        super(WTEventStorageBoxesView, self)._onLoaded()
        Waiting.hide('loadPage')
        wt_event_sound.playLootBoxStorageEnter()

    def _onLoading(self, *args, **kwargs):
        super(WTEventStorageBoxesView, self)._onLoading(*args, **kwargs)
        Waiting.show('loadPage')
        rStorage = R.strings.wt_event.storageBoxes
        with self.getViewModel().transaction() as model:
            model.setTitle(backport.text(rStorage.title()))
            model.setIsEnterFromHangar(not self.__gameEventController.isEventPrbActive() and self.__gameEventController.isEnabled())
            model.setIsLootBoxEnabled(self.__lobbyContext.getServerSettings().isLootBoxesEnabled())
            for box in ('wt_hunter', 'wt_boss', 'wt_special'):
                boxCard = BoxCardModel()
                boxCard.setId(box)
                boxCard.setQuantity(self.__getBoxCount(box))
                rName = rStorage.name.dyn(box)
                if rName.exists():
                    boxCard.setName(backport.text(rName()))
                rDescription = rStorage.description.dyn(box)
                if rDescription.exists():
                    boxCard.setDescription(backport.text(rDescription()))
                self.__fillRewards(boxCard)
                model.boxCards.addViewModel(boxCard)

        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(WTEventStorageBoxesView, self)._finalize()

    def __destroyWindow(self, isTransition=False):
        if not isTransition:
            wt_event_sound.playLootBoxExit()
        self.destroyWindow()

    def __addListeners(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.viewModel.onAwardOpen += self.__onAwardOpen
        self.viewModel.onBuySpecialBox += self.__onBuySpecialBox
        self.viewModel.onToMissions += self.__onToMissions
        self.viewModel.onToEvent += self.__onToEvent
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__gameEventController.onEventUpdated += self.__onEventUpdated

    def __removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.viewModel.onAwardOpen -= self.__onAwardOpen
        self.viewModel.onBuySpecialBox -= self.__onBuySpecialBox
        self.viewModel.onToMissions -= self.__onToMissions
        self.viewModel.onToEvent -= self.__onToEvent
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__gameEventController.onEventUpdated -= self.__onEventUpdated

    def __onTokensUpdate(self, diff):
        for key in diff.iterkeys():
            if key.startswith(LOOTBOX_TOKEN_PREFIX):
                self.__updateBoxesCount()
                return

    def __onEventUpdated(self):
        if not self.__gameEventController.isEnabled():
            self.__destroyWindow()

    def __onAwardOpen(self, args):
        boxType = args.get('id')
        showWtEventLootboxOpenWindow(boxType=boxType, isTransition=True)
        self.__destroyWindow(isTransition=True)

    def __onBuySpecialBox(self):
        showLootBoxBuyWindow()

    def __onToMissions(self):
        showMissionsCategories(groupID=WT_GROUP_PREFIX)
        self.__destroyWindow()

    def __onToEvent(self):
        self.__doSelectAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE)
        self.__destroyWindow()

    @process
    def __doSelectAction(self, actionName):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            yield dispatcher.doSelectAction(PrbAction(actionName))
        return

    def __fillRewards(self, boxCard):
        rewards = self.__gameEventController.getLootBoxRewards(boxCard.getId())
        for reward in sorted(rewards, reverse=boxCard.getId() in ('wt_hunter', 'wt_boss')):
            rewardModel = RewardModel()
            if reward.startswith('gold'):
                name, amount = reward.split('_')
                rewardModel.setType(name)
                rewardModel.setAmount(amount)
            else:
                rewardModel.setType(reward)
            boxCard.rewards.addViewModel(rewardModel)

    def __updateBoxesCount(self):
        with self.getViewModel().transaction() as model:
            for boxCard in model.boxCards.getItems():
                boxCard.setQuantity(self.__getBoxCount(boxCard.getId()))

    def __getBoxCount(self, boxId):
        totalCount = 0
        for box in self.__lootBoxesController.getAllEventLootBoxes():
            if box.getType() == boxId:
                totalCount += box.getInventoryCount()

        return totalCount

    def __onServerSettingChanged(self, *_):
        self.viewModel.setIsLootBoxEnabled(self.__lobbyContext.getServerSettings().isLootBoxesEnabled())


class WTEventStorageBoxesWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WTEventStorageBoxesWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=WTEventStorageBoxesView(), parent=parent, decorator=None)
        return

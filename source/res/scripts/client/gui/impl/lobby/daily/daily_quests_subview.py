# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_subview.py
import logging
import typing
import weakref
from constants import DailyQuestsLevels as LEVELS
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.impl.backport.backport_tooltip import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_subview_model import DailyQuestsSubviewModel
from gui.impl.gen.view_models.views.lobby.daily.tooltips.locked_subscription_bonus_tooltip_model import LockedSubscriptionBonusTooltipModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.daily.daily_quests_presenter import DailyQuestsPresenterRegular, DailyQuestsPresenterPremium, EpicQuestsPresenter
from gui.impl.lobby.daily.unseen_quests_component import UnseenQuestsComponent
from gui.impl.lobby.daily.tooltips.reroll_tooltip import RerollTooltip
from gui.impl.pub import ViewImpl
from gui.server_events import daily_quests
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.shared.event_dispatcher import showShop
from adisp import adisp_process
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf.view.view_event import ViewEvent
    from frameworks.wulf.windows_system.window import Window
_logger = logging.getLogger(__name__)

class DailyQuestsSubviewBase(ViewImpl):

    def activate(self):
        self._subscribe()
        self._update()

    def deactivate(self):
        self._unsubscribe()

    def _update(self):
        raise NotImplementedError


class DailyQuestsSubview(DailyQuestsSubviewBase):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    subscriptionCtrl = dependency.descriptor(IWotPlusController)
    __slots__ = ('__parent', '__tooltipData', '__presenters')

    def __init__(self, parent, layoutID):
        viewSettings = ViewSettings(layoutID, ViewFlags.VIEW, DailyQuestsSubviewModel())
        super(DailyQuestsSubview, self).__init__(viewSettings)
        self.__parent = weakref.proxy(parent)
        self.__tooltipData = {}
        self.__presenters = [DailyQuestsPresenterRegular(self.viewModel.regular, weakref.proxy(self)), DailyQuestsPresenterPremium(self.viewModel.premium, weakref.proxy(self)), EpicQuestsPresenter(self.viewModel.epic, weakref.proxy(self))]
        self.__unseenComponent = UnseenQuestsComponent(self.viewModel.unseenQuests, weakref.proxy(self))

    @property
    def viewModel(self):
        return super(DailyQuestsSubview, self).getViewModel()

    @property
    def currentTabIdx(self):
        return self.__parent.getCurrentTabID()

    @property
    def tooltipData(self):
        return self.__tooltipData

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.daily.tooltips.RerollTooltip():
            return RerollTooltip(event.getArgument('rerollPremium'))
        if contentID == R.views.lobby.daily.tooltips.LockedSubscriptionBonusTooltip():
            model = LockedSubscriptionBonusTooltipModel()
            with model.transaction() as tx:
                tx.setIsActiveSubscription(self.subscriptionCtrl.isEnabled())
                tx.setIsQuestDone(event.getArgument('isQuestDone'))
            return ViewImpl(ViewSettings(R.views.lobby.daily.tooltips.LockedSubscriptionBonusTooltip(), model=model))
        lootBoxRes = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes').dyn('tooltips').dyn('LootboxTooltip')
        if lootBoxRes.exists() and contentID == lootBoxRes():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            missionId, tooltipId = event.getArgument('tooltipId', '').rsplit(':', 1)
            tooltipData = self.__tooltipData.get(missionId, {}).get(tooltipId)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        return super(DailyQuestsSubview, self).createToolTipContent(event=event, contentID=contentID)

    def createToolTip(self, event):
        missionParam = event.getArgument('tooltipId', '')
        if not missionParam:
            return super(DailyQuestsSubview, self).createToolTip(event)
        else:
            missionParams = missionParam.rsplit(':', 1)
            if len(missionParams) != 2:
                tooltipData = self.__tooltipData.get(missionParam)
            else:
                missionId, tooltipId = missionParams
                tooltipsData = self.__tooltipData.get(missionId, {})
                tooltipData = tooltipsData.get(tooltipId)
            if tooltipData and isinstance(tooltipData, TooltipData):
                window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
                if window is not None:
                    window.load()
            else:
                window = super(DailyQuestsSubview, self).createToolTip(event)
            return window

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestsSubview, self)._onLoading()
        self.__unseenComponent.initialize()

    def _finalize(self):
        super(DailyQuestsSubview, self)._finalize()
        self.__unseenComponent.finalize()
        self.__unseenComponent = None
        for presenter in self.__presenters:
            presenter.finalize()

        del self.__presenters[:]
        return

    def activate(self):
        super(DailyQuestsSubview, self).activate()
        for presenter in self.__presenters:
            presenter.initialize()

    def _update(self):
        with self.viewModel.transaction() as tx:
            tx.setCurrentTabIdx(self.currentTabIdx)
        self.__unseenComponent.setCurrentTab(self.currentTabIdx)

    def deactivate(self):
        super(DailyQuestsSubview, self).deactivate()
        for presenter in self.__presenters:
            presenter.finalize()

    def _getEvents(self):
        return ((self.viewModel.onReroll, self.__onReroll),
         (self.viewModel.onBuyPremiumBtnClick, self.__onBuyPremiumBtn),
         (self.__parent.onIsCurrentMissionTab, self.__onIsCurrentMissionTab),
         (self.__parent.onPlayStreakTab, self.__onPlayStreakTab))

    @adisp_process
    @args2params(bool)
    def __onReroll(self, rerollPremium):
        levelFilter = LEVELS.DAILY_PREMIUM if rerollPremium else LEVELS.DAILY_SIMPLE
        result = yield daily_quests.DailyQuestReroll(levelFilter, rerollPremium).request()
        if result.success:
            self._update()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __onIsCurrentMissionTab(self, isActive):
        self.__unseenComponent.setIsCurrentMissionTab(isActive)

    def __onPlayStreakTab(self):
        self.__unseenComponent.setIsCurrentMissionTab(False)

    def __onBuyPremiumBtn(self):
        showShop(getBuyPremiumUrl())

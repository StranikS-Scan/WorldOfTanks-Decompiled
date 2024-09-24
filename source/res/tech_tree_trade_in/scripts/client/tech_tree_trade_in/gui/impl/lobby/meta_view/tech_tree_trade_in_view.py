# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/meta_view/tech_tree_trade_in_view.py
from functools import partial
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gui_decorators import args2params
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import hideWebBrowserOverlay
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.Scaleform.Waiting import Waiting
from tech_tree_trade_in.gui.shared.event_dispatcher import pushTechTreeTradeInErrorNotification
from skeletons.gui.shared import IItemsCache
from tech_tree_trade_in.gui.scaleform.daapi.view.lobby.tech_tree_trade_in_sounds import TECH_TREE_TRADE_IN_OVERLAY_SOUND_SPACE
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tech_tree_trade_in_view_model import TechTreeTradeInViewModel, MainViews
from gui.impl.pub import ViewImpl
from tech_tree_trade_in.gui.shared import event_dispatcher
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews.branch_selection_sub_view import BranchSelectionSubView
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews.intro_sub_view import IntroSubView
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews.multicurrency_selection_sub_view import MulticurrencySelectionView
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews.post_trade_view import PostTradeView
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews.summary_view import SummaryView
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController, GuiSettingsTradeInUrlName
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews.view_helpers import SummaryRequestDataCache, ResponseType

class TechTreeTradeInView(ViewImpl):
    __slots__ = ('__moneyBalanceWidget', '__subViews', '__currentSubView', '__viewId', '__summaryRequestCache', '__errorNotificationShown')
    _COMMON_SOUND_SPACE = TECH_TREE_TRADE_IN_OVERLAY_SOUND_SPACE
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewId):
        settings = ViewSettings(R.views.tech_tree_trade_in.lobby.TechTreeTradeInView())
        settings.flags = ViewFlags.VIEW
        settings.model = TechTreeTradeInViewModel()
        self.__subViews = None
        self.__currentSubView = None
        self.__viewId = viewId
        self.__moneyBalanceWidget = MoneyBalance(layoutID=R.views.dialogs.widgets.MoneyBalance())
        self.__summaryRequestCache = None
        self.__errorNotificationShown = False
        super(TechTreeTradeInView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(TechTreeTradeInView, self).getViewModel()

    @args2params(int)
    def switchContent(self, viewType):
        self.__currentSubView = self.__subViews[MainViews(viewType)]
        self.__updateSubView()

    def switchContentWithContext(self, viewType, ctx):
        self.__currentSubView = self.__subViews[MainViews(viewType)]
        self.__updateSubView(ctx)

    def switchToSummaryView(self, price):
        branchSelectionVM = self.viewModel.branchSelectionModel
        branchToTradeId = branchSelectionVM.getSelectedBranchToTradeId()
        branchToReceiveId = branchSelectionVM.getSelectedBranchToReceiveId()
        responseType = self.__summaryRequestCache.request((branchToTradeId, branchToReceiveId), partial(self.__onTradeSummaryReceived, price), self.__onTradeSummaryRequestError)
        if responseType == ResponseType.SERVER:
            Waiting.show('updating')

    def createToolTip(self, event):
        tooltip = None
        if self.__currentSubView:
            tooltip = self.__currentSubView.createToolTip(event)
        return tooltip or super(TechTreeTradeInView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        content = None
        if self.__currentSubView.isLoaded:
            content = self.__currentSubView.createToolTipContent(event, contentID)
        return content or super(TechTreeTradeInView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(TechTreeTradeInView, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addCallback('cache.mayConsumeWalletResources', self.__moneyBalanceWidget._moneyChangeHandler)
        self.__summaryRequestCache = SummaryRequestDataCache()
        self.setChildView(self.__moneyBalanceWidget.layoutID, self.__moneyBalanceWidget)
        self.__initSubViews()
        self.__currentSubView = self.__subViews[self.__viewId]
        self.__updateSubView()

    def _finalize(self):
        hideWebBrowserOverlay()
        self.__currentSubView = None
        self.__clearSubViews()
        self.__summaryRequestCache = None
        super(TechTreeTradeInView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.mainOverlayModel.onSwitchContent, self.switchContent),
         (self.viewModel.mainOverlayModel.onShowInfo, self.__showInfo),
         (self.viewModel.mainOverlayModel.footer.onConfirm, self.__onConfirm),
         (self.__techTreeTradeInController.onSettingsChanged, self.__onSettingsChanged),
         (self.__techTreeTradeInController.onEntryPointUpdated, self.__onSettingsChanged))

    def __showInfo(self):
        urlOrNone = self.__techTreeTradeInController.getTradeInURL(GuiSettingsTradeInUrlName.INFO_PAGE)
        event_dispatcher.showBranchTechTradeInOverlay(urlOrNone)

    def __initSubViews(self):
        subViews = (IntroSubView(self.viewModel.introModel, self),
         BranchSelectionSubView(self.viewModel.branchSelectionModel, self),
         SummaryView(self.viewModel.summaryModel, self),
         PostTradeView(self.viewModel.postTradeModel, self),
         MulticurrencySelectionView(self.viewModel.multicurrencySelectionModel, self))
        self.__subViews = {sv.viewId:sv for sv in subViews}

    def __clearSubViews(self):
        if not self.__subViews:
            return
        else:
            for subView in self.__subViews.values():
                if subView is not None and subView.isLoaded:
                    subView.finalize()

            self.__subViews.clear()
            return

    def __updateSubView(self, ctx=None):
        ctx = ctx or {}
        with self.viewModel.transaction() as vm:
            vm.setViewType(self.__currentSubView.viewId)
            self.__currentSubView.initialize(ctx=ctx)

    def __onConfirm(self):
        if not self.__currentSubView:
            LOG_ERROR('TechTreeTradeIn: no current subview to call onConfirm method')
        if not hasattr(self.__currentSubView, 'onConfirm'):
            LOG_ERROR('TechTreeTradeIn: current subview has no onConfirm method', self.__currentSubView.viewId)
        self.__currentSubView.onConfirm()

    def __onTradeSummaryReceived(self, price, _, data):
        Waiting.hide('updating')
        self.switchContentWithContext(MainViews.SUMMARY, {'price': price,
         'summary': data})

    def __onTradeSummaryRequestError(self, *_, **__):
        Waiting.hide('updating')
        pushTechTreeTradeInErrorNotification()

    def __onSettingsChanged(self, *args, **kwargs):
        if not (self.__techTreeTradeInController.isEnabled() and self.__techTreeTradeInController.isActive()):
            if not self.__errorNotificationShown:
                self.__errorNotificationShown = True
                pushTechTreeTradeInErrorNotification()
                self.destroyWindow()


class TechTreeTradeInViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, viewId):
        super(TechTreeTradeInViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TechTreeTradeInView(viewId))

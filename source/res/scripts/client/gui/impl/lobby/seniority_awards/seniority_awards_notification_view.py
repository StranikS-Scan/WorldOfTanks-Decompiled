# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_notification_view.py
from account_helpers.AccountSettings import AccountSettings, SENIORITY_AWARDS_WINDOW_SHOWN
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPlayerSeniorityAwardsUrl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_notification_view_model import SeniorityAwardsNotificationViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.event_dispatcher import showShop
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import ISeniorityAwardsController
from skeletons.gui.shared import IItemsCache

class SeniorityAwardsNotificationView(ViewImpl):
    __slots__ = ('__delayer',)
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.seniority_awards.SeniorityAwardsNotificationView())
        settings.model = SeniorityAwardsNotificationViewModel()
        super(SeniorityAwardsNotificationView, self).__init__(settings)
        self.__delayer = CallbackDelayer()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SeniorityAwardsNotificationView, self)._initialize()
        self.viewModel.onOpenShopClick += self.__onOpenShopClick
        self.viewModel.onCloseAction += self.__onClose
        self.__seniorityAwardCtrl.onUpdated += self.__update
        self.__itemsCache.onSyncCompleted += self.__update
        self.__connectionMgr.onDisconnected += self.__onDisconnect
        AccountSettings.setSessionSettings(SENIORITY_AWARDS_WINDOW_SHOWN, True)
        timeDelta = self.__getTimeDeltaTillShowLastCall()
        if timeDelta > 0:
            self.__delayer.delayCallback(timeDelta + 0.1, self.__updateDate)

    def _finalize(self):
        super(SeniorityAwardsNotificationView, self)._finalize()
        self.viewModel.onOpenShopClick -= self.__onOpenShopClick
        self.viewModel.onCloseAction -= self.__onClose
        self.__seniorityAwardCtrl.onUpdated -= self.__update
        self.__itemsCache.onSyncCompleted -= self.__update
        self.__connectionMgr.onDisconnected -= self.__onDisconnect
        self.__delayer.clearCallbacks()

    def _onLoading(self, *args, **kwargs):
        super(SeniorityAwardsNotificationView, self)._onLoading(*args, **kwargs)
        self.__update()

    def __update(self, *_, **__):
        if not self.__seniorityAwardCtrl.needShowNotification:
            self.destroyWindow()
            return
        specialCurrency = self.__seniorityAwardCtrl.getSACoin()
        with self.viewModel.transaction():
            self.viewModel.setSpecialCurrencyCount(specialCurrency)
            self.__updateDate()

    def __updateDate(self):
        if self.__getTimeDeltaTillShowLastCall() < 0:
            self.viewModel.setDate(int(self.__seniorityAwardCtrl.endTimestamp - time_utils.getServerUTCTime()))

    def __getTimeDeltaTillShowLastCall(self):
        return self.__seniorityAwardCtrl.showNotificationLastCallTimestamp - time_utils.getServerUTCTime()

    def __onOpenShopClick(self):
        showShop(getPlayerSeniorityAwardsUrl())
        self.destroyWindow()

    def __onDisconnect(self):
        AccountSettings.setSessionSettings(SENIORITY_AWARDS_WINDOW_SHOWN, True)
        self.destroyWindow()

    def __onClose(self):
        self.destroyWindow()


class SeniorityAwardsNotificationWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(SeniorityAwardsNotificationWindow, self).__init__(WindowFlags.WINDOW, content=SeniorityAwardsNotificationView(), parent=parent)

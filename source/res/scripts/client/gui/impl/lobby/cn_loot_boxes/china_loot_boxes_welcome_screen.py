# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_welcome_screen.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getCNLootBoxesUrl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_welcome_screen_model import ChinaLootBoxesWelcomeScreenModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showShop
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency, time_utils
from skeletons.gui.game_control import ICNLootBoxesController
DAILY_BOXES_COUNT = 30

class ChinaLootBoxesWelcomeScreen(ViewImpl):
    __slots__ = ('__isClosed', '__endDate', '__notifier')
    __cnLootBoxesCtrl = dependency.descriptor(ICNLootBoxesController)

    def __init__(self, layoutID, endDate):
        settings = ViewSettings(layoutID)
        settings.model = ChinaLootBoxesWelcomeScreenModel()
        self.__endDate = endDate
        self.__isClosed = False
        super(ChinaLootBoxesWelcomeScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChinaLootBoxesWelcomeScreen, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ChinaLootBoxesWelcomeScreen, self)._initialize(*args, **kwargs)
        self.__notifier = PeriodicNotifier(self.__getTimeLeft, self.__updateTimeLeft, (time_utils.ONE_MINUTE,))
        self.__notifier.startNotification()
        self.__addListeners()

    def _finalize(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
        self.__removeListeners()
        self.__onClose()
        super(ChinaLootBoxesWelcomeScreen, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setTimeLeft(self.__getTimeLeft())
            model.setDailyBoxesCount(DAILY_BOXES_COUNT)
        switchHangarOverlaySoundFilter(True)

    def __addListeners(self):
        self.viewModel.onBuy += self.__onBuyClick
        self.viewModel.onClose += self.__onClose
        self.__cnLootBoxesCtrl.onStatusChange += self.__onCNLootBoxesStatusChange
        self.__cnLootBoxesCtrl.onAvailabilityChange += self.__onCNLootBoxesStatusChange
        g_playerEvents.onDisconnected += self.__onDisconnected

    def __removeListeners(self):
        self.viewModel.onBuy -= self.__onBuyClick
        self.viewModel.onClose -= self.__onClose
        self.__cnLootBoxesCtrl.onStatusChange -= self.__onCNLootBoxesStatusChange
        self.__cnLootBoxesCtrl.onAvailabilityChange -= self.__onCNLootBoxesStatusChange
        g_playerEvents.onDisconnected -= self.__onDisconnected

    def __onClose(self):
        if not self.__isClosed:
            switchHangarOverlaySoundFilter(False)
            self.__cnLootBoxesCtrl.onWelcomeScreenClosed()
        self.__isClosed = True

    def __onBuyClick(self):
        showShop(getCNLootBoxesUrl())

    def __onCNLootBoxesStatusChange(self, *_):
        if not self.__cnLootBoxesCtrl.isActive() or not self.__cnLootBoxesCtrl.isLootBoxesAvailable():
            self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()

    @replaceNoneKwargsModel
    def __updateTimeLeft(self, model=None):
        model.setTimeLeft(self.__getTimeLeft())

    def __getTimeLeft(self):
        return max(self.__endDate - time_utils.getServerUTCTime() * time_utils.MS_IN_SECOND, 0)


class ChinaLootBoxesWelcomeScreenWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, endDate):
        super(ChinaLootBoxesWelcomeScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ChinaLootBoxesWelcomeScreen(R.views.lobby.cn_loot_boxes.ChinaLootBoxesWelcomeScreen(), endDate))

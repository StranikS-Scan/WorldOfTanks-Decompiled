# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_welcome_screen.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_welcome_screen_model import ChinaLootBoxesWelcomeScreenModel
from gui.impl.lobby.cn_loot_boxes.tooltips.china_loot_box_infotype import ChinaLootBoxTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.gui_items.loot_box import ChinaLootBoxes
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency, time_utils
from skeletons.gui.game_control import ICNLootBoxesController, IEntitlementsController

class ChinaLootBoxesWelcomeScreen(ViewImpl):
    __slots__ = ('__isClosed', '__notifier')
    __cnLootBoxes = dependency.descriptor(ICNLootBoxesController)
    __entitlements = dependency.descriptor(IEntitlementsController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.cn_loot_boxes.ChinaLootBoxesWelcomeScreen())
        settings.model = ChinaLootBoxesWelcomeScreenModel()
        self.__isClosed = False
        super(ChinaLootBoxesWelcomeScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChinaLootBoxesWelcomeScreen, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ChinaLootBoxTooltip(boxType=ChinaLootBoxes.PREMIUM)

    def _initialize(self, *args, **kwargs):
        super(ChinaLootBoxesWelcomeScreen, self)._initialize(*args, **kwargs)
        self.__notifier = PeriodicNotifier(self.__getTimeLeft, self.__updateTimeLeft, (time_utils.ONE_MINUTE,))
        self.__notifier.startNotification()

    def _finalize(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
        self.__onClose()
        super(ChinaLootBoxesWelcomeScreen, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setTimeLeft(self.__getTimeLeft())
            model.setDailyBoxesCount(self.__cnLootBoxes.getDayLimit())
            model.setEndDate(self.__getEndDate())
            model.setIsBuyAvailable(self.__cnLootBoxes.isBuyAvailable())
            model.setGuaranteedLimit(self.__cnLootBoxes.getGuaranteedBonusLimit(ChinaLootBoxes.PREMIUM))
        switchHangarOverlaySoundFilter(True)

    def _onLoaded(self, *args, **kwargs):
        super(ChinaLootBoxesWelcomeScreen, self)._onLoaded(*args, **kwargs)
        self.__updateBuyAvailability()

    def _getEvents(self):
        return ((self.viewModel.onBuy, self.__onBuyClick),
         (self.viewModel.onClose, self.__onClose),
         (self.__cnLootBoxes.onStatusChange, self.__onCNLootBoxesStatusChange),
         (self.__cnLootBoxes.onAvailabilityChange, self.__onCNLootBoxesStatusChange),
         (self.__entitlements.onCacheUpdated, self.__updateBuyAvailability),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def __onClose(self):
        if not self.__isClosed:
            switchHangarOverlaySoundFilter(False)
            self.__cnLootBoxes.setIntroWasShown(True)
        self.__isClosed = True

    def __onBuyClick(self):
        self.__cnLootBoxes.openExternalShopPage()

    def __onCNLootBoxesStatusChange(self, *_):
        if self.__cnLootBoxes.isActive() and self.__cnLootBoxes.isLootBoxesAvailable():
            self.viewModel.setIsBuyAvailable(self.__cnLootBoxes.isBuyAvailable())
        else:
            self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()

    @replaceNoneKwargsModel
    def __updateTimeLeft(self, model=None):
        model.setTimeLeft(self.__getTimeLeft())

    def __getTimeLeft(self):
        return max(self.__getEndDate() - time_utils.getServerUTCTime(), 0)

    def __getEndDate(self):
        _, endDate = self.__cnLootBoxes.getEventActiveTime()
        return endDate

    @replaceNoneKwargsModel
    def __updateBuyAvailability(self, model=None):
        model.setIsBuyAvailable(self.__cnLootBoxes.isBuyAvailable())


class ChinaLootBoxesWelcomeScreenWindow(WindowImpl):
    __slots__ = ()

    def __init__(self):
        super(ChinaLootBoxesWelcomeScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ChinaLootBoxesWelcomeScreen())

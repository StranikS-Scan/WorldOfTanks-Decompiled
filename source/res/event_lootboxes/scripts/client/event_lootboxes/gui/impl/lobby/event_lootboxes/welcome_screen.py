# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/lobby/event_lootboxes/welcome_screen.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.welcome_screen_model import WelcomeScreenModel
from tooltips.loot_box_tooltip import EventLootBoxTooltip
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventLootBoxesController, IEntitlementsController

class EventLootBoxesWelcomeScreen(ViewImpl):
    __slots__ = ('__isClosed', '__notifier')
    __eventLootBoxes = dependency.descriptor(IEventLootBoxesController)
    __entitlements = dependency.descriptor(IEntitlementsController)

    def __init__(self):
        settings = ViewSettings(R.views.event_lootboxes.lobby.event_lootboxes.WelcomeScreen())
        settings.model = WelcomeScreenModel()
        self.__isClosed = False
        super(EventLootBoxesWelcomeScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventLootBoxesWelcomeScreen, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EventLootBoxTooltip(boxType=EventLootBoxes.PREMIUM)

    def _initialize(self, *args, **kwargs):
        super(EventLootBoxesWelcomeScreen, self)._initialize(*args, **kwargs)
        self.__notifier = PeriodicNotifier(self.__getTimeLeft, self.__updateTimeLeft, (time_utils.ONE_MINUTE,))
        self.__notifier.startNotification()

    def _finalize(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
        self.__onClose()
        super(EventLootBoxesWelcomeScreen, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(EventLootBoxesWelcomeScreen, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setTimeLeft(self.__getTimeLeft())
            model.setDailyBoxesCount(self.__eventLootBoxes.getDayLimit())
            model.setEndDate(self.__getEndDate())
            model.setIsBuyAvailable(self.__eventLootBoxes.isBuyAvailable())
            model.setGuaranteedText(self.__getGuaranteedText())
            model.setUseExternalShop(self.__eventLootBoxes.useExternalShop())
        switchHangarOverlaySoundFilter(True)

    def _onLoaded(self, *args, **kwargs):
        self.__updateBuyAvailability()

    def _getEvents(self):
        return ((self.viewModel.onBuy, self.__onBuyClick),
         (self.viewModel.onClose, self.__onClose),
         (self.__eventLootBoxes.onStatusChange, self.__onLootBoxesStatusChange),
         (self.__eventLootBoxes.onAvailabilityChange, self.__onLootBoxesStatusChange),
         (self.__entitlements.onCacheUpdated, self.__updateBuyAvailability),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def __onClose(self):
        if not self.__isClosed:
            switchHangarOverlaySoundFilter(False)
            self.__eventLootBoxes.setIntroWasShown(True)
        self.__isClosed = True

    def __onBuyClick(self):
        self.__eventLootBoxes.openShop()

    def __onLootBoxesStatusChange(self, *_):
        if self.__eventLootBoxes.isActive() and self.__eventLootBoxes.isLootBoxesAvailable():
            self.viewModel.setIsBuyAvailable(self.__eventLootBoxes.isBuyAvailable())
        else:
            self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()

    @replaceNoneKwargsModel
    def __updateBuyAvailability(self, model=None):
        model.setIsBuyAvailable(self.__eventLootBoxes.isBuyAvailable())

    @replaceNoneKwargsModel
    def __updateTimeLeft(self, model=None):
        model.setTimeLeft(self.__getTimeLeft())

    def __getTimeLeft(self):
        return max(self.__getEndDate() - time_utils.getServerUTCTime(), 0)

    def __getEndDate(self):
        _, endDate = self.__eventLootBoxes.getEventActiveTime()
        return endDate

    def __getGuaranteedText(self):
        guaranteedLimit = self.__eventLootBoxes.getGuaranteedBonusLimit(EventLootBoxes.PREMIUM)
        fails = guaranteedLimit - 1
        levels = toRomanRangeString(self.__eventLootBoxes.getVehicleLevels(EventLootBoxes.PREMIUM))
        return backport.text(R.strings.event_lootboxes.welcomeScreen.content.guaranteedText(), fails=fails, guaranteed=guaranteedLimit, levels=levels)


class EventLootBoxesWelcomeScreenWindow(WindowImpl):
    __slots__ = ()

    def __init__(self):
        super(EventLootBoxesWelcomeScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EventLootBoxesWelcomeScreen())

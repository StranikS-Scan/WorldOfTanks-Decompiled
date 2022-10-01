# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_storage_screen.py
from PlayerEvents import g_playerEvents
from constants import LOOTBOX_TOKEN_PREFIX
from frameworks.wulf import ViewSettings, WindowFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_storage_screen_model import ChinaLootBoxesStorageScreenModel
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.storage_box_model import BoxType, StorageBoxModel
from gui.impl.lobby.cn_loot_boxes.china_loot_boxes_sound import enterLootBoxState, exitLootBoxState, playStorageClosed, playStorageOpened
from gui.impl.lobby.cn_loot_boxes.tooltips.china_loot_box_infotype import ChinaLootBoxTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showCNLootBoxOpenErrorWindow, showCNLootBoxOpenWindow
from gui.shared.gui_items.loot_box import ChinaLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import ICNLootBoxesController, IEntitlementsController

class ChinaLootBoxesStorageScreen(ViewImpl):
    __slots__ = ('__notifier', '__hasPremiumBoxes', '__isClosed', '__eventEndNotifier')
    __cnLootBoxes = dependency.descriptor(ICNLootBoxesController)
    __entitlementsController = dependency.descriptor(IEntitlementsController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = ChinaLootBoxesStorageScreenModel()
        self.__notifier = None
        self.__eventEndNotifier = None
        self.__hasPremiumBoxes = False
        self.__isClosed = False
        super(ChinaLootBoxesStorageScreen, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(ChinaLootBoxesStorageScreen, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.cn_loot_boxes.tooltips.ChinaLootBoxInfoType():
            boxType = event.getArgument('type')
            return ChinaLootBoxTooltip(boxType=boxType)
        return super(ChinaLootBoxesStorageScreen, self).createToolTipContent(event=event, contentID=contentID)

    def _initialize(self, *args, **kwargs):
        super(ChinaLootBoxesStorageScreen, self)._initialize(*args, **kwargs)
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        if self.__eventEndNotifier is not None:
            self.__eventEndNotifier.stopNotification()
            self.__eventEndNotifier.clear()
            self.__eventEndNotifier = None
        self.__onClose()
        super(ChinaLootBoxesStorageScreen, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(ChinaLootBoxesStorageScreen, self)._onLoading()
        self.__notifier = PeriodicNotifier(self.__getTimeLeft, self.__updateBuyAvailability, (time_utils.ONE_MINUTE,))
        self.__notifier.startNotification()
        self.__eventEndNotifier = PeriodicNotifier(self.__getEventEndTimeLeft, self.__updateEventEndTimeLeft, (time_utils.ONE_MINUTE,))
        self.__eventEndNotifier.startNotification()
        with self.viewModel.transaction() as model:
            self.__updateLootBoxesAvailability(model=model)
            self.__updateEventEndTimeLeft(model=model)
            self.__updateBuyAvailability(model=model)
            model.setDayLimit(self.__cnLootBoxes.getDayLimit())
            for boxId in (BoxType.COMMON, BoxType.PREMIUM):
                box = StorageBoxModel()
                box.setType(boxId)
                model.boxes.addViewModel(box)

            self.__updateBoxesCount(model=model)
        playStorageOpened(self.__hasPremiumBoxes)
        enterLootBoxState()

    def __addListeners(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__cnLootBoxes.onStatusChange += self.__onEventUpdated
        self.__cnLootBoxes.onAvailabilityChange += self.__onEventUpdated
        self.viewModel.onBuyBoxes += self.__onBuyBoxes
        self.viewModel.onClose += self.__onClose
        boxes = self.viewModel.boxes.getItems()
        for box in boxes:
            box.onOpen += self.__onOpenBox

        g_playerEvents.onDisconnected += self.__onDisconnected

    def __removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__cnLootBoxes.onStatusChange -= self.__onEventUpdated
        self.__cnLootBoxes.onAvailabilityChange -= self.__onEventUpdated
        self.viewModel.onBuyBoxes -= self.__onBuyBoxes
        self.viewModel.onClose -= self.__onClose
        boxes = self.viewModel.boxes.getItems()
        for box in boxes:
            box.onOpen -= self.__onOpenBox

        g_playerEvents.onDisconnected -= self.__onDisconnected

    def __onClose(self):
        if not self.__isClosed:
            playStorageClosed()
            exitLootBoxState()
        self.__isClosed = True

    @replaceNoneKwargsModel
    def __updateLootBoxesAvailability(self, model=None):
        model.setIsLootBoxesEnabled(self.__cnLootBoxes.isLootBoxesAvailable())

    @replaceNoneKwargsModel
    def __updateBoxesCount(self, model=None):
        self.__hasPremiumBoxes = False
        storeInfo = self.__cnLootBoxes.getStoreInfo()
        for box in model.boxes.getItems():
            boxInfo = storeInfo.get(box.getType().value)
            if boxInfo is not None:
                boxCount = boxInfo.getInventoryCount()
                box.setCount(boxCount)
                if boxCount > 0 and box.getType().value == ChinaLootBoxes.PREMIUM:
                    self.__hasPremiumBoxes = True

        return

    @replaceNoneKwargsModel
    def __updateBuyAvailability(self, model=None):
        isCacheInited = self.__entitlementsController.isCacheInited()
        model.setIsEntitlementCacheInited(isCacheInited)
        boxesLeft = max(self.__cnLootBoxes.getDayLimit() - self.__cnLootBoxes.getDayInfoStatistics(), 0)
        model.setBoxesLeft(boxesLeft)
        if not boxesLeft and isCacheInited:
            model.setIsBuyAvailable(False)
            currentUTCTime = time_utils.getServerUTCTime()
            dayTimeLeft = self.__cnLootBoxes.getTimeLeftToResetPurchase()
            _, finish = self.__cnLootBoxes.getEventActiveTime()
            isLastEventDay = finish - currentUTCTime <= dayTimeLeft
            if not isLastEventDay:
                model.setTimeLeft(self.__getTimeLeft() * time_utils.MS_IN_SECOND)
            else:
                model.setIsLastDay(True)

    @replaceNoneKwargsModel
    def __updateEventEndTimeLeft(self, model=None):
        model.setEventEndTimeLeft(self.__getEventEndTimeLeft())

    def __onEventUpdated(self, *_):
        if self.__cnLootBoxes.isActive():
            self.__updateLootBoxesAvailability()
            self.__updateEventEndTimeLeft()
            self.__updateBuyAvailability()
        else:
            self.destroyWindow()

    def __onTokensUpdate(self, diff):
        for token in diff.iterkeys():
            if token.startswith(LOOTBOX_TOKEN_PREFIX):
                self.__updateBoxesCount()
                return

    @decorators.adisp_process('loadContent')
    def __onOpenBox(self, args):
        boxType = args.get('type')
        if boxType is not None:
            box = self.__cnLootBoxes.getStoreInfo().get(boxType)
            if self.__cnLootBoxes.isLootBoxesAvailable() and box is not None and box.getInventoryCount() > 0:
                result = yield LootBoxOpenProcessor(box, 1).request()
                self.destroyWindow()
                if result and result.success:
                    showCNLootBoxOpenWindow(boxType, rewards=result.auxData)
                else:
                    showCNLootBoxOpenErrorWindow()
        return

    def __onBuyBoxes(self):
        self.__cnLootBoxes.openShop()

    def __getTimeLeft(self):
        boxesLeft = self.__cnLootBoxes.getDayLimit() > self.__cnLootBoxes.getDayInfoStatistics()
        return self.__cnLootBoxes.getTimeLeftToResetPurchase() + time_utils.ONE_SECOND if not boxesLeft else 0

    def __getEventEndTimeLeft(self):
        _, finish = self.__cnLootBoxes.getEventActiveTime()
        return max((finish - time_utils.getServerUTCTime()) * time_utils.MS_IN_SECOND, 0)

    def __onDisconnected(self):
        self.destroyWindow()


class ChinaLootBoxesStorageScreenWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(ChinaLootBoxesStorageScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ChinaLootBoxesStorageScreen(R.views.lobby.cn_loot_boxes.ChinaLootBoxesStorageScreen()), parent=parent)

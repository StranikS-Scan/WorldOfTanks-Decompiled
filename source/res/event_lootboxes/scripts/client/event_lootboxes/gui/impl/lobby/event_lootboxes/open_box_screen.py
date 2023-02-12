# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/lobby/event_lootboxes/open_box_screen.py
import logging
import BigWorld
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import LOOT_BOXES_OPEN_ANIMATION_ENABLED
from frameworks.wulf import ViewSettings, WindowFlags
from event_lootboxes.gui.event_lootboxes.bonuses_packers import packBonusModelAndTooltipData
from sound import enterLootBoxSoundState, exitLootBoxSoundState, playStorageClosed, playStorageOpened
from event_lootboxes.gui.impl.lobby.event_lootboxes.tooltips.compensation_tooltip import EventLootBoxesCompensationTooltip
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.vehicle_model import VehicleType
from gui.Scaleform.Waiting import Waiting
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.open_box_screen_model import BoxType, OSBit, OpenBoxScreenModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import GoldBonus, IntegralBonus
from gui.shared.event_dispatcher import selectVehicleInHangar
from event_lootboxes.gui.shared.event_dispatcher import showEventLootBoxOpenErrorWindow, showEventLootBoxOpenWindow
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.gui_items.loot_box import EVENT_LOOT_BOXES_CATEGORY, EventLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventLootBoxesController
_logger = logging.getLogger(__name__)
_OS_BIT_MAP = {1: OSBit.X86,
 2: OSBit.X64,
 3: OSBit.UNKNOWN}

class EventLootBoxesOpenBoxScreen(ViewImpl):
    __slots__ = ('__compensationTooltipData', '__rewards', '__tooltipData', '__boxType', '__vehicle', '__bonuses', '__notifier', '__osBit')
    __eventLootBoxes = dependency.descriptor(IEventLootBoxesController)

    def __init__(self, layoutID, rewards, boxType):
        settings = ViewSettings(layoutID)
        settings.model = OpenBoxScreenModel()
        self.__tooltipData = {}
        self.__compensationTooltipData = {}
        self.__rewards = rewards
        self.__boxType = boxType
        self.__vehicle = None
        self.__bonuses = []
        statistics = BigWorld.wg_getClientStatistics()
        self.__osBit = _OS_BIT_MAP[statistics.get('osBit', 3)] if statistics else OSBit.UNKNOWN
        super(EventLootBoxesOpenBoxScreen, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(EventLootBoxesOpenBoxScreen, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EventLootBoxesCompensationTooltip(self.__compensationTooltipData) if contentID == R.views.event_lootboxes.lobby.event_lootboxes.tooltips.CompensationTooltip() else super(EventLootBoxesOpenBoxScreen, self).createToolTipContent(event=event, contentID=contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltipData.get(tooltipId, None)
            if tooltipData is None:
                _logger.warning('Tooltip data not found. tooltipId=%s, tooltipData=%s', tooltipId, self.__tooltipData)
                return
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(EventLootBoxesOpenBoxScreen, self).createToolTip(event)

    def update(self, *args, **kwargs):
        self.__vehicle = None
        self.__boxType = kwargs.get('boxType')
        self.__rewards = kwargs.get('rewards')
        self.__updateData()
        self.__updateCounters()
        return

    def _initialize(self, *args, **kwargs):
        super(EventLootBoxesOpenBoxScreen, self)._initialize(*args, **kwargs)
        self.__notifier = PeriodicNotifier(self.__getTimeLeft, self.__updateBuyAvailability, (time_utils.ONE_MINUTE,))
        self.__notifier.startNotification()

    def _finalize(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
        self.__onHideWaiting()
        super(EventLootBoxesOpenBoxScreen, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.changeAnimationState, self.__changeAnimationState),
         (self.viewModel.openNextBox, self.__onOpenBox),
         (self.viewModel.buyBox, self.__onBuyBox),
         (self.viewModel.hideWaiting, self.__onHideWaiting),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.showVehicleInHangar, self.__onShowVehicleInHangar),
         (self.__eventLootBoxes.onBoxesCountChange, self.__updateBoxesCount),
         (self.__eventLootBoxes.onAvailabilityChange, self.__onAvailabilityChange),
         (self.__eventLootBoxes.onAvailabilityChange, self.__onStatusChange),
         (self.__eventLootBoxes.onStatusChange, self.__onStatusChange),
         (self.__eventLootBoxes.onBoxesUpdate, self.__updateMainRewardBoxesLeft),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _onLoading(self, *args, **kwargs):
        super(EventLootBoxesOpenBoxScreen, self)._onLoading(*args, **kwargs)
        self.__onShowWaiting()
        self.__updateData()
        enterLootBoxSoundState()

    def _onLoaded(self, *args, **kwargs):
        self.__onHideWaiting()
        self.__updateCounters()
        self.__inBoxesFlowEnter()

    def __updateData(self):
        with self.viewModel.transaction() as model:
            self.__updateAnimationState(model=model)
            self.__updateBuyAvailability(model=model)
            self.__updateAvailabilityChange(model=model)
            self.__updateBoxesCount()
            model.setMainRewardBoxesLeft(self.__eventLootBoxes.boxCountToGuaranteedBonus)
            model.setDayLimit(self.__eventLootBoxes.getDayLimit())
            model.setBoxType(BoxType(self.__boxType))
            model.setOsBit(self.__osBit)
            model.setGuaranteedLimit(self.__eventLootBoxes.getGuaranteedBonusLimit(EventLootBoxes.PREMIUM))
            model.setUseExternalShop(self.__eventLootBoxes.useExternalShop())
            self.__setRewards(model=model)

    def __updateCounters(self):
        self.__updateBoxesCount()
        self.__updateMainRewardBoxesLeft()

    def __onClose(self):
        exitLootBoxSoundState()

    def __changeAnimationState(self):
        isAnimationActive = self.__eventLootBoxes.getSetting(EVENT_LOOT_BOXES_CATEGORY, LOOT_BOXES_OPEN_ANIMATION_ENABLED)
        self.__eventLootBoxes.setSetting(EVENT_LOOT_BOXES_CATEGORY, LOOT_BOXES_OPEN_ANIMATION_ENABLED, not isAnimationActive)
        if self.__osBit == OSBit.X64:
            self.__updateAnimationState()

    @replaceNoneKwargsModel
    def __updateAnimationState(self, model=None):
        isAnimationActive = self.__eventLootBoxes.getSetting(EVENT_LOOT_BOXES_CATEGORY, LOOT_BOXES_OPEN_ANIMATION_ENABLED) and self.__osBit == OSBit.X64
        model.setIsAnimationActive(isAnimationActive)

    @replaceNoneKwargsModel
    def __updateBuyAvailability(self, model=None):
        boxesLeft = self.__getBoxesToBuyLeft()
        model.setPurchasesLeft(boxesLeft)
        if not boxesLeft:
            model.setIsBuyAvailable(False)
            nextBuyDate, _ = time_utils.getDayTimeBoundsForUTC(time_utils.getServerUTCTime() + time_utils.ONE_DAY)
            _, finish = self.__eventLootBoxes.getEventActiveTime()
            if nextBuyDate < finish:
                self.__updateTimeLeft()
            else:
                model.setIsLastDay(True)
        else:
            model.setIsBuyAvailable(True)

    @replaceNoneKwargsModel
    def __updateTimeLeft(self, model=None):
        model.setTimeLeft(self.__getTimeLeft() * time_utils.MS_IN_SECOND)

    def __updateBoxesCount(self, *_):
        with self.viewModel.transaction() as model:
            model.setBoxCount(self.__getBoxCount())

    def __setRewards(self, model=None):
        model.rewards.clearItems()
        model.setHasVehicle(False)
        self.__bonuses = BattlePassAwardsManager.composeBonuses(self.__rewards['bonus'])
        packBonusModelAndTooltipData(self.__bonuses, model.rewards, tooltipData=self.__tooltipData, vehicleModel=model.vehicle)
        vehicleBonuses = [ bonus for bonus in self.__bonuses if bonus.getName() == 'vehicles' ]
        if vehicleBonuses:
            vehicleBonus = vehicleBonuses[0]
            self.__vehicle, _ = vehicleBonus.getVehicles()[0]
            if vehicleBonus.checkIsCompensatedVehicle(self.__vehicle):
                self.__setCompensationTooltipData(vehicleBonus)
            else:
                self.__setVehicle(model)

    def __setVehicle(self, model):
        model.vehicle.setName(self.__vehicle.userName)
        model.vehicle.setType(VehicleType(self.__vehicle.type))
        model.vehicle.setLevel(self.__vehicle.level)
        iconSource = R.images.gui.maps.shop.vehicles.c_600x450.dyn(getNationLessName(self.__vehicle.name))()
        model.vehicle.setIconSource(iconSource)
        model.setHasVehicle(True)

    def __setCompensationTooltipData(self, vehicleBonus):
        compensationBonuses = (bonus for bonus in vehicleBonus.compensation(self.__vehicle, vehicleBonus) if isinstance(bonus, (IntegralBonus, GoldBonus)))
        compensation = {}
        for currency in Currency.BY_WEIGHT:
            value = sum([ int(b.getValue()) for b in compensationBonuses if b.getName() == currency ] + [0])
            if value > 0:
                compensation = {'currency': currency,
                 'value': value}
                break

        self.__compensationTooltipData = {'iconBefore': R.images.gui.maps.shop.vehicles.c_180x135.dyn(getNationLessName(self.__vehicle.name))(),
         'vehicleLevel': self.__vehicle.level,
         'vehicleType': self.__vehicle.type,
         'vehicleName': self.__vehicle.userName,
         'compensation': compensation}

    def __getBoxesToBuyLeft(self):
        return max(self.__eventLootBoxes.getDayLimit() - self.__eventLootBoxes.getDayInfoStatistics(), 0)

    @decorators.adisp_process('loadContent')
    def __onOpenBox(self):
        box = self.__eventLootBoxes.getStoreInfo(EVENT_LOOT_BOXES_CATEGORY).get(self.__boxType)
        if self.__eventLootBoxes.isLootBoxesAvailable() and box is not None and box.getInventoryCount() > 0:
            result = yield LootBoxOpenProcessor(box, 1).request()
            if result and result.success:
                showEventLootBoxOpenWindow(self.__boxType, rewards=result.auxData)
            else:
                showEventLootBoxOpenErrorWindow()
        return

    def __onShowVehicleInHangar(self):
        if self.__vehicle is not None:
            self.destroyWindow()
            selectVehicleInHangar(self.__vehicle.intCD)
        return

    def __onBuyBox(self):
        self.__eventLootBoxes.openShop()

    def __onShowWaiting(self):
        Waiting.show('loadContent')

    def __onHideWaiting(self):
        Waiting.hide('loadContent')

    def __getBoxCount(self):
        box = self.__eventLootBoxes.getStoreInfo(EVENT_LOOT_BOXES_CATEGORY).get(self.__boxType)
        return box.getInventoryCount() if box is not None else 0

    def __getTimeLeft(self):
        boxesLeft = self.__eventLootBoxes.getDayLimit() > self.__eventLootBoxes.getDayInfoStatistics()
        return self.__eventLootBoxes.getTimeLeftToResetPurchase() + time_utils.ONE_SECOND if not boxesLeft else 0

    def __onStatusChange(self, *_):
        if not self.__eventLootBoxes.isActive() or not self.__eventLootBoxes.isLootBoxesAvailable():
            self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()

    def __onAvailabilityChange(self, *_):
        self.__updateAvailabilityChange()

    @replaceNoneKwargsModel
    def __updateAvailabilityChange(self, model=None):
        model.setIsLootBoxAvailable(self.__eventLootBoxes.isLootBoxesAvailable())

    @replaceNoneKwargsModel
    def __updateMainRewardBoxesLeft(self, model=None):
        model.setMainRewardBoxesLeft(self.__eventLootBoxes.boxCountToGuaranteedBonus)

    @staticmethod
    def __inBoxesFlowEnter():
        playStorageOpened()

    @staticmethod
    def __inBoxesFlowExit():
        playStorageClosed()


class EventLootBoxesOpenBoxScreenWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, boxType=None, rewards=None):
        super(EventLootBoxesOpenBoxScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EventLootBoxesOpenBoxScreen(R.views.event_lootboxes.lobby.event_lootboxes.OpenBoxScreen(), rewards=rewards, boxType=boxType))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_open_box_screen.py
import logging
import BigWorld
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CN_LOOT_BOXES_OPEN_ANIMATION_STATE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.cn_loot_boxes.cn_loot_box_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_open_box_screen_model import BoxType, ChinaLootBoxesOpenBoxScreenModel, OSBit
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.vehicle_model import VehicleType
from gui.impl.lobby.cn_loot_boxes.china_loot_boxes_sound import enterLootBoxState, exitLootBoxState, playStorageOpened, playStorageClosed
from gui.impl.lobby.cn_loot_boxes.tooltips.china_loot_boxes_compensation_tooltip import ChinaLootBoxesCompensationTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import GoldBonus, IntegralBonus
from gui.shared.event_dispatcher import selectVehicleInHangar, showCNLootBoxOpenErrorWindow, showCNLootBoxOpenWindow
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.gui_items.loot_box import ChinaLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import ICNLootBoxesController
_logger = logging.getLogger(__name__)
_OS_BIT_MAP = {1: OSBit.X86,
 2: OSBit.X64,
 3: OSBit.UNKNOWN}

class _ScreenState(object):

    def __init__(self):
        self.__isInBoxesFlow = False

    @property
    def isInBoxesFlow(self):
        return self.__isInBoxesFlow

    @isInBoxesFlow.setter
    def isInBoxesFlow(self, value):
        self.__isInBoxesFlow = value


_SCREEN_STATE = _ScreenState()

class ChinaLootBoxesOpenBoxScreen(ViewImpl):
    __slots__ = ('__compensationTooltipData', '__rewards', '__tooltipData', '__boxType', '__vehicle', '__bonuses', '__notifier', '__isClosed', '__osBit', '__isOpenInProgress')
    __cnLootBoxes = dependency.descriptor(ICNLootBoxesController)

    def __init__(self, layoutID, rewards, boxType):
        settings = ViewSettings(layoutID)
        settings.model = ChinaLootBoxesOpenBoxScreenModel()
        self.__tooltipData = {}
        self.__compensationTooltipData = {}
        self.__rewards = rewards
        self.__boxType = boxType
        self.__vehicle = None
        self.__bonuses = []
        self.__isClosed = False
        self.__isOpenInProgress = False
        statistics = BigWorld.wg_getClientStatistics()
        self.__osBit = _OS_BIT_MAP[statistics.get('osBit', 3)] if statistics else OSBit.UNKNOWN
        super(ChinaLootBoxesOpenBoxScreen, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(ChinaLootBoxesOpenBoxScreen, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ChinaLootBoxesCompensationTooltip(self.__compensationTooltipData) if contentID == R.views.lobby.cn_loot_boxes.tooltips.ChinaLootBoxesCompensationTooltip() else super(ChinaLootBoxesOpenBoxScreen, self).createToolTipContent(event=event, contentID=contentID)

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
            return super(ChinaLootBoxesOpenBoxScreen, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(ChinaLootBoxesOpenBoxScreen, self)._initialize(*args, **kwargs)
        self.__notifier = PeriodicNotifier(self.__getTimeLeft, self.__updateBuyAvailability, (time_utils.ONE_MINUTE,))
        self.__notifier.startNotification()

    def _finalize(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
        self.__onHideWaiting()
        super(ChinaLootBoxesOpenBoxScreen, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.changeAnimationState, self.__changeAnimationState),
         (self.viewModel.openNextBox, self.__onOpenBox),
         (self.viewModel.buyBox, self.__onBuyBox),
         (self.viewModel.hideWaiting, self.__onHideWaiting),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.showVehicleInHangar, self.__onShowVehicleInHangar),
         (self.__cnLootBoxes.onBoxesCountChange, self.__updateBoxesCount),
         (self.__cnLootBoxes.onAvailabilityChange, self.__onAvailabilityChange),
         (self.__cnLootBoxes.onAvailabilityChange, self.__onStatusChange),
         (self.__cnLootBoxes.onStatusChange, self.__onStatusChange),
         (self.__cnLootBoxes.onBoxesUpdate, self.__updateMainRewardBoxesLeft),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _onLoading(self, *args, **kwargs):
        super(ChinaLootBoxesOpenBoxScreen, self)._onLoading(*args, **kwargs)
        Waiting.show('loadContent')
        with self.viewModel.transaction() as model:
            self.__updateAnimationState(model=model)
            self.__updateBuyAvailability(model=model)
            self.__updateAvailabilityChange(model=model)
            self.__updateBoxesCount()
            model.setMainRewardBoxesLeft(self.__cnLootBoxes.boxCountToGuaranteedBonus)
            model.setDayLimit(self.__cnLootBoxes.getDayLimit())
            model.setBoxType(BoxType(self.__boxType))
            model.setOsBit(self.__osBit)
            model.setGuaranteedLimit(self.__cnLootBoxes.getGuaranteedBonusLimit(ChinaLootBoxes.PREMIUM))
            self.__setRewards(model=model)
        enterLootBoxState()

    def _onLoaded(self, *args, **kwargs):
        self.__inBoxesFlowEnter()
        if not AccountSettings.getSettings(CN_LOOT_BOXES_OPEN_ANIMATION_STATE):
            self.__onHideWaiting()
        self.__updateBoxesCount()
        self.__updateMainRewardBoxesLeft()

    def __onClose(self):
        if not self.__isClosed:
            exitLootBoxState()
            self.__inBoxesFlowExit()
        self.__isClosed = True

    def __changeAnimationState(self):
        isAnimationActive = AccountSettings.getSettings(CN_LOOT_BOXES_OPEN_ANIMATION_STATE)
        AccountSettings.setSettings(CN_LOOT_BOXES_OPEN_ANIMATION_STATE, not isAnimationActive)
        if self.__osBit == OSBit.X64:
            self.__updateAnimationState()

    @replaceNoneKwargsModel
    def __updateAnimationState(self, model=None):
        isAnimationActive = AccountSettings.getSettings(CN_LOOT_BOXES_OPEN_ANIMATION_STATE) and self.__osBit == OSBit.X64
        model.setIsAnimationActive(isAnimationActive)

    @replaceNoneKwargsModel
    def __updateBuyAvailability(self, model=None):
        boxesLeft = self.__getBoxesToBuyLeft()
        model.setPurchasesLeft(boxesLeft)
        if not boxesLeft:
            model.setIsBuyAvailable(False)
            nextBuyDate, _ = time_utils.getDayTimeBoundsForUTC(time_utils.getServerUTCTime() + time_utils.ONE_DAY)
            _, finish = self.__cnLootBoxes.getEventActiveTime()
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

        self.__compensationTooltipData = {'iconBefore': R.images.gui.maps.shop.vehicles.c_600x450.dyn(getNationLessName(self.__vehicle.name))(),
         'vehicleLevel': self.__vehicle.level,
         'vehicleType': self.__vehicle.type,
         'vehicleName': self.__vehicle.userName,
         'compensation': compensation}

    def __getBoxesToBuyLeft(self):
        return max(self.__cnLootBoxes.getDayLimit() - self.__cnLootBoxes.getDayInfoStatistics(), 0)

    @decorators.process('loadContent')
    def __onOpenBox(self):
        if self.__isOpenInProgress:
            return
        else:
            self.__isOpenInProgress = True
            box = self.__cnLootBoxes.getStoreInfo().get(self.__boxType)
            if self.__cnLootBoxes.isLootBoxesAvailable() and box is not None and box.getInventoryCount() > 0:
                result = yield LootBoxOpenProcessor(box, 1).request()
                self.destroyWindow()
                if result and result.success:
                    showCNLootBoxOpenWindow(self.__boxType, rewards=result.auxData)
                else:
                    showCNLootBoxOpenErrorWindow()
            return

    def __onShowVehicleInHangar(self):
        if self.__vehicle is not None:
            self.destroyWindow()
            selectVehicleInHangar(self.__vehicle.intCD)
        return

    def __onBuyBox(self):
        self.__cnLootBoxes.openExternalShopPage()

    def __onHideWaiting(self):
        Waiting.hide('loadContent')

    def __getBoxCount(self):
        box = self.__cnLootBoxes.getStoreInfo().get(self.__boxType)
        return box.getInventoryCount() if box is not None else 0

    def __getTimeLeft(self):
        boxesLeft = self.__cnLootBoxes.getDayLimit() > self.__cnLootBoxes.getDayInfoStatistics()
        return self.__cnLootBoxes.getTimeLeftToResetPurchase() + time_utils.ONE_SECOND if not boxesLeft else 0

    def __onStatusChange(self, *_):
        if not self.__cnLootBoxes.isActive() or not self.__cnLootBoxes.isLootBoxesAvailable():
            self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()

    def __onAvailabilityChange(self, *_):
        self.__updateAvailabilityChange()

    @replaceNoneKwargsModel
    def __updateAvailabilityChange(self, model=None):
        model.setIsLootBoxAvailable(self.__cnLootBoxes.isLootBoxesAvailable())

    @replaceNoneKwargsModel
    def __updateMainRewardBoxesLeft(self, model=None):
        model.setMainRewardBoxesLeft(self.__cnLootBoxes.boxCountToGuaranteedBonus)

    @staticmethod
    def __inBoxesFlowEnter():
        if not _SCREEN_STATE.isInBoxesFlow:
            playStorageOpened()
            _SCREEN_STATE.isInBoxesFlow = True

    @staticmethod
    def __inBoxesFlowExit():
        playStorageClosed()
        _SCREEN_STATE.isInBoxesFlow = False


class ChinaLootBoxesOpenBoxScreenWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, boxType=None, rewards=None):
        super(ChinaLootBoxesOpenBoxScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ChinaLootBoxesOpenBoxScreen(R.views.lobby.cn_loot_boxes.ChinaLootBoxesOpenBoxScreen(), rewards=rewards, boxType=boxType))

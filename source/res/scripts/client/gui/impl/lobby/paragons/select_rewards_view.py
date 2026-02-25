# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/select_rewards_view.py
import logging
import th_async
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, ViewStatus
from gui.Scaleform.Waiting import Waiting
from gui.game_control.paragons_reward_controller import ProductsStates
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.common.request_status_model import RequestStatus
from gui.impl.gen.view_models.views.lobby.paragons.select_rewards_view_model import SelectRewardsViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.paragons.paragons_window_events import loadParagonsWithRewardSelector
from gui.impl.lobby.paragons.tooltips.selected_rewards_tooltip import SelectedRewardsTooltip
from gui.impl.lobby.paragons.sound_constants import PARAGONS_PREVIEW_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.paragons.paragons_bonuses_packers import getParagonsBonusPacker
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import showVehiclePreview
from helpers import dependency
from BWUtil import AsyncReturn
from paragons_common import PARAGONS_SEASON_PRODUCT_TAG_PREFIX
from skeletons.gui.game_control import IParagonsRewardsShopController, IVehicleComparisonBasket, IParagonsController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_MAX_AVAILABLE_TO_SELECT = 1

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getVehicleBonus(key, value, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(value)
    return [] if vehicle.isInInventory or vehicle.isRestorePossible() else getNonQuestBonuses('vehicles', {value: {}})


_PRODUCT_DATA_KEY_BONUS_FACTORY = {'vehicleCD': _getVehicleBonus}

def _getBonusesFromProduct(productData):
    bonuses = []
    for key, value in productData.iteritems():
        if key in _PRODUCT_DATA_KEY_BONUS_FACTORY:
            bonuses.extend(_PRODUCT_DATA_KEY_BONUS_FACTORY[key](key, value))

    return bonuses


def _getSeasonFromProduct(productData):
    season = 0
    tags = productData.get('tags')
    for tag in tags:
        if tag.startswith(PARAGONS_SEASON_PRODUCT_TAG_PREFIX):
            season = int(tag[len(PARAGONS_SEASON_PRODUCT_TAG_PREFIX):])
            break

    return season


class SelectRewardsView(ViewImpl):
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __selectableRewardsCtrl = dependency.descriptor(IParagonsRewardsShopController)
    __paragonsCtrl = dependency.descriptor(IParagonsController)
    __slots__ = ('__rewards', '__entitlementID', '__tooltipData', '__chapterID', '__levelID', '__asyncScope', '__asyncEvent')

    def __init__(self, layoutID, chapterID, levelID, entitlementID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = SelectRewardsViewModel()
        self.__rewards = {}
        self.__chapterID = chapterID
        self.__levelID = levelID
        self.__entitlementID = entitlementID
        self.__tooltipData = {}
        self.__asyncScope = th_async.AsyncScope()
        self.__asyncEvent = th_async.AsyncEvent(scope=self.__asyncScope)
        super(SelectRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SelectRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SelectRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def createToolTipContent(self, event, contentID):
        return SelectedRewardsTooltip(event.getArgument('selectedCDs').split(','), contentID) if contentID == R.views.lobby.paragons.tooltips.SelectedRewardsTooltip() else None

    def _finalize(self):
        super(SelectRewardsView, self)._finalize()
        self.__asyncScope.destroy()

    def _onLoading(self, *args, **kwargs):
        super(SelectRewardsView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setAvailableToSelect(self.__getAvailableToSelectEntitlements())
            model.setLevel(self.__levelID)
            self.__fillRewards(model=model)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onClaim, self.__onClaim),
         (self.viewModel.onCompare, self.__onCompare),
         (self.viewModel.onPreview, self.__onPreview),
         (self.__selectableRewardsCtrl.entitlements.onEntitlementsUpdated, self.__onEntitlementsUpdated),
         (self.__selectableRewardsCtrl.onSelectableRewardReceived, self.__onSelectableRewardReceived),
         (self.__paragonsCtrl.onFeatureStateChanged, self.__onFeatureStateChanged))

    def __onClose(self):
        self.destroyWindow()

    @th_async.th_async
    @replaceNoneKwargsModel
    def __fillRewards(self, model=None):
        state, products = yield th_async.await_callback(self.__getProducts)()
        if self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING):
            raise AsyncReturn(None)
        if state == ProductsStates.EMPTY:
            model.requestStatus.setStatus(RequestStatus.FAILED)
        else:
            packer = getParagonsBonusPacker()
            bonusIndex = 0
            bonusModelsList = model.getAvailableRewards()
            for productCode, product in products.iteritems():
                if not self.__selectableRewardsCtrl.isValidProduct(product, self.__entitlementID):
                    continue
                bonuses = _getBonusesFromProduct(product)
                for bonus in (b for b in bonuses if b.isShowInGUI()):
                    bonusList = packer.pack(bonus)
                    bTooltipList = packer.getToolTip(bonus)
                    bContentIdList = packer.getContentId(bonus)
                    for bSubIndex, bModel in enumerate(bonusList):
                        bModel.setIndex(bonusIndex)
                        bModel.setTooltipId(str(bonusIndex))
                        self.__tooltipData[str(bonusIndex)] = bTooltipList[bSubIndex]
                        bModel.setTooltipContentId(str(bContentIdList[bSubIndex]))
                        bModel.setSeasonID(_getSeasonFromProduct(product))
                        bonusModelsList.addViewModel(bModel)
                        self.__rewards[bonusIndex] = productCode
                        bonusIndex += 1

            bonusModelsList.invalidate()
        return

    def __getAvailableToSelectEntitlements(self):
        currentLevelID = self.__paragonsCtrl.paragons.getProgressByChapterID(self.__chapterID)
        return min(self.__selectableRewardsCtrl.entitlements.getEntitlementsByID(self.__entitlementID), int(currentLevelID >= self.__levelID), _MAX_AVAILABLE_TO_SELECT)

    @th_async.th_async
    @args2params(int)
    def __onClaim(self, rewardId):
        try:
            Waiting.show('paragons/selectReward')
            productCode = self.__rewards[rewardId]
            self.viewModel.requestStatus.setStatus(RequestStatus.INPROCESS)
            isSuccess, _ = yield th_async.th_await(self.__selectableRewardsCtrl.buyProductAndMarkReward)(productCode, self.__chapterID, self.__levelID, self.__entitlementID)
            if self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING):
                raise AsyncReturn(None)
            if isSuccess:
                if not self.__asyncEvent.is_set():
                    yield th_async.th_await(self.__asyncEvent.wait(), timeout=10)
                if self.viewStatus not in (ViewStatus.DESTROYED, ViewStatus.DESTROYING):
                    self.destroyWindow()
            else:
                self.viewModel.requestStatus.setStatus(RequestStatus.FAILED)
        finally:
            Waiting.hide('paragons/selectReward')

        return

    @args2params(int)
    def __onCompare(self, vehicleCD):
        self.__cmpBasket.addVehicle(vehicleCD)

    @args2params(int)
    def __onPreview(self, vehicleCD):
        showVehiclePreview(vehicleCD, previewBackCb=self.__returnToThisWindow, previewAlias=VIEW_ALIAS.VEHICLE_PREVIEW, backBtnLabel=backport.text(R.strings.paragons.vehiclePreview.backButton()), soundSpace=PARAGONS_PREVIEW_SOUND_SPACE)
        self.destroyWindow()

    def __onEntitlementsUpdated(self):
        self.viewModel.setAvailableToSelect(self.__getAvailableToSelectEntitlements())

    def __onFeatureStateChanged(self, isPaused, isEnabled):
        if not isEnabled or isPaused:
            self.destroyWindow()

    @adisp_process
    def __getProducts(self, callback=None):
        res = yield self.__selectableRewardsCtrl.getProducts()
        callback(res)

    @adisp_process
    def __buyProducts(self, productCode, callback=None):
        res = yield self.__selectableRewardsCtrl.buyProduct(productCode)
        callback(res)

    def __onSelectableRewardReceived(self, data):
        self.__asyncEvent.set()

    def __returnToThisWindow(self):
        loadParagonsWithRewardSelector(self.__chapterID, self.__levelID, self.__entitlementID)


class SelectRewardsViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, chapterID, levelID, entitlementID, parent=None):
        super(SelectRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SelectRewardsView(R.views.lobby.paragons.SelectRewardsView(), chapterID, levelID, entitlementID), parent=parent)

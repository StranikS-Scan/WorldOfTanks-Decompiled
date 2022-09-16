# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/awards/multiple_awards_view.py
import logging
import typing
from adisp import adisp_process
from constants import RentType
from frameworks.wulf import ViewSettings, ViewStatus, ViewFlags
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.awards.multiple_awards_view_model import MultipleAwardsViewModel
from gui.impl.gen.view_models.views.lobby.awards.tooltips.awards_vehicle_for_choose_tooltip_view_model import AwardsVehicleForChooseTooltipViewModel
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.awards import SupportedTokenTypes
from gui.impl.lobby.awards.tooltip import VEH_FOR_CHOOSE_ID
from gui.impl.lobby.awards.tooltip.vehicle_for_choose import VehicleForChooseTooltipContent
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import event_dispatcher
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
from gui.impl.gen.view_models.views.lobby.awards.reward_model import RewardModel, RentTypeEnum
if typing.TYPE_CHECKING:
    from gui.platform.catalog_service.controller import _PurchaseDescriptor
_logger = logging.getLogger(__name__)

class MultipleAwardsView(ViewImpl):
    __purchaseCache = dependency.descriptor(IPurchaseCache)
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __slots__ = ('__tooltipItems', '__vehicleIntCD', '__offer')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.awards.MultipleAwardsView(), model=MultipleAwardsViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(MultipleAwardsView, self).__init__(settings)
        self.__tooltipItems = {}
        self.__vehicleIntCD = None
        self.__offer = None
        return

    @property
    def viewModel(self):
        return super(MultipleAwardsView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(MultipleAwardsView, self)._initialize(*args, **kwargs)
        self.viewModel.onClose += self.__onClose
        self.viewModel.showHangar += self.__handleShowHangar
        self.viewModel.makeChoice += self.__handleMakeChoice

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(MultipleAwardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipId = event.getArgument('tooltipId')
        if event.contentID == R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent():
            if tooltipId in self.__tooltipItems:
                tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
                 'labelBefore': event.getArgument('labelBefore', ''),
                 'iconAfter': event.getArgument('iconAfter', ''),
                 'labelAfter': event.getArgument('labelAfter', ''),
                 'bonusName': event.getArgument('bonusName', ''),
                 'countBefore': event.getArgument('countBefore', 1),
                 'tooltipType': LootBoxCompensationTooltipTypes.VEHICLE}
                tooltipData.update(self.__tooltipItems[tooltipId].specialArgs)
                settings = ViewSettings(R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent())
                settings.flags = ViewFlags.VIEW
                settings.model = LootBoxVehicleCompensationTooltipModel()
                settings.kwargs = tooltipData
                return VehicleCompensationTooltipContent(settings)
            _logger.warning("Couldn't find corresponded tooltip! tooltipId=%s", str(tooltipId))
        elif event.contentID == VEH_FOR_CHOOSE_ID:
            if tooltipId in self.__tooltipItems:
                settings = ViewSettings(VEH_FOR_CHOOSE_ID)
                settings.flags = ViewFlags.VIEW
                settings.model = AwardsVehicleForChooseTooltipViewModel()
                settings.kwargs = self.__tooltipItems[tooltipId].specialArgs
                return VehicleForChooseTooltipContent(settings)
            _logger.warning("Couldn't find corresponded tooltip! tooltipId=%s", str(tooltipId))
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    @adisp_process
    def _onLoading(self, rewards, tooltips, productCode, *args, **kwargs):
        super(MultipleAwardsView, self)._onLoading(*args, **kwargs)
        self.__tooltipItems = tooltips
        yield lambda callback: callback(True)
        if productCode:
            purchasePackage = yield self.__purchaseCache.requestPurchaseByID(productCode)
            if self.__isDestroyed():
                return
            with self.viewModel.transaction() as model:
                productTitle = purchasePackage.getTitleID()
                if productTitle:
                    model.setTitle(backport.text(R.strings.awards.multipleAwards.steam.dyn(productTitle)(), name=purchasePackage.getProductName()))
                productIconID = purchasePackage.getIconID()
                if productIconID:
                    model.setTitleIcon(backport.image(R.images.gui.maps.icons.awards.multipleAwards.title.dyn(productIconID)()))
                self.__setProductTypeData(rewards)
                model.setMainItemsCount(purchasePackage.getMainAmount())
                for vR in rewards:
                    model.rewards.addViewModel(vR)

        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        self.viewModel.onClose -= self.__onClose
        self.viewModel.showHangar -= self.__handleShowHangar
        self.viewModel.makeChoice -= self.__handleMakeChoice
        self.__tooltipItems = None
        self.__vehicleIntCD = None
        self.__offer = None
        super(MultipleAwardsView, self)._finalize()
        return

    def __isDestroyed(self):
        destroyed = self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING)
        return destroyed or self.viewModel is None

    def __extendSortedBonusList(self, sortedBList, extraData):
        for order, extItem in extraData.iterItems():
            sortedBList.insert(order, extItem)

    def __setProductTypeData(self, rewards):
        offersForChoice = set()
        vehicles = []
        hasVehicleForChoice = False
        rentVehicles = 0
        maxRentVehiclesForChoice = 0
        for reward in rewards:
            if isinstance(reward, RewardModel):
                rewardItemID = reward.getItemID()
                if rewardItemID:
                    rewardItemName = reward.getName()
                    if rewardItemName in SupportedTokenTypes.ALL():
                        offer = self.__offersProvider.getOffer(rewardItemID)
                        if offer:
                            giftVehiclesForChoice = 0
                            offersForChoice.add(rewardItemID)
                            for gift in offer.getAllGifts():
                                if gift.isVehicle:
                                    if gift.rentType != RentType.NO_RENT:
                                        hasVehicleForChoice = True
                                        giftVehiclesForChoice += 1
                                        if giftVehiclesForChoice > maxRentVehiclesForChoice:
                                            maxRentVehiclesForChoice = giftVehiclesForChoice

                        else:
                            _logger.warning("Couldn't get offer by tokenID = %s", str(rewardItemID))
                    elif rewardItemName == 'vehicles' or rewardItemName == 'vehicles_rent':
                        vehicles.append(rewardItemID)
                        if reward.getVehicleRentType() != RentTypeEnum.NONE:
                            rentVehicles += 1

        if maxRentVehiclesForChoice > 1:
            subtitle = R.strings.awards.multipleAwards.status.onChoiceRentMultiple()
        elif hasVehicleForChoice:
            subtitle = R.strings.awards.multipleAwards.status.onChoiceRentSingle()
        elif rentVehicles > 1:
            subtitle = R.strings.awards.multipleAwards.status.rentMultiple()
        elif rentVehicles == 1:
            subtitle = R.strings.awards.multipleAwards.status.rentSingle()
        elif offersForChoice:
            subtitle = R.strings.awards.multipleAwards.status.onChoice()
        else:
            subtitle = R.strings.awards.multipleAwards.status.base()
        self.__offer = next(iter(offersForChoice)) if len(offersForChoice) == 1 else None
        self.__vehicleIntCD = vehicles[0] if len(vehicles) == 1 else None
        self.viewModel.setSubTitle(backport.text(subtitle))
        self.viewModel.setHasRewardsOnChoice(bool(offersForChoice))
        self.viewModel.setHasVehicleToView(bool(self.__vehicleIntCD))
        return

    def __onClose(self):
        self.destroyWindow()

    def __handleShowHangar(self):
        event_dispatcher.selectVehicleInHangar(self.__vehicleIntCD)
        self.destroyWindow()

    def __handleMakeChoice(self):
        if self.__offer:
            event_dispatcher.showOfferGiftsWindow(self.__offer)
        else:
            event_dispatcher.showStorage(STORAGE_CONSTANTS.OFFERS)


class MultipleAwardsViewWindow(LobbyNotificationWindow):
    __slots__ = ('__blur',)

    def __init__(self, rewards, tooltips, productCode):
        super(MultipleAwardsViewWindow, self).__init__(content=self._getContentView(rewards, tooltips, productCode))
        self.__blur = None
        return

    def load(self):
        if self.__blur is None:
            self.__blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)
        super(MultipleAwardsViewWindow, self).load()
        return

    @classmethod
    def _getContentView(cls, rewards, tooltips, productCode):
        return MultipleAwardsView(rewards=rewards, tooltips=tooltips, productCode=productCode)

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(MultipleAwardsViewWindow, self)._finalize()
        return

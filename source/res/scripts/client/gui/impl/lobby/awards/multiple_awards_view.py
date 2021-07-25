# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/awards/multiple_awards_view.py
import logging
from copy import deepcopy
import typing
from adisp import process
from constants import OFFER_TOKEN_PREFIX, RentType
from frameworks.wulf import ViewSettings, ViewStatus, ViewFlags
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.battle_pass.battle_pass_award import awardsFactory
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.awards.multiple_awards_view_model import MultipleAwardsViewModel
from gui.impl.gen.view_models.views.lobby.awards.tooltips.awards_vehicle_for_choose_tooltip_view_model import AwardsVehicleForChooseTooltipViewModel
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.awards.packers import packBonusModelAndTooltipData
from gui.impl.lobby.awards.tooltip import VEH_FOR_CHOOSE_ID
from gui.impl.lobby.awards.tooltip.vehicle_for_choose import VehicleForChooseTooltipContent
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import TokensBonus, VehiclesBonus, mergeBonuses
from gui.shared import event_dispatcher
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from items.components import component_constants
from skeletons.gui.cdn import IPurchaseCache
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from gui.cdn.controller import _PurchaseDescriptor
_logger = logging.getLogger(__name__)
_MAX_AWARDS = 10

def _deepupdate(original, update):
    for key, value in original.iteritems():
        if key not in update:
            update[key] = value
        if isinstance(value, dict):
            _deepupdate(value, update[key])


def _getSortedBonusList(bonusData, order):
    sortedList = []
    for oItem in order:
        for oKey, oVal in oItem.iteritems():
            bDataSection = bonusData.get(oKey)
            if bDataSection:
                if isinstance(bDataSection, dict):
                    if isinstance(oVal, dict):
                        for oValKey in oVal.iterkeys():
                            if oValKey in bDataSection:
                                sortedList.append({oKey: {oValKey: bDataSection[oValKey]}})
                                del bDataSection[oValKey]

                        if not bDataSection:
                            del bonusData[oKey]
                    else:
                        _logger.error('The type of items in order list and data section does not correspond to one another!')
                else:
                    sortedList.append({oKey: bDataSection})
                    del bonusData[oKey]

    if bonusData:
        sortedList.append(bonusData)
    return sortedList


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

    @process
    def _onLoading(self, invoiceData, *args, **kwargs):
        super(MultipleAwardsView, self)._onLoading(*args, **kwargs)
        yield lambda callback: callback(True)
        metaData = invoiceData.get('meta', {})
        productCode = self.__purchaseCache.getProductCode(metaData)
        if productCode:
            bonusData = deepcopy(invoiceData['data'])
            compensation = invoiceData.get('compensation', {})
            _deepupdate(compensation, bonusData)
            bonuses = []
            for bData in _getSortedBonusList(bonusData, metaData.get('order', component_constants.EMPTY_TUPLE)):
                bonuses.extend(awardsFactory(bData))

            bonuses = mergeBonuses(bonuses)
            viewRevards, self.__tooltipItems = yield packBonusModelAndTooltipData(bonuses[:_MAX_AWARDS], productCode)
            purchasePackage = yield self.__purchaseCache.requestPurchaseByID(productCode)
            destroyed = self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING)
            if destroyed or self.viewModel is None:
                return
            productTitle = purchasePackage.getTitleID()
            if productTitle:
                self.viewModel.setTitle(backport.text(R.strings.awards.multipleAwards.steam.dyn(productTitle)(), name=purchasePackage.getProductName()))
            productIconID = purchasePackage.getIconID()
            if productIconID:
                self.viewModel.setTitleIcon(backport.image(R.images.gui.maps.icons.awards.multipleAwards.title.dyn(productIconID)()))
            self.__setProductTypeData(bonuses)
            self.viewModel.setMainItemsCount(purchasePackage.getMainAmount())
            for vR in viewRevards:
                self.viewModel.rewards.addViewModel(vR)

        return

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.showHangar -= self.__handleShowHangar
        self.viewModel.makeChoice -= self.__handleMakeChoice
        self.__tooltipItems = None
        self.__vehicleIntCD = None
        self.__offer = None
        super(MultipleAwardsView, self)._finalize()
        return

    def __setProductTypeData(self, bonuses):
        offersForChoice = []
        vehicles = []
        hasVehicleForChoice = False
        rentVehicles = 0
        maxRentVehiclesForChoice = 0
        for bonus in bonuses:
            if isinstance(bonus, TokensBonus):
                for tID in bonus.getTokens():
                    if tID.startswith(OFFER_TOKEN_PREFIX):
                        for offer in self.__offersProvider.getAvailableOffersByToken(tID):
                            giftVehiclesForChoice = 0
                            offersForChoice.append(offer.id)
                            for gift in offer.getAllGifts():
                                if gift.isVehicle:
                                    if gift.rentType != RentType.NO_RENT:
                                        hasVehicleForChoice = True
                                        giftVehiclesForChoice += 1
                                        if giftVehiclesForChoice > maxRentVehiclesForChoice:
                                            maxRentVehiclesForChoice = giftVehiclesForChoice

            if isinstance(bonus, VehiclesBonus):
                for vehicle, vehInfo in bonus.getVehicles():
                    vehicles.append(vehicle.intCD)
                    if bonus.isRentVehicle(vehInfo):
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
        self.__offer = offersForChoice[0] if len(offersForChoice) == 1 else None
        self.__vehicleIntCD = vehicles[0] if len(vehicles) == 1 else None
        self.viewModel.setSubTitle(backport.text(subtitle))
        self.viewModel.setHasRewardsOnChoice(bool(offersForChoice))
        self.viewModel.setHasVehicleToView(bool(self.__vehicleIntCD))
        return

    def __onClose(self):
        self.destroyWindow()

    def __handleShowHangar(self):
        event_dispatcher.selectVehicleInHangar(self.__vehicleIntCD)

    def __handleMakeChoice(self):
        if self.__offer:
            event_dispatcher.showOfferGiftsWindow(self.__offer)
        else:
            event_dispatcher.showStorage(STORAGE_CONSTANTS.OFFERS)


class MultipleAwardsViewWindow(LobbyNotificationWindow):
    __slots__ = ('__blur',)

    def __init__(self, invoiceData):
        super(MultipleAwardsViewWindow, self).__init__(content=MultipleAwardsView(invoiceData=invoiceData))
        self.__blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)

    def _finalize(self):
        self.__blur.fini()
        super(MultipleAwardsViewWindow, self)._finalize()

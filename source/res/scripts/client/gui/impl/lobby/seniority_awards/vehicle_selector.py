# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/vehicle_selector.py
from collections import OrderedDict
import logging
from adisp import adisp_process
from frameworks.wulf import ViewSettings, ViewStatus, WindowFlags, WindowLayer
from gui import GUI_NATIONS, SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.seniority_awards.vehicle_bonus_model import VehicleBonusModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.vehicle_selector_model import VehicleSelectorModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.lobby.seniority_awards.popovers.vehicle_filter_popover import VehicleFilterPopover
from gui.impl.lobby.seniority_awards.tooltips.selected_rewards_tooltip import SelectedRewardsTooltip
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.selectable_reward.common import SelectableRewardManager
from gui.shared.gui_items.processors.offers import ReceiveMultipleOfferGiftsProcessor
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from helpers import dependency
from skeletons.gui.offers import IOffersDataProvider
from tutorial.control.game_vars import getVehicleByIntCD
_NATIONS_KEY_NAME = 'Nations'
_TYPES_KEY_NAME = 'Types'
_TYPES_ORDER = ('heavyTank', 'mediumTank', 'lightTank', 'AT-SPG', 'SPG')
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent
_logger = logging.getLogger(__name__)

class VehicleSelector(FullScreenDialogBaseView):
    __slots__ = ('__vehicles', '__giftToken', '__vehicleToGiftID', '__filters', '__filterPopover', '__selectedVehicles')
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    _helper = SelectableRewardManager

    def __init__(self, layoutID, giftToken):
        settings = ViewSettings(layoutID)
        settings.model = VehicleSelectorModel()
        self.__vehicles = []
        self.__vehicleToGiftID = {}
        self.__filters = {}
        self.__filterPopover = None
        self.__resetFilters(True)
        self.__giftToken = giftToken
        self.__selectedVehicles = None
        super(VehicleSelector, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(VehicleSelector, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(VehicleSelector, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.seniority_awards.tooltips.SelectedRewardsTooltip():
            vehicleCDs = event.getArgument('selectedVehicles', [])
            if vehicleCDs:
                vehicleCDs = map(int, vehicleCDs.split(':'))
            return SelectedRewardsTooltip(contentID, vehicleCDs)
        return super(VehicleSelector, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        if event.contentID == R.views.lobby.seniority_awards.popovers.VehicleFilterPopover():
            self.__filterPopover = VehicleFilterPopover(self.__filters, self.onUpdateFilter)
            return self.__filterPopover
        return super(VehicleSelector, self).createPopOverContent(event)

    def onUpdateFilter(self, filters=None):
        if filters:
            self.__filters = filters
        self.__updateVehicles()

    def _onLoading(self, *args, **kwargs):
        super(VehicleSelector, self)._onLoading(*args, **kwargs)
        self.__getVehiclesFromGiftToken()
        self._fillModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onApplySelect, self.__processReward), (self.viewModel.onFilterReset, self.__resetFilters))

    @replaceNoneKwargsModel
    def _fillModel(self, model=None):
        offer = self.__offersProvider.getOfferByGiftToken(self.__giftToken)
        model.setAvailableToSelectCount(offer.availableTokens)
        model.setAvailableVehiclesCount(len(self.__vehicles))
        model.setFinishSelectTimeStamp(int(offer.expiration))
        if not offer.isOfferAvailable:
            model.setIsError(True)
        self._fillVehiclesModel(model)

    def _fillVehiclesModel(self, model):
        vehicles = model.getVehicles()
        vehicles.clear()
        for vehicle in self.__vehicles:
            vehicleModel = self.__packVehicleModel(vehicle)
            vehicles.addViewModel(vehicleModel)

        vehicles.invalidate()

    def __packVehicleModel(self, vehicle):
        vehicleModel = VehicleBonusModel()
        vehicleModel.setVehicleLvl(vehicle.level)
        vehicleModel.setUserName(vehicle.userName)
        vehicleModel.setName(vehicle.name.split(':')[-1])
        vehicleModel.setNation(vehicle.nationName)
        vehicleModel.setVehicleCD(vehicle.intCD)
        vehicleModel.setType(vehicle.type)
        vehicleModel.setTooltipId(str(vehicle.intCD))
        vehicleModel.setTooltipContentId(str(_R_BACKPORT_TOOLTIP()))
        return vehicleModel

    def _processReceivedRewards(self, result):
        if result.success and result.auxData:
            self._setResult(DialogButtons.SUBMIT)
            self.destroyWindow()
        else:
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.seniority_awards.rewardChoice.error()), type=SystemMessages.SM_TYPE.Error)

    @replaceNoneKwargsModel
    def __updateVehicles(self, model=None):
        isNationsFilterEmpty = self.__isFilterEmpty(_NATIONS_KEY_NAME)
        isTypesFilterEmpty = self.__isFilterEmpty(_TYPES_KEY_NAME)
        vehicles = model.getVehicles()
        vehicles.clear()
        for vehicle in self.__vehicles:
            if isNationsFilterEmpty and isTypesFilterEmpty or isTypesFilterEmpty and self.__nationFit(vehicle) or isNationsFilterEmpty and self.__typeFit(vehicle) or self.__nationFit(vehicle) and self.__typeFit(vehicle):
                vehicleModel = self.__packVehicleModel(vehicle)
                vehicles.addViewModel(vehicleModel)

        vehicles.invalidate()

    def __isFilterEmpty(self, key):
        return not any((value for value in self.__filters[key].itervalues()))

    def __nationFit(self, vehicle):
        return self.__filters[_NATIONS_KEY_NAME][vehicle.nationName]

    def __typeFit(self, vehicle):
        return self.__filters[_TYPES_KEY_NAME][vehicle.type]

    def __resetFilters(self, init=False):
        self.__filters = {_NATIONS_KEY_NAME: OrderedDict(((nation, False) for nation in GUI_NATIONS)),
         _TYPES_KEY_NAME: OrderedDict(((t, False) for t in VEHICLE_TYPES_ORDER))}
        if self.__filterPopover and self.__filterPopover.viewStatus == ViewStatus.LOADED:
            self.__filterPopover.updateFilterFromOutside(self.__filters)
        elif not init:
            self.onUpdateFilter()

    def __onClose(self):
        self._setResult(DialogButtons.CANCEL)
        self.destroyWindow()

    def __processReward(self, event):
        vehicleCDs = event.get('selectedVehicles').split(':')
        vehicleCDs = map(int, vehicleCDs)
        self.__selectedVehicles = vehicleCDs
        if vehicleCDs and not [ item for item in vehicleCDs if item not in self.__vehicleToGiftID ]:
            self.__chooseRewards([ self.__vehicleToGiftID[veh] for veh in vehicleCDs ])
        else:
            _logger.error('[SENIORITY_AWARDS] Invalid veh intCDs %s', vehicleCDs)

    def _getAdditionalData(self):
        return self.__selectedVehicles

    @adisp_process
    def __chooseRewards(self, giftIDs):
        offer = self.__offersProvider.getOfferByGiftToken(self.__giftToken)
        result = yield ReceiveMultipleOfferGiftsProcessor({offer.id: giftIDs}).request()
        self._processReceivedRewards(result)

    def __getBackportTooltipData(self, event):
        vehicleCD = event.getArgument('vehicleCD')
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SENIORITY_AWARD_VEHICLE, specialArgs=(vehicleCD,
         100,
         None,
         None,
         None,
         None,
         True,
         True))

    def __getVehiclesFromGiftToken(self):
        offer = self.__offersProvider.getOfferByGiftToken(self.__giftToken)
        self.__vehicles = []
        for bonus in offer.availableGifts:
            if bonus.isVehicle:
                vehicle = getVehicleByIntCD(bonus.rawBonuses.get('vehicles').keys()[0])
                if not vehicle.isInInventory:
                    self.__vehicles.append(vehicle)
                    self.__vehicleToGiftID[vehicle.intCD] = bonus.id


class VehicleSelectorWindow(LobbyNotificationWindow):
    __slots__ = ('_wrappedView',)

    def __init__(self, giftToken):
        self._wrappedView = VehicleSelector(R.views.lobby.seniority_awards.VehicleSelector(), giftToken)
        super(VehicleSelectorWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=self._wrappedView, layer=WindowLayer.TOP_WINDOW)

    def wait(self):
        return self._wrappedView.wait()

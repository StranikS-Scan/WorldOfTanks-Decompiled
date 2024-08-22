# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/exchange/exchange_free_xp_window.py
import logging
from gui import GUI_NATIONS_ORDER_INDEX
from gui.impl.lobby.exchange.exchange_rates_helper import calculateMaxPossibleFreeXp, handleUserValuesInput, handleAndRoundStepperInput
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.utils.decorators import adisp_process
from exchange.personal_discounts_constants import EXCHANGE_RATE_FREE_XP_NAME
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_free_xp_model import ExchangeRateFreeXpModel
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_vehicles_selection_model import ExchangeRateVehiclesSelectionModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.exchange.base_exchange_window import BaseExchangeWindow
from gui.shared.gui_items.processors.common import FreeXPExchanger
from gui.shop import showBuyGoldForXpWebOverlay
from gui.veh_post_progression.models.progression import PostProgressionCompletion
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

def getLevelOfFieldModification(vehicle):
    stepId = 0
    for stepItem in vehicle.postProgression.iterOrderedSteps():
        if stepItem.isUnlocked() and not stepItem.action.isMultiAction():
            return stepItem.getLevel() - 1
        if stepItem.isReceived() and stepItem.getLevel() > stepId:
            stepId = stepItem.getLevel()

    return stepId


class ExchangeFreeXPView(BaseExchangeWindow):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, ctx=None, *args, **kwargs):
        settings = ViewSettings(layoutID, model=ExchangeRateFreeXpModel(), args=args, kwargs=kwargs)
        self.__xpSelectedForExchange = False
        self.__selectedXpFromVehicles = 0
        super(ExchangeFreeXPView, self).__init__(settings, exchangeRateType=EXCHANGE_RATE_FREE_XP_NAME, ctx=ctx)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getCallbacks(self):
        callbacks = super(ExchangeFreeXPView, self)._getCallbacks()
        return callbacks + (('stats.vehTypeXP', self.__updateData), ('stats.freeXP', self.__updateData))

    def _getEvents(self):
        eventsTuple = super(ExchangeFreeXPView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onVehiclesSelected, self.__onVehiclesSelectedChanged),)

    @replaceNoneKwargsModel
    def _updateModel(self, model=None):
        super(ExchangeFreeXPView, self)._updateModel(model=model)
        self.__updateVehiclesInfo(model=model)
        self.__onVehiclesSelectedChanged(event=self._initValues, vehiclesChanged=False, model=model)

    @replaceNoneKwargsModel
    def _setStepperValues(self, selectedGold, selectedCurrency, model=None):
        gold = min(model.getMaxGoldAmountForExchange(), selectedGold)
        xp = min(model.getMaxResourceAmountForExchange(), selectedCurrency)
        model.setGoldAmountForExchange(gold)
        model.setResourceAmountForExchange(xp)
        model.setAmountOfPersonalDiscounts(self._getDiscountsRequiredForExchange(goldForExchange=gold))

    def _setMaxAmountForExchange(self, maxGold, maxResource, model):
        if maxResource == 0:
            maxResource = self.__xpSelectedForExchange
        maxGold, maxXp = handleUserValuesInput(selectedGold=0, selectedCurrency=maxResource, validateGold=False, exchangeProvider=self.exchangeRate)
        model.setMaxResourceAmountForExchange(maxXp)
        model.setMaxGoldAmountForExchange(maxGold)

    @replaceNoneKwargsModel
    def _onSelectedValueChanged(self, params=None, model=None):
        if not params:
            currentValue = model.getResourceAmountForExchange()
            params = self._initValues if not currentValue else {'currency': currentValue}
        selectedGold, selectedCurrency = handleAndRoundStepperInput(params, exchangeRate=self.exchangeRate, validateGold=False)
        self._setStepperValues(selectedGold, selectedCurrency, model=model)

    @adisp_process('exchangeVehiclesXP')
    def _onExchange(self, data):
        goldPrice = int(data.get('gold', 0))
        if goldPrice < 1:
            _logger.debug("Parameter 'gold' parameter is incorrect %d", goldPrice)
            return
        selectedVehicles = data.get('selectedVehicles', '')
        if selectedVehicles:
            selectedVehicles = [ int(num) for num in selectedVehicles.strip('[]').split(',') ]
        if not selectedVehicles:
            _logger.debug("Parameter 'selectedVehicles' is missed for xp conversion")
            return
        eliteVcls = self.__itemsCache.items.stats.eliteVehicles
        xps = self.__itemsCache.items.stats.vehiclesXPs
        money = self.__itemsCache.items.stats.money
        xpToExchange = 0
        for vehicleCD in selectedVehicles:
            if vehicleCD in eliteVcls:
                xpToExchange += xps.get(vehicleCD, 0)

        exchangeXP = self.exchangeRate.calculateExchange(goldPrice)
        xpToExchange = min(xpToExchange, exchangeXP)
        if self._wallet.isAvailable and money.gold < goldPrice:
            self._goToGoldBuy(goldPrice)
        else:
            result = yield FreeXPExchanger(xpToExchange, selectedVehicles).request()
            self._processResult(result, xpToExchange)

    @staticmethod
    def _goToGoldBuy(gold):
        showBuyGoldForXpWebOverlay(gold)

    def __updateVehiclesInfo(self, model=None):
        vehiclesModel = model.getVehiclesSelection()
        vehiclesModel.clear()
        for vehicleCD in self.__itemsCache.items.stats.eliteVehicles:
            try:
                vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
                if not vehicle.xp or not vehicle.activeInNationGroup:
                    continue
            except Exception:
                continue

            vehicleModel = ExchangeRateVehiclesSelectionModel()
            vehicleModel.setAmountOfCombatXp(vehicle.xp)
            fillVehicleModel(vehicleModel, vehicle)
            vehicleModel.setNationOrder(GUI_NATIONS_ORDER_INDEX[vehicle.nationName])
            self.__addVehicleAdditionalInfo(vehicleModel, vehicle)
            vehiclesModel.addViewModel(vehicleModel)

        vehiclesModel.invalidate()

    @staticmethod
    def __addVehicleAdditionalInfo(model, vehicle):
        postProgressionStatus = vehicle.postProgression.isAvailable(vehicle)
        model.setIsFieldModernizationAvailable(postProgressionStatus.result)
        model.setIsFieldModernizationComplited(PostProgressionCompletion.FULL == vehicle.postProgression.getCompletion())
        model.setLevelOfFieldModernization(getLevelOfFieldModification(vehicle))

    @replaceNoneKwargsModel
    def __onVehiclesSelectedChanged(self, event=None, vehiclesChanged=True, model=None):
        if event:
            self.__selectedXpFromVehicles = int(event.get('currency', 0))
        maxXp = calculateMaxPossibleFreeXp(self.__selectedXpFromVehicles, validateGold=False)
        maxGold, maxXp = handleUserValuesInput(selectedGold=0, selectedCurrency=maxXp, validateGold=False, exchangeProvider=self.exchangeRate)
        self.__selectedXpFromVehicles = maxXp
        self._setMaxAmountForExchange(maxGold=maxGold, maxResource=maxXp, model=model)
        selectedGold, selectedXp = self.viewModel.getGoldAmountForExchange(), self.viewModel.getResourceAmountForExchange()
        if vehiclesChanged and self._initValues:
            self._initValues = {}
            return
        if vehiclesChanged or maxGold < selectedGold or maxXp < selectedXp or not selectedXp or not selectedGold:
            model.setGoldAmountForExchange(maxGold)
            model.setResourceAmountForExchange(maxXp)
            model.setAmountOfPersonalDiscounts(self._getDiscountsRequiredForExchange(goldForExchange=maxGold))

    def __updateData(self, *args):
        self._updateModel()


class ExchangeXPWindowDialog(ExchangeFreeXPView):
    __slots__ = ('_result', '_exchangeAmount')

    def __init__(self, *args, **kwargs):
        self._result, self._exchangeAmount = (None, 0)
        super(ExchangeXPWindowDialog, self).__init__(*args, **kwargs)
        return None

    def _processResult(self, result, exchangeAmount):
        self._result, self._exchangeAmount = result, exchangeAmount
        self._setResult(DialogButtons.SUBMIT)
        if result.success:
            self.destroy()

    def _goToGoldBuy(self, gold):
        super(ExchangeXPWindowDialog, self)._goToGoldBuy(gold)
        self._setNotExchangedResult()
        self.destroy()

    def _getAdditionalData(self):
        return (self._result, self._exchangeAmount)

    def _setNotExchangedResult(self):
        self._setResult(DialogButtons.CANCEL)
        self._result, self._exchangeAmount = (None, 0)
        return None

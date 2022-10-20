# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/confirm_dialog.py
from __future__ import absolute_import
import logging
from helpers import dependency
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.fitting_types import FittingTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.ammunition_buy_model import AmmunitionBuyModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.confirm_bottom_content_type import ConfirmBottomContentType
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.dialogs.contents.exchange_content import ExchangeContentResult
from gui.impl.lobby.dialogs.buy_and_exchange import BuyAndExchange
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.tank_setup.dialogs.helpers.ammunition_buy_helper import isFreeInstalling
from gui.impl.lobby.tank_setup.dialogs.main_content.main_contents import AmmunitionBuyMainContent
from gui.shared.money import ZERO_MONEY
from gui.impl.lobby.tank_setup.dialogs.bottom_content.bottom_contents import AmmunitionBuyBottomContent
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.game_control import IEventBattlesController
_logger = logging.getLogger(__name__)
_SECTION_TO_FITTING_TYPE = {TankSetupConstants.BATTLE_BOOSTERS: FittingTypes.BOOSTER,
 TankSetupConstants.CONSUMABLES: FittingTypes.EQUIPMENT,
 TankSetupConstants.HWCONSUMABLES: FittingTypes.EQUIPMENT,
 TankSetupConstants.OPT_DEVICES: FittingTypes.OPTIONAL_DEVICE,
 TankSetupConstants.BATTLE_ABILITIES: FittingTypes.BATTLE_ABILITY}

class TankSetupConfirmDialog(BuyAndExchange):
    __slots__ = ('__items', '__vehicleInvID', '__totalPrice', '_mainContent', '_buyContent', '__startState', '_itemsType')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), model=AmmunitionBuyModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__items = kwargs.pop('items', tuple())
        vehicle = kwargs.pop('vehicle', None)
        self.__vehicleInvID = vehicle.invID if vehicle is not None else None
        self.__totalPrice = sum([ item.getBuyPrice().price for item in self.__items if not isFreeInstalling(item, vehicle) ], ZERO_MONEY)
        self._mainContent = None
        self._buyContent = None
        startState = kwargs.pop('startState', None)
        self._itemsType = None
        super(TankSetupConfirmDialog, self).__init__(settings=settings, price=self.__totalPrice, startState=startState)
        self.__startState = startState if startState is not None else self._getStartStateByStats()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def items(self):
        return self.__items

    def _onLoading(self, *args, **kwargs):
        super(TankSetupConfirmDialog, self)._onLoading(*args, **kwargs)
        vehicle = self._itemsCache.items.getVehicle(self.__vehicleInvID)
        self._buyContent = AmmunitionBuyBottomContent(viewModel=self.viewModel.dealPanel, vehicle=vehicle, items=self.__items)
        self._buyContent.onLoading()
        if self.__startState == BuyAndExchangeStateEnum.EXCHANGE_CONTENT:
            filterItems = REQ_CRITERIA.INVENTORY
        else:
            filterItems = None
        self._mainContent = AmmunitionBuyMainContent(viewModel=self.viewModel.mainContent, items=self.__items, vehicleInvID=self.__vehicleInvID, itemsType=self._itemsType, filterCriteria=filterItems)
        self._mainContent.onLoading()
        return

    def _initialize(self, *args, **kwargs):
        super(TankSetupConfirmDialog, self)._initialize()
        if self._buyContent is not None:
            self._buyContent.initialize()
        if self._mainContent is not None:
            self._mainContent.initialize()
        return

    def _finalize(self):
        if self._mainContent is not None:
            self._mainContent.finalize()
        if self._buyContent is not None:
            self._buyContent.finalize()
        super(TankSetupConfirmDialog, self)._finalize()
        return

    def _onInventoryResync(self, *args, **kwargs):
        super(TankSetupConfirmDialog, self)._onInventoryResync(*args, **kwargs)
        if self._buyContent is not None:
            self._buyContent.update()
        return

    def _transitToExchange(self):
        super(TankSetupConfirmDialog, self)._transitToExchange()
        if self._mainContent is not None:
            self._mainContent.updateFilter(filterCriteria=REQ_CRITERIA.INVENTORY)
        return

    def _exchangeComplete(self, result):
        if result == ExchangeContentResult.IS_OK:
            self._onAccept()

    def _stateToContent(self):
        stateToContent = super(TankSetupConfirmDialog, self)._stateToContent()
        stateToContent[BuyAndExchangeStateEnum.BUY_NOT_REQUIRED] = ConfirmBottomContentType.SAVE_SLOTS_CONTENT
        return stateToContent

    def _buyNotRequiredAccept(self):
        self._onAccept()


class TankSetupExitConfirmDialog(TankSetupConfirmDialog):
    __slots__ = ('__rollBack',)

    def __init__(self, *args, **kwargs):
        super(TankSetupExitConfirmDialog, self).__init__(*args, **kwargs)
        self._itemsType = _SECTION_TO_FITTING_TYPE.get(kwargs.pop('fromSection', ''), None)
        self.__rollBack = False
        return

    def _onLoading(self, *args, **kwargs):
        super(TankSetupExitConfirmDialog, self)._onLoading(*args, **kwargs)
        self.viewModel.setWithRollback(True)

    def _getAdditionalData(self):
        return {'rollBack': self.__rollBack}

    def _onCancelClicked(self):
        self.__rollBack = True
        self._onCancel()

    def _onInventoryResync(self, *args, **kwargs):
        if self.__isNeedToCheckCount() and self.__isChangedInInventory():
            self._onCancel()
            return
        super(TankSetupExitConfirmDialog, self)._onInventoryResync(*args, **kwargs)

    def __isNeedToCheckCount(self):
        return self._itemsType == _SECTION_TO_FITTING_TYPE[TankSetupConstants.OPT_DEVICES]

    def __isChangedInInventory(self):
        return any((cachedItem.isInInventory != self._itemsCache.items.getItemByCD(cachedItem.intCD).isInInventory for cachedItem in self.items))


class HWTankSetupExitConfirmDialog(TankSetupExitConfirmDialog):
    _eventBattlesController = dependency.descriptor(IEventBattlesController)

    def _onLoading(self, *args, **kwargs):
        super(HWTankSetupExitConfirmDialog, self)._onLoading(*args, **kwargs)
        self._isEventHangar = self._eventBattlesController.isEventHangar()
        self._eventBattlesController.onEventDisabled += self._onEventDisabled
        self._eventBattlesController.onCompleteActivePhase += self._onCompleteActivePhase

    def _finalize(self):
        self._eventBattlesController.onEventDisabled -= self._onEventDisabled
        self._eventBattlesController.onCompleteActivePhase -= self._onCompleteActivePhase
        super(HWTankSetupExitConfirmDialog, self)._finalize()

    def _onCompleteActivePhase(self):
        progressCtrl = self._eventBattlesController.getHWProgressCtrl()
        if not progressCtrl or progressCtrl.isPostPhase():
            self._onCancelClicked()

    def _onEventDisabled(self):
        self._onCancelClicked()

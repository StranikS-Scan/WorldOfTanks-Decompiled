# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/dialogs/buy_pair_modification.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.fitting_types import FittingTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.ammunition_buy_model import AmmunitionBuyModel
from gui.impl.lobby.dialogs.auxiliary.confirmed_item_helpers import ConfirmedItemWarningTypes
from gui.impl.lobby.dialogs.buy_and_exchange import BuyAndExchange
from gui.impl.lobby.dialogs.contents.multiple_items_content import MultipleItemsContent
from gui.impl.lobby.tank_setup.dialogs.bottom_content.bottom_contents import PriceBottomContent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.veh_post_progression.models.ext_money import EXT_MONEY_ZERO
from post_progression_common import ACTION_TYPES
_logger = logging.getLogger(__name__)
ACTION_TYPE_TO_FITTING_TYPE = {ACTION_TYPES.MODIFICATION: FittingTypes.POST_PROGRESSION_MODIFICATION,
 ACTION_TYPES.PAIR_MODIFICATION: FittingTypes.POST_PROGRESSION_PAIR_MODIFICATION}

class BuyPairModificationDialog(BuyAndExchange[AmmunitionBuyModel]):
    __slots__ = ('_buyContent', '_mainContent', '__vehicle', '__toStepID', '__price', '__modID', '__item')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), model=AmmunitionBuyModel())
        settings.args = args
        settings.kwargs = kwargs
        self._buyContent = None
        self._mainContent = None
        self.__vehicle = kwargs.get('vehicle', None)
        self.__toStepID = kwargs.get('stepID', 0)
        self.__price = EXT_MONEY_ZERO
        self.__modID = kwargs.get('modID', 0)
        self.__item = None
        self.__updateData()
        super(BuyPairModificationDialog, self).__init__(settings, self.__price, kwargs.get('startState', None))
        return

    def _onLoading(self, *args, **kwargs):
        if not self.__updateData():
            self._onCancel()
            return
        self._updatePrice(self.__price)
        super(BuyPairModificationDialog, self)._onLoading(*args, **kwargs)
        self._buyContent = PriceBottomContent(viewModel=self.viewModel.dealPanel, price=self.__price)
        self._buyContent.onLoading()
        self._mainContent = BuyPairModificationMainContent(viewModel=self.viewModel.mainContent, items=[self.__item.getModificationByID(self.__modID)], vehicleInvID=self.__vehicle.invID, itemsType=ACTION_TYPE_TO_FITTING_TYPE.get(self.__item.actionType, ''))
        self._mainContent.onLoading()

    def _initialize(self, *args, **kwargs):
        super(BuyPairModificationDialog, self)._initialize()
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
        super(BuyPairModificationDialog, self)._finalize()
        return

    def _onInventoryResync(self, reason, diff):
        super(BuyPairModificationDialog, self)._onInventoryResync(reason, diff)
        changedVehicles = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self.__vehicle.intCD in changedVehicles:
            self.__vehicle = self._itemsCache.items.getItemByCD(self.__vehicle.intCD)
        if self.__updateData():
            if self._buyContent is not None:
                self._buyContent.update(self.__price)
            self._updatePrice(self.__price)
        else:
            self._onCancel()
        return

    def __updateData(self):
        if self.__vehicle is None or not self.__toStepID or not self.__modID:
            return False
        elif not self.__vehicle.postProgressionAvailability():
            return False
        else:
            step = self.__vehicle.postProgression.getStep(self.__toStepID)
            if not step.isReceived() or step.action.getPurchasedID() == self.__modID:
                _logger.error('not received or already purchased pair %s', self.__toStepID)
                return False
            self.__item = step.action
            self.__price = self.__item.getModificationByID(self.__modID).getPrice()
            return True


class BuyPairModificationMainContent(MultipleItemsContent):
    __slots__ = ('_warnings',)

    def __init__(self, viewModel, items, vehicleInvID=None, itemsType=None):
        super(BuyPairModificationMainContent, self).__init__(viewModel, items, vehicleInvID, itemsType)
        self._warnings = {}

    def onLoading(self, *args, **kwargs):
        super(BuyPairModificationMainContent, self).onLoading(*args, **kwargs)
        self._viewModel.setDemountPairModification(ConfirmedItemWarningTypes.PAIR_MODIFICATIONS_WILL_BE_DEMOUNT in self._warnings)

    def _fillItems(self, array):
        array.clear()
        for item in self._confirmedItemsPacker.packItems(items=self._items):
            array.addViewModel(item.getCofirmedItemViewModel())
            self._warnings.update(item.getWarnings())

        array.invalidate()

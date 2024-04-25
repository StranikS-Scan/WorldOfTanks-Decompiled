# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/buy_vehicle_dialog_view.py
import typing
from adisp import adisp_async, adisp_process
from wg_async import wg_await
from gui.impl.gen import R
from gui.impl.lobby.buy_vehicle_view import BuyVehicleView, VehicleBuyActionTypes
from gui.shared.gui_items.Tankman import CrewTypes
if typing.TYPE_CHECKING:
    from typing import Callable
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.shared.gui_items.Vehicle import Vehicle

class BuyVehicleDialogView(BuyVehicleView):
    _BG_DYN_ACC = R.images.historical_battles.gui.maps.icons.backgrounds.shopConfirmBackground

    def __init__(self, vehicle, vehiclePrice, buyingCallback):
        ctx = {'nationID': vehicle.nationID,
         'itemID': vehicle.innationID,
         'actionType': VehicleBuyActionTypes.BUY,
         'isTradeIn': False,
         'showOnlyCongrats': False,
         'customVehiclePrice': vehiclePrice}
        self._buyingCallback = buyingCallback
        self.__result = False
        super(BuyVehicleDialogView, self).__init__(ctx=ctx)

    def _initialize(self, *args, **kwargs):
        super(BuyVehicleDialogView, self)._initialize(*args, **kwargs)
        self.viewModel.setNation('')

    @adisp_async
    @adisp_process
    def _requestForMoneyObtainImpl(self, callback):
        isWithSlot = self.viewModel.equipmentBlock.slot.getIsSelected()
        isWithAmmo = self.viewModel.equipmentBlock.ammo.getIsSelected()
        crewTypeMap = {-1: 0,
         0: CrewTypes.SKILL_50,
         1: CrewTypes.SKILL_75,
         2: CrewTypes.SKILL_100}
        result = yield wg_await(self._buyingCallback(isWithSlot, isWithAmmo, crewTypeMap[self.getCrewType()]))
        self.__result = result
        callback(result)
        if result.success or getattr(result, 'errStr', None) == 'DISABLED':
            self.destroyWindow()
        return

    def destroyWindow(self):
        self._sendDialogResult(self.__result)

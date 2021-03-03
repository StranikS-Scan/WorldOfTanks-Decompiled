# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/dialogs/black_market_confirm_vehicle.py
from constants import Configs
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bm2021.dialogs.black_market_confirm_vehicle_model import BlackMarketConfirmVehicleModel
from gui.impl.lobby.bm2021.sound import BLACK_MARKET_CONFIRM_SOUND_SPACE
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.lobby.loot_box.loot_box_helper import setVehicleDataToModel
from gui.impl.gen.view_models.common.vehicle_model import VehicleModel
from gui.shared.gui_items.loot_box import BLACK_MARKET_ITEM_TYPE
from helpers import dependency
from skeletons.gui.game_control import IEventItemsController
from skeletons.gui.lobby_context import ILobbyContext

class BlackMarketConfirmVehicle(FullScreenDialogView):
    __slots__ = ('__vehicles', '__endDate', '__chosenVehicleId')
    _COMMON_SOUND_SPACE = BLACK_MARKET_CONFIRM_SOUND_SPACE
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventItemsCtrl = dependency.descriptor(IEventItemsController)

    def __init__(self, vehicles, chosenVehicleId, endDate):
        settings = ViewSettings(R.views.lobby.bm2021.dialogs.BlackMarketConfirmVehicle())
        settings.model = BlackMarketConfirmVehicleModel()
        super(BlackMarketConfirmVehicle, self).__init__(settings)
        self.__vehicles = vehicles
        self.__endDate = endDate
        self.__chosenVehicleId = chosenVehicleId

    @property
    def viewModel(self):
        return super(BlackMarketConfirmVehicle, self).getViewModel()

    def _addListeners(self):
        self.viewModel.onConfirm += self._onAccept
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _removeListeners(self):
        self.viewModel.onConfirm -= self._onAccept
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def _setBaseParams(self, model):
        vehicleModels = model.getVehicleList()
        for vehicleCD in self.__vehicles:
            vehicleModel = VehicleModel()
            setVehicleDataToModel(vehicleCD, vehicleModel)
            vehicleModels.addViewModel(vehicleModel)

        vehicleModels.invalidate()
        model.setChosenVehicleId(self.__chosenVehicleId)
        model.setEndDate(self.__endDate)

    def __onServerSettingsChange(self, diff):
        if Configs.LOOT_BOXES_CONFIG.value in diff:
            item = self.__eventItemsCtrl.getOwnedItemsByType(BLACK_MARKET_ITEM_TYPE)
            if item is None or not diff[Configs.LOOT_BOXES_CONFIG.value].get(item.getID(), {}).get('enabled'):
                self.destroy()
        return

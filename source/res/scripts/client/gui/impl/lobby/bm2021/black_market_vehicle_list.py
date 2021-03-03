# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/black_market_vehicle_list.py
from functools import partial
from constants import Configs
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen.view_models.views.lobby.bm2021.black_market_vehicle_list_model import BlackMarketVehicleListModel
from gui.impl.gen.view_models.common.vehicle_model import VehicleModel
from gui.impl.lobby.bm2021.sound import BLACK_MARKET_OVERLAY_SOUND_SPACE
from gui.impl.lobby.loot_box.loot_box_helper import getObtainableVehicles, setVehicleDataToModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import OptionalBlocks
from gui.Scaleform.daapi.view.lobby.vehicle_preview.hangar_switchers import CustomHangars
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showConfigurableVehiclePreview, showBlackMarketVehicleListWindow, hideVehiclePreview
from gui.shared.gui_items.loot_box import BLACK_MARKET_ITEM_TYPE
from helpers import dependency
from items.utils import getItemDescrByCompactDescr
from skeletons.gui.game_control import IEventItemsController
from skeletons.gui.lobby_context import ILobbyContext

class BlackMarketVehicleList(ViewImpl):
    __slots__ = ('__prevRestoreCallback',)
    _COMMON_SOUND_SPACE = BLACK_MARKET_OVERLAY_SOUND_SPACE
    __itemsCtrl = dependency.descriptor(IEventItemsController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID, restoreCallback):
        settings = ViewSettings(layoutID)
        settings.model = BlackMarketVehicleListModel()
        super(BlackMarketVehicleList, self).__init__(settings)
        self.__prevRestoreCallback = restoreCallback

    def _onLoading(self, *args, **kwargs):
        super(BlackMarketVehicleList, self)._onLoading(*args, **kwargs)
        item = self.__itemsCtrl.getEventItemsByType(BLACK_MARKET_ITEM_TYPE)
        bonusVehicles = item.getBonusVehicles()
        obtainableVehicles = getObtainableVehicles(item)
        bonusVehicles = sorted(bonusVehicles, key=lambda vehCD: (vehCD in obtainableVehicles, getItemDescrByCompactDescr(vehCD).level, vehCD), reverse=True)
        with self.viewModel.transaction() as vm:
            vm.setSlotsNumber(min((len(obtainableVehicles), item.getReRollCount())))
            vehicleModelsList = vm.getVehicleList()
            for vehicleCD in bonusVehicles:
                vehicleModel = VehicleModel()
                setVehicleDataToModel(vehicleCD, vehicleModel)
                vehicleModel.setIsFromStorage(vehicleCD not in obtainableVehicles)
                vehicleModelsList.addViewModel(vehicleModel)

    def _onLoaded(self, *args, **kwargs):
        super(BlackMarketVehicleList, self)._onLoading(*args, **kwargs)
        hideVehiclePreview(back=False)

    def _initialize(self, *args, **kwargs):
        super(BlackMarketVehicleList, self)._initialize(*args, **kwargs)
        self.viewModel.onVehiclePreview += self.__onVehiclePreview
        self.viewModel.onBackClick += self.__onBackClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _finalize(self):
        self.viewModel.onVehiclePreview -= self.__onVehiclePreview
        self.viewModel.onBackClick -= self.__onBackClick
        self.__prevRestoreCallback = None
        super(BlackMarketVehicleList, self)._finalize()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        return

    def __onBackClick(self):
        self.destroyWindow()

    def __onVehiclePreview(self, args):
        vehCD = int(args.get('vehicleId', 0))
        if vehCD in getObtainableVehicles(self.__itemsCtrl.getEventItemsByType(BLACK_MARKET_ITEM_TYPE)):
            showConfigurableVehiclePreview(vehTypeCompDescr=vehCD, previewAlias=VIEW_ALIAS.BLACK_MARKET_VEHICLE_LIST_SCREEN, hiddenBlocks=OptionalBlocks.ALL, customHangarAlias=CustomHangars.CUSTOMIZATION_HANGAR.value, previewBackCb=partial(self.__restoreCallback, self.__prevRestoreCallback))
            self.destroyWindow()

    @classmethod
    def __restoreCallback(cls, prevRestoreCallback):
        view = prevRestoreCallback()
        if view is not None:
            showBlackMarketVehicleListWindow(prevRestoreCallback, parent=view.getParentWindow())
        return

    def __onServerSettingsChange(self, diff):
        if Configs.LOOT_BOXES_CONFIG.value in diff:
            if self.__itemsCtrl.getOwnedItemsByType(BLACK_MARKET_ITEM_TYPE) is None:
                self.destroyWindow()
        return

    @property
    def viewModel(self):
        return super(BlackMarketVehicleList, self).getViewModel()


class BlackMarketVehicleListWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, contentResId, restoreCallback, parent=None):
        super(BlackMarketVehicleListWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BlackMarketVehicleList(contentResId, restoreCallback), parent=parent, layer=WindowLayer.OVERLAY)

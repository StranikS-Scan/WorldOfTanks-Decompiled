# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/carousel_view.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_view_model import HangarCarouselViewModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items.Vehicle import getIconResourceName
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.carousel_tank_model import CarouselTankModel
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
from white_tiger.gui.white_tiger_account_settings import getWTFavorites
from white_tiger.gui.impl.lobby.tooltips.carousel_vehicle_tooltip_view import CarouselVehicleTooltipView
from white_tiger.gui.impl.lobby.tooltips.ticket_tooltip_view import TicketTooltipView
from gui.impl.gui_decorators import args2params
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from skeletons.gui.game_control import IPlatoonController

class CarouselView(ViewComponent[HangarCarouselViewModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __whiteTigerCtrl = dependency.descriptor(IWhiteTigerController)
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, layoutID=R.aliases.white_tiger.shared.Carousel(), **kwargs):
        super(CarouselView, self).__init__(layoutID=layoutID, model=HangarCarouselViewModel)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.white_tiger.mono.lobby.tooltips.ticket_tooltip():
            return TicketTooltipView()
        return CarouselVehicleTooltipView(vehInvID=event.getArgument('id')) if contentID == R.views.white_tiger.mono.lobby.tooltips.carousel_vehicle_tooltip() else super(CarouselView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(CarouselView, self).getViewModel()

    @sf_lobby
    def __app(self):
        return None

    def _getVehicles(self):
        return [ self.__itemsCache.items.getItemByCD(intCD) for intCD in self.__whiteTigerCtrl.getWTVehicles() ]

    def _onLoading(self, *args, **kwargs):
        super(CarouselView, self)._onLoading()
        self.__fillVehicles()

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onCurrentVehicleChanged),
         (self.viewModel.onClick, self.__onCarouselClick),
         (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.__whiteTigerCtrl.onEventPrbChanged, self.__onPrbEntitySwitched))

    def _getCallbacks(self):
        return (('cache.vehsLock', self.__onVehicleLockUpdated), ('tokens', self.__onTokensUpdate))

    def _unsubscribe(self):
        super(CarouselView, self)._unsubscribe()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onVehicleLockUpdated(self, *args):
        self.__fillVehicles()

    def __fillVehicles(self):
        isPlatoon = self.__platoonCtrl.isInPlatoon()
        with self.viewModel.transaction() as vm:
            vehicles = self._getVehicles()
            tanks = vm.getTanks()
            tanks.clear()
            tanks.reserve(len(vehicles))
            favourite = getWTFavorites()
            for vehicle in vehicles:
                if WT_VEHICLE_TAGS.PRIORITY_BOSS in vehicle.tags and not self.__itemsCache.items.getVehicle(vehicle.invID):
                    continue
                iconName = getIconResourceName(vehicle.name)
                if WT_VEHICLE_TAGS.BOSS in vehicle.tags:
                    if WT_VEHICLE_TAGS.PRIORITY_BOSS not in vehicle.tags:
                        if not self.__economicsCtrl.hasEnoughTickets():
                            iconName += '_alt'
                    tank = CarouselTankModel()
                    tank.setId(vehicle.invID)
                    tank.setInBattle(vehicle.isInBattle)
                    tank.setInPlatoon(vehicle.isInUnit)
                    tank.setTitle(vehicle.userName)
                    tank.setIcon(R.images.white_tiger.gui.maps.icons.carousel.vehicles.big.dyn(iconName)())
                    tank.setIconSmall(R.images.white_tiger.gui.maps.icons.carousel.vehicles.small.dyn(iconName)())
                    tank.setQuantity(self.__economicsCtrl.getTicketCount())
                    tank.setSelected(favourite == vehicle.invID)
                    WT_VEHICLE_TAGS.BOSS in vehicle.tags and tank.setIsSpecial(WT_VEHICLE_TAGS.PRIORITY_BOSS in vehicle.tags)
                    tank.setIsHunter(False)
                    tank.setUnsuitable(vehicle.isInUnit or isPlatoon)
                else:
                    tank.setIsSpecial(False)
                    tank.setIsHunter(True)
                    tank.setUnsuitable(False)
                tanks.addViewModel(tank)

            tanks.invalidate()

    def __onCurrentVehicleChanged(self):
        self.__fillVehicles()

    @args2params(int)
    def __onCarouselClick(self, id):
        vehicle = self.__itemsCache.items.getVehicle(id)
        self.__whiteTigerCtrl.selectVehicle(vehicle.invID)

    def __onTokensUpdate(self, diff):
        if self.__whiteTigerCtrl.isEventPrbActive() and ('wtevent:' in key for key in diff.keys()):
            self.__fillVehicles()

    def __onSyncCompleted(self, reason, diff):
        if self.__whiteTigerCtrl.isEventPrbActive() and reason is CACHE_SYNC_REASON.CLIENT_UPDATE and diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
            self.__fillVehicles()
        return

    def __onPrbEntitySwitched(self, _):
        self.__fillVehicles()

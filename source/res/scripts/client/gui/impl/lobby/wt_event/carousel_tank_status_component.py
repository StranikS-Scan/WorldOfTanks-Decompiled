# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/carousel_tank_status_component.py
import typing
from CurrentVehicle import g_currentVehicle
from gui.server_events.events_constants import WT_GROUP_PREFIX
from gui.server_events.events_dispatcher import showMissionsCategories
from gui.shop import showLootBoxBuyWindow
from helpers import dependency
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.wt_event.carousel_tank_status_model import CarouselTankStatusModel
    from gui.impl.lobby.wt_event.wt_event_carousel_view import EventVehicleCDs

class CarouselTankStatusComponent(object):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    eventController = dependency.descriptor(IGameEventController)
    __slots__ = ('__viewModel', '__vehCDs', '__selectedVehicleCD')

    def __init__(self, vehCDs, selectedVehicleCD=None):
        self.__viewModel = None
        self.__vehCDs = vehCDs
        self.__selectedVehicleCD = selectedVehicleCD
        return

    def init(self, viewModel):
        self.__viewModel = viewModel

    def destroy(self):
        self.__viewModel = None
        return

    def addListeners(self):
        self.__viewModel.onBuyTicket += self.__onBuyTicket
        self.__viewModel.onOpenTasks += self.__onOpenTasks

    def removeListeners(self):
        self.__viewModel.onBuyTicket -= self.__onBuyTicket
        self.__viewModel.onOpenTasks -= self.__onOpenTasks

    def update(self, selectedVehCD=None):
        if selectedVehCD is None and g_currentVehicle.item is not None:
            selectedVehCD = g_currentVehicle.item.intCD
        self.__setSelectedVehicle(selectedVehCD)
        self.__update()
        return

    def __setSelectedVehicle(self, selectedVehicleCD):
        if selectedVehicleCD == self.__selectedVehicleCD:
            return
        self.__viewModel.setIsHunter(selectedVehicleCD == self.__vehCDs.hunterIntCD)
        self.__viewModel.setIsSpecial(selectedVehicleCD == self.__vehCDs.eliteBossIntCD)
        self.__viewModel.setQuantity(0)
        self.__selectedVehicleCD = selectedVehicleCD

    def __update(self):
        if self.__selectedVehicleCD == self.__vehCDs.bossIntCD:
            tokensCount = self.eventController.getWtEventTokensCount()
            self.__viewModel.setQuantity(tokensCount)

    def __onBuyTicket(self):
        showLootBoxBuyWindow()

    def __onOpenTasks(self):
        showMissionsCategories(groupID=WT_GROUP_PREFIX)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/postbattle/event.py
import logging
import typing
from constants import WT_TAGS
from gui.impl.gen import R
from white_tiger.gui.impl.lobby.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_event_stamp_tooltip_view import WtEventStampTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher
from gui.shared.utils.requesters import REQ_CRITERIA
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import TICKET_UI_NAME
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared import IItemsCache
from skeletons.prebattle_vehicle import IPrebattleVehicle
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewEvent
    from gui.impl.lobby.postbattle.postbattle_screen_view import PostbattleScreenView
_logger = logging.getLogger(__name__)

class PostbattleScreenEventPlugin(IGlobalListener):
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self, proxy):
        super(PostbattleScreenEventPlugin, self).__init__()
        self.__proxy = proxy

    def getContentTooltipCreator(self):
        return {R.views.white_tiger.lobby.tooltips.LootBoxTooltipView(): self.__getWtEventLootBoxTooltip,
         R.views.white_tiger.lobby.tooltips.TicketTooltipView(): self.__getWtEventTicketTooltip,
         R.views.white_tiger.lobby.tooltips.StampTooltipView(): self.__getWtEventStampTooltip}

    def addListeners(self):
        self.startGlobalListening()
        self.__proxy.viewModel.onWidgetClick += self.__onWidgetClick
        self.__gameEventCtrl.onUpdated += self.__update

    def removeListeners(self):
        self.stopGlobalListening()
        self.__proxy.viewModel.onWidgetClick -= self.__onWidgetClick
        self.__gameEventCtrl.onUpdated -= self.__update

    def finalize(self):
        self.__proxy = None
        return

    def onPrbEntitySwitched(self):
        if not self.__gameEventCtrl.isEventPrbActive():
            if self.__proxy:
                self.__proxy.destroyWindow()

    def __onWidgetClick(self, args):
        typeName = args.get('type')
        if typeName is None:
            raise SoftException('Invalid arguments to extract widget type')
        if not self.__gameEventCtrl.isModeActive():
            _logger.warning("Can't go to event views because event isn't available now.")
            return
        else:
            if typeName == self.__gameEventCtrl.getConfig().stamp:
                event_dispatcher.showEventProgressionWindow()
            elif typeName == TICKET_UI_NAME:
                self.__gotoBossInHangar()
            elif typeName == WhiteTigerLootBoxes.WT_HUNTER or typeName == WhiteTigerLootBoxes.WT_BOSS:
                event_dispatcher.showEventStorageWindow()
            self.__gameEventCtrl.doSelectEventPrb()
            return

    def __getWtEventLootBoxTooltip(self, event):
        return WtEventLootBoxTooltipView(isHunterLootBox=event.getArgument('isHunterLootBox'))

    def __getWtEventTicketTooltip(self, _):
        return WtEventTicketTooltipView()

    def __getWtEventStampTooltip(self, _):
        return WtEventStampTooltipView()

    def __gotoBossInHangar(self):
        vehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({WT_TAGS.BOSS}) | REQ_CRITERIA.VEHICLE.HAS_NO_TAG({WT_TAGS.PRIORITY_BOSS}))
        if not vehicles:
            raise SoftException("Can't get boss vehicles")
        vehicle = vehicles.values()[0]
        self.__prebattleVehicle.select(vehicle)
        event_dispatcher.showHangar()
        self.__proxy.destroyWindow()

    def __update(self):
        if not self.__gameEventCtrl.isAvailable():
            self.__proxy.destroyWindow()

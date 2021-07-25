# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/context_menu/recruit_card_context_menu.py
from gui import SystemMessages
from gui.impl.gen import R
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.shared import event_dispatcher
from gui.shared.gui_items.processors.tankman import TankmanUnload
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.detachment import IDetachmentCache
from shared_utils import CONST_CONTAINER
from ids_generators import SequenceIDGenerator
from gui.shared.utils import decorators

class MenuItems(CONST_CONTAINER):
    MOBILIZE = 'mobilize'
    UNLOAD = 'unload'
    GO_TO_HANGAR_VEHICLE = 'goToHangarVehicle'


class MenuHandlers(CONST_CONTAINER):
    MOBILIZE = '_mobilize'
    UNLOAD = '_unload'
    GO_TO_HANGAR_VEHICLE = '_goToHangarVehicle'


class RecruitCardContextMenu(AbstractContextMenuHandler):
    __sqGen = SequenceIDGenerator()
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    _gui = dependency.descriptor(IGuiLoader)
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, cmProxy, ctx=None):
        super(RecruitCardContextMenu, self).__init__(cmProxy, ctx, {MenuItems.MOBILIZE: MenuHandlers.MOBILIZE,
         MenuItems.UNLOAD: MenuHandlers.UNLOAD,
         MenuItems.GO_TO_HANGAR_VEHICLE: MenuHandlers.GO_TO_HANGAR_VEHICLE})

    def _initFlashValues(self, ctx):
        self._recruit = self._itemsCache.items.getTankman(int(ctx.tmanInvId))

    def _generateOptions(self, ctx=None):
        options = []
        recruit = self._recruit
        vehicle = self._itemsCache.items.getVehicle(recruit.vehicleInvID)
        convertionEnabled = self._lobbyContext.getServerSettings().isDetachmentManualConversionEnabled()
        options.append(self._makeItem(MenuItems.MOBILIZE, backport.text(R.strings.menu.contextMenu.convert()), {'enabled': convertionEnabled and not recruit.isDismissed}))
        isInTank = vehicle is not None
        options.append(self._makeItem(MenuItems.UNLOAD, backport.text(R.strings.menu.contextMenu.tankmanUnload()), {'enabled': isInTank and not vehicle.isCrewLocked}))
        options.append(self._makeItem(MenuItems.GO_TO_HANGAR_VEHICLE, backport.text(R.strings.menu.contextMenu.selectVehicleInHangar()), {'enabled': isInTank}))
        return options

    def _mobilize(self):
        event_dispatcher.showDetachmentMobilizationView(False, NavigationViewSettings(NavigationViewModel.MOBILIZATION, previousViewSettings=NavigationViewSettings(NavigationViewModel.BARRACK_RECRUIT)), installRecruit=self._recruit)

    @decorators.process('unloading')
    def _unload(self):
        recruit = self._recruit
        vehicle = self._itemsCache.items.getVehicle(recruit.vehicleInvID)
        result = yield TankmanUnload(vehicle, recruit.vehicleSlotIdx).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def _goToHangarVehicle(self):
        vehicle = self._itemsCache.items.getVehicle(self._recruit.vehicleInvID)
        event_dispatcher.selectVehicleInHangar(vehicle.intCD)

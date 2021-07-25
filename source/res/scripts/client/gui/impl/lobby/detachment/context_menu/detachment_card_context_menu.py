# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/context_menu/detachment_card_context_menu.py
from async import async, await
from crew2.detachment_states import CanAssignResult
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import getVehicleLockStatusForDetachment
from gui.impl.dialogs.dialogs import showDetachmentDemobilizeDialogView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from helpers import dependency
from items.components.detachment_constants import DemobilizeReason
from shared_utils import CONST_CONTAINER
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger

class MenuItems(CONST_CONTAINER):
    PERSONAL_CASE = 'personalCase'
    RAISE_PERFORMANCE = 'raisePerformance'
    UNLOAD = 'tankmanUnload'
    DISMISS = 'dismiss'
    SELECT_VEHICLE_IN_HANGAR = 'selectVehicleInHangar'
    PERKS_MATRIX = 'perksMatrix'


class MenuHandlers(CONST_CONTAINER):
    PERSONAL_CASE = '_showPersonalCase'
    RAISE_PERFORMANCE = '_raisePerformance'
    UNLOAD = '_unloadDetachment'
    DISMISS = '_dismissDetachment'
    SELECT_VEHICLE_IN_HANGAR = '_selectVehicleInHangar'
    PERKS_MATRIX = '_showPerksMatrix'


class DetachmentCardContextMenu(AbstractContextMenuHandler):
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    uiLogger = DetachmentLogger(GROUP.HANGAR_DETACHMENT_WIDGET_CONTEXT_MENU)

    def __init__(self, cmProxy, ctx=None):
        super(DetachmentCardContextMenu, self).__init__(cmProxy, ctx, {MenuItems.PERSONAL_CASE: MenuHandlers.PERSONAL_CASE,
         MenuItems.RAISE_PERFORMANCE: MenuHandlers.RAISE_PERFORMANCE,
         MenuItems.UNLOAD: MenuHandlers.UNLOAD,
         MenuItems.DISMISS: MenuHandlers.DISMISS,
         MenuItems.SELECT_VEHICLE_IN_HANGAR: MenuHandlers.SELECT_VEHICLE_IN_HANGAR,
         MenuItems.PERKS_MATRIX: MenuHandlers.PERKS_MATRIX})

    def _initFlashValues(self, ctx):
        self._detachment = self.__detachmentCache.getDetachment(ctx.detInvId)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.DETACHMENT_PERSONAL_CASE)
    def _showPersonalCase(self):
        event_dispatcher.showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': self._detachment.invID}, NavigationViewSettings(NavigationViewModel.BARRACK_DETACHMENT))

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.RAISE_EFFICIENCY)
    def _raisePerformance(self):
        event_dispatcher.showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_PROGRESSION, {'detInvID': self._detachment.invID}, NavigationViewSettings(NavigationViewModel.BARRACK_DETACHMENT))

    def _unloadDetachment(self):
        self.uiLogger.log(ACTION.DETACHMENT_MOVE_TO_BARRACKS)
        ActionsFactory.doAction(ActionsFactory.RESET_DETACHMENT_VEHICLE_LINK, self._detachment.invID)

    def _selectVehicleInHangar(self):
        vehicle = self.__itemsCache.items.getVehicle(self._detachment.vehInvID)
        event_dispatcher.selectVehicleInHangar(vehicle.intCD)

    def _showPerksMatrix(self):
        event_dispatcher.showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_PERKS_MATRIX, {'detInvID': self._detachment.invID}, NavigationViewSettings(NavigationViewModel.BARRACK_DETACHMENT))

    @async
    def _dismissDetachment(self):
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.DEMOBILIZE_DETACHMENT_DIALOG)
        sdr = yield await(showDetachmentDemobilizeDialogView(self._detachment.invID, DemobilizeReason.DISMISS))
        if sdr.busy:
            return
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            ActionsFactory.doAction(ActionsFactory.DEMOBILIZED_DETACHMENT, data['detInvID'], data['allowRemove'], data['freeExcludeInstructors'])

    def _makeLabel(self, menuId):
        return backport.text(R.strings.menu.contextMenu.dyn(menuId)())

    def _generateOptions(self, ctx=None):
        vehicle = self.__itemsCache.items.getVehicle(self._detachment.vehInvID)
        hasTagCrewLocked = vehicle.isCrewLocked if vehicle else False
        canAssingRes, _ = getVehicleLockStatusForDetachment(self._detachment, vehicle, checkLockCrew=False)
        canProcessStrict = canAssingRes == CanAssignResult.OK
        dismissEnabled = self.__lobbyContext.getServerSettings().isDissolveDetachmentEnabled()
        dismissLimitReached = self._detachment.isSellsDailyLimitReached()
        return [self._makeItem(MenuItems.PERSONAL_CASE, self._makeLabel(MenuItems.PERSONAL_CASE), {'enabled': canProcessStrict}),
         self._makeItem(MenuItems.PERKS_MATRIX, self._makeLabel(MenuItems.PERKS_MATRIX), {'enabled': canProcessStrict}),
         self._makeItem(MenuItems.RAISE_PERFORMANCE, self._makeLabel(MenuItems.RAISE_PERFORMANCE), {'enabled': canProcessStrict}),
         self._makeItem(MenuItems.UNLOAD, self._makeLabel(MenuItems.UNLOAD), {'enabled': canProcessStrict and not hasTagCrewLocked and vehicle is not None}),
         self._makeItem(MenuItems.DISMISS, self._makeLabel(MenuItems.DISMISS), {'enabled': canProcessStrict and dismissEnabled and not dismissLimitReached and not hasTagCrewLocked}),
         self._makeItem(MenuItems.SELECT_VEHICLE_IN_HANGAR, self._makeLabel(MenuItems.SELECT_VEHICLE_IN_HANGAR), {'enabled': vehicle is not None})]

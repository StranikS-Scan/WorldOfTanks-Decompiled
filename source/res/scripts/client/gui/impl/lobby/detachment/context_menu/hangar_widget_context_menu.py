# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/context_menu/hangar_widget_context_menu.py
from typing import TYPE_CHECKING, Optional
from CurrentVehicle import g_currentVehicle
from async import async, await
from crew2.detachment_states import CanAssignResult
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import getVehicleLockStatusForDetachment, isDetachmentInRecycleBin, getBestDetachmentForVehicle, getRecruitsForMobilization, canAssignDetachmentToVehicle
from gui.impl.dialogs.dialogs import showDetachmentDemobilizeDialogView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from helpers import dependency
from items.components.detachment_constants import DemobilizeReason, NO_DETACHMENT_ID, TypeDetachmentAssignToVehicle
from shared_utils import CONST_CONTAINER
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
if TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment

class MenuItems(CONST_CONTAINER):
    PERSONAL_CASE = 'personalCase'
    SET_BEST_DETACHMENT = 'setBestCrew'
    RETURN_DETACHMENT = 'returnCrew'
    RAISE_PERFORMANCE = 'raisePerformance'
    UNLOAD = 'tankmanUnload'
    DISMISS = 'dismiss'
    CONVERT_RECRUITS = 'convertRecruits'
    SELECT_DETACHMENT = 'selectDetachment'
    RECRUIT_NEW = 'recruitNew'


class MenuHandlers(CONST_CONTAINER):
    PERSONAL_CASE = '_showPersonalCase'
    SET_BEST_DETACHMENT = '_setBestDetachment'
    RETURN_DETACHMENT = '_returnPrevDetachment'
    RAISE_PERFORMANCE = '_raisePerformance'
    UNLOAD = '_unloadDetachment'
    DISMISS = '_dismissDetachment'
    CONVERT_RECRUITS = '_convertRecruits'
    SELECT_DETACHMENT = '_selectDetachment'
    RECRUIT_NEW = '_recruitNew'


_ITEM_MAX_RECRUITS = 99
_MAX_RECRUITS_FORMATTER = '{}+'

class HangarWidgetContextMenu(AbstractContextMenuHandler):
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    uiLogger = DetachmentLogger(GROUP.HANGAR_DETACHMENT_WIDGET_CONTEXT_MENU)

    def __init__(self, cmProxy, ctx=None):
        super(HangarWidgetContextMenu, self).__init__(cmProxy, ctx, {MenuItems.PERSONAL_CASE: MenuHandlers.PERSONAL_CASE,
         MenuItems.SET_BEST_DETACHMENT: MenuHandlers.SET_BEST_DETACHMENT,
         MenuItems.RETURN_DETACHMENT: MenuHandlers.RETURN_DETACHMENT,
         MenuItems.RAISE_PERFORMANCE: MenuHandlers.RAISE_PERFORMANCE,
         MenuItems.UNLOAD: MenuHandlers.UNLOAD,
         MenuItems.DISMISS: MenuHandlers.DISMISS,
         MenuItems.CONVERT_RECRUITS: MenuHandlers.CONVERT_RECRUITS,
         MenuItems.SELECT_DETACHMENT: MenuHandlers.SELECT_DETACHMENT,
         MenuItems.RECRUIT_NEW: MenuHandlers.RECRUIT_NEW})

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.DETACHMENT_PERSONAL_CASE)
    def _showPersonalCase(self):
        detInvID = g_currentVehicle.getLinkedDetachmentID()
        event_dispatcher.showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': detInvID})

    @uiLogger.dLog(ACTION.SET_BEST_DETACHMENT)
    def _setBestDetachment(self):
        bestDetachment = getBestDetachmentForVehicle(g_currentVehicle.item)
        ActionsFactory.doAction(ActionsFactory.ASSIGN_DETACHMENT, bestDetachment.invID, g_currentVehicle.item.invID, TypeDetachmentAssignToVehicle.IS_BEST)

    @uiLogger.dLog(ACTION.SET_PREVIOUS_DETACHMENT)
    def _returnPrevDetachment(self):
        ActionsFactory.doAction(ActionsFactory.ASSIGN_DETACHMENT, g_currentVehicle.item.lastDetachmentID, g_currentVehicle.item.invID, TypeDetachmentAssignToVehicle.IS_LAST)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.RAISE_EFFICIENCY)
    def _raisePerformance(self):
        detInvID = g_currentVehicle.getLinkedDetachmentID()
        event_dispatcher.showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_PROGRESSION, {'detInvID': detInvID})

    def _unloadDetachment(self):
        detInvID = g_currentVehicle.getLinkedDetachmentID()
        if detInvID:
            self.uiLogger.log(ACTION.DETACHMENT_MOVE_TO_BARRACKS)
            ActionsFactory.doAction(ActionsFactory.RESET_DETACHMENT_VEHICLE_LINK, detInvID)

    @async
    def _dismissDetachment(self):
        detInvID = g_currentVehicle.getLinkedDetachmentID()
        if detInvID != NO_DETACHMENT_ID:
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.DEMOBILIZE_DETACHMENT_DIALOG)
            sdr = yield await(showDetachmentDemobilizeDialogView(detInvID, DemobilizeReason.DISMISS))
            if sdr.busy:
                return
            isOk, data = sdr.result
            if isOk == DialogButtons.SUBMIT:
                ActionsFactory.doAction(ActionsFactory.DEMOBILIZED_DETACHMENT, data['detInvID'], data['allowRemove'], data['freeExcludeInstructors'])

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.MOBILIZE_CREW)
    def _convertRecruits(self):
        event_dispatcher.showDetachmentMobilizationView(True)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.ASSIGN_DETACHMENT)
    def _selectDetachment(self):
        event_dispatcher.showAssignDetachmentToVehicleView(g_currentVehicle.invID)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.NEW_COMMANDER_LIST)
    def _recruitNew(self):
        from gui.shared.event_dispatcher import showNewCommanderWindow
        showNewCommanderWindow(g_currentVehicle.invID)

    def _makeLabel(self, menuId, param=None):
        return backport.text(R.strings.menu.contextMenu.dyn(menuId)(), recruits=param) if menuId == MenuItems.CONVERT_RECRUITS else backport.text(R.strings.menu.contextMenu.dyn(menuId)())

    def _generateOptions(self, ctx=None):
        currentDetachment = self._getCurrentDetachment()
        hasDetachment = currentDetachment is not None
        options = []
        canProcessStrict = True
        hasTagCrewLocked = g_currentVehicle.isCrewLocked()
        if hasDetachment:
            canAssingRes, _ = getVehicleLockStatusForDetachment(currentDetachment, g_currentVehicle.item, checkLockCrew=False)
            canProcessStrict = canAssingRes == CanAssignResult.OK
            options.append(self._makeItem(MenuItems.PERSONAL_CASE, self._makeLabel(MenuItems.PERSONAL_CASE), {'enabled': canProcessStrict,
             'disabledTextColor': 13347959,
             'textAlpha': 1 if canProcessStrict else 0.5}))
        options.append(self._makeItem(MenuItems.SELECT_DETACHMENT, self._makeLabel(MenuItems.SELECT_DETACHMENT), {'enabled': canProcessStrict and not hasTagCrewLocked}))
        options.append(self._makeItem(MenuItems.SET_BEST_DETACHMENT, self._makeLabel(MenuItems.SET_BEST_DETACHMENT), {'enabled': canProcessStrict and self.__isBestDetachmentOptionAvailable()}))
        options.append(self._makeItem(MenuItems.RETURN_DETACHMENT, self._makeLabel(MenuItems.RETURN_DETACHMENT), {'enabled': self.__isPrevDetachmentOptionAvailable()}))
        if hasDetachment:
            dismissEnabled = self.__lobbyContext.getServerSettings().isDissolveDetachmentEnabled()
            dismissLimitReached = currentDetachment.isSellsDailyLimitReached()
            options.append(self._makeItem(MenuItems.RAISE_PERFORMANCE, self._makeLabel(MenuItems.RAISE_PERFORMANCE), {'enabled': not g_currentVehicle.isLocked()}))
            options.append(self._makeItem(MenuItems.UNLOAD, self._makeLabel(MenuItems.UNLOAD), {'enabled': canProcessStrict and not hasTagCrewLocked}))
            options.append(self._makeItem(MenuItems.DISMISS, self._makeLabel(MenuItems.DISMISS), {'enabled': canProcessStrict and dismissEnabled and not dismissLimitReached and not hasTagCrewLocked}))
        else:
            options.append(self._makeItem(MenuItems.RECRUIT_NEW, self._makeLabel(MenuItems.RECRUIT_NEW)))
        recruitsCount = len(getRecruitsForMobilization(g_currentVehicle.item))
        if recruitsCount:
            enabled = self.__lobbyContext.getServerSettings().isDetachmentManualConversionEnabled()
            recruitsItemValue = _MAX_RECRUITS_FORMATTER.format(_ITEM_MAX_RECRUITS) if recruitsCount > _ITEM_MAX_RECRUITS else recruitsCount
            options.append(self._makeItem(MenuItems.CONVERT_RECRUITS, self._makeLabel(MenuItems.CONVERT_RECRUITS, recruitsItemValue), {'enabled': enabled}))
        return options

    def _getCurrentDetachment(self):
        detInvID = g_currentVehicle.getLinkedDetachmentID()
        return self.__detachmentCache.getDetachment(detInvID)

    def __isPrevDetachmentOptionAvailable(self):
        if g_currentVehicle.isLocked() or g_currentVehicle.isCrewLocked():
            return False
        else:
            lastCrewIDs = g_currentVehicle.item.lastCrew
            if lastCrewIDs is not None and not all((recruit is None for recruit in lastCrewIDs)):
                return False
            currentVehicle = g_currentVehicle.item
            lastDetachmentID = currentVehicle.lastDetachmentID
            if lastDetachmentID is None or lastDetachmentID == currentVehicle.getLinkedDetachmentID():
                return False
            lastDetachment = self.__detachmentCache.getDetachment(lastDetachmentID)
            if lastDetachment is None or isDetachmentInRecycleBin(lastDetachment):
                return False
            if not canAssignDetachmentToVehicle(lastDetachment, currentVehicle) == CanAssignResult.OK:
                return False
            vehicle = self.__itemsCache.items.getVehicle(lastDetachment.vehInvID)
            return False if vehicle is not None and (vehicle.isLocked or vehicle.isCrewLocked) else True

    def __isBestDetachmentOptionAvailable(self):
        if g_currentVehicle.isLocked() or g_currentVehicle.isCrewLocked():
            return False
        else:
            bestDetachment = getBestDetachmentForVehicle(g_currentVehicle.item)
            currentDetInvID = g_currentVehicle.getLinkedDetachmentID()
            if bestDetachment is None or bestDetachment.invID == currentDetInvID:
                return False
            currentDetachment = self.__detachmentCache.getDetachment(currentDetInvID)
            return bestDetachment.experience > currentDetachment.experience if currentDetachment is not None else True

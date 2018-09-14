# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortContextMenuHandler.py
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.managers.context_menu.AbstractContextMenuHandler import AbstractContextMenuHandler
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES

class FortContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity, FortViewHelper):

    def __init__(self, cmProxy, ctx = None):
        super(FortContextMenuHandler, self).__init__(cmProxy, ctx, {FORTIFICATION_ALIASES.CTX_ACTION_DIRECTION_CONTROL: 'fortDirection',
         FORTIFICATION_ALIASES.CTX_ACTION_PREPARE_ORDER: 'fortPrepareOrder',
         FORTIFICATION_ALIASES.CTX_ACTION_ASSIGN_PLAYERS: 'fortAssignPlayers',
         FORTIFICATION_ALIASES.CTX_ACTION_MODERNIZATION: 'fortModernization',
         FORTIFICATION_ALIASES.CTX_ACTION_DESTROY: 'fortDestroy'})

    def fortDirection(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)

    def fortAssignPlayers(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, ctx={'data': self.buildingID}), scope=EVENT_BUS_SCOPE.LOBBY)

    def fortModernization(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, ctx={'data': self.buildingID}), scope=EVENT_BUS_SCOPE.LOBBY)

    def fortDestroy(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, ctx={'data': self.buildingID}), scope=EVENT_BUS_SCOPE.LOBBY)

    def fortPrepareOrder(self):
        currentOrderID = self.fortCtrl.getFort().getBuildingOrder(FortViewHelper.getBuildingIDbyUID(self.buildingID))
        from gui import DialogsInterface
        DialogsInterface.showDialog(BuyOrderDialogMeta(FortViewHelper.getOrderUIDbyID(currentOrderID)), None)
        return

    def _initFlashValues(self, ctx):
        self.buildingID = ctx.uid

    def _clearFlashValues(self):
        self.buildingID = None
        return

    def _generateOptions(self, ctx = None):
        result = []
        buildingDescr = self.fortCtrl.getFort().getBuilding(FortViewHelper.getBuildingIDbyUID(self.buildingID))
        if buildingDescr is not None and self.fortCtrl.getPermissions().canViewContext():
            canModernization = self._canModernization(buildingDescr)
            enableModernizationBtn = self._isEnableModernizationBtnByProgress(buildingDescr) and self._isEnableModernizationBtnByDamaged(buildingDescr)
            if self._isMilitaryBase(buildingDescr.typeID):
                if self._isVisibleDirectionCtrlBtn(buildingDescr):
                    result.append(self._makeItem(FORTIFICATION_ALIASES.CTX_ACTION_DIRECTION_CONTROL, MENU.FORTIFICATIONCTX_DIRECTIONCONTROL, {'enabled': self._isEnableDirectionControl()}))
            elif self._isVisibleActionBtn(buildingDescr):
                result.append(self._makeItem(FORTIFICATION_ALIASES.CTX_ACTION_PREPARE_ORDER, MENU.FORTIFICATIONCTX_PREPAREORDER, {'enabled': self._isEnableActionBtn(buildingDescr)}))
            result.append(self._makeItem(FORTIFICATION_ALIASES.CTX_ACTION_ASSIGN_PLAYERS, MENU.FORTIFICATIONCTX_ASSIGNEDPLAYERS))
            if canModernization:
                result.append(self._makeItem(FORTIFICATION_ALIASES.CTX_ACTION_MODERNIZATION, MENU.FORTIFICATIONCTX_MODERNIZATION, {'enabled': enableModernizationBtn}))
            if not self._isMilitaryBase(buildingDescr.typeID) and self._isVisibleDemountBtn(buildingDescr):
                result.append(self._makeItem(FORTIFICATION_ALIASES.CTX_ACTION_DESTROY, MENU.FORTIFICATIONCTX_DESTROY, {'enabled': self._isEnableDemountBtn(buildingDescr)}))
        return result

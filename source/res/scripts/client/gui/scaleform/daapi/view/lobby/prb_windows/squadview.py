# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadView.py
from account_helpers.AccountSettings import AccountSettings, FALLOUT
from gui.Scaleform.daapi.view.lobby.prb_windows.SquadActionButtonStateVO import SquadActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.framework.managers.TextManager import TextManager
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.context import unit_ctx
from gui.Scaleform.daapi.view.meta.SquadViewMeta import SquadViewMeta
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE, FUNCTIONAL_EXIT
from gui.server_events import g_eventsCache
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.ItemsCache import g_itemsCache
from helpers import i18n
from shared_utils import findFirst
from gui.prb_control import settings
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getEventVehiclesNamesStr

class SquadView(SquadViewMeta):

    def __init__(self):
        super(SquadView, self).__init__()
        self.__isFallout = None
        return

    def inviteFriendRequest(self):
        if self.__canSendInvite():
            self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ctx={'prbName': 'squad',
             'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)

    def toggleReadyStateRequest(self):
        self.unitFunctional.togglePlayerReadyAction(True)

    def onUnitVehicleChanged(self, dbID, vInfo):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo(dbID=dbID)
        if g_eventsCache.isEventEnabled() and pInfo.isCreator():
            self.__isFallout = None
            if not vInfo.isEmpty():
                vehicle = g_itemsCache.items.getItemByCD(vInfo.vehTypeCD)
                self.__isFallout = vehicle.isEvent
            self._updateRallyData()
            self._setActionButtonState()
            return
        else:
            if pInfo.isInSlot:
                slotIdx = pInfo.slotIdx
                if not vInfo.isEmpty():
                    vehicleVO = makeVehicleVO(g_itemsCache.items.getItemByCD(vInfo.vehTypeCD), functional.getRosterSettings().getLevelsRange(), isFallout=self.__isFallout, isCreator=pInfo.isCreator(), isCurrentPlayer=pInfo.isCurrentPlayer())
                    slotCost = vInfo.vehLevel
                else:
                    slotState = functional.getSlotState(slotIdx)
                    vehicleVO = None
                    if slotState.isClosed:
                        slotCost = settings.UNIT_CLOSED_SLOT_COST
                    else:
                        slotCost = 0
                self.as_setMemberVehicleS(slotIdx, slotCost, vehicleVO)
            return

    def chooseVehicleRequest(self):
        pass

    def leaveSquad(self):
        self.prbDispatcher.doLeaveAction(unit_ctx.LeaveUnitCtx(waitingID='prebattle/leave', funcExit=FUNCTIONAL_EXIT.NO_FUNC))

    def onUnitPlayerAdded(self, pInfo):
        super(SquadView, self).onUnitPlayerAdded(pInfo)
        self._setActionButtonState()

    def onUnitPlayerRemoved(self, pInfo):
        super(SquadView, self).onUnitPlayerRemoved(pInfo)
        self._setActionButtonState()

    def onUnitPlayerStateChanged(self, pInfo):
        self._updateRallyData()
        self._setActionButtonState()

    def onUnitFlagsChanged(self, flags, timeLeft):
        super(SquadView, self).onUnitFlagsChanged(flags, timeLeft)
        self._setActionButtonState()
        if flags.isInQueue():
            self._closeSendInvitesWindow()

    def onUnitRosterChanged(self):
        super(SquadView, self).onUnitRosterChanged()
        self._setActionButtonState()
        if not self.__canSendInvite():
            self._closeSendInvitesWindow()

    def onUnitMembersListChanged(self):
        super(SquadView, self).onUnitMembersListChanged()
        self.__updateFalloutState()
        self._updateRallyData()
        self._setActionButtonState()

    def _populate(self):
        self.__updateFalloutState()
        super(SquadView, self)._populate()
        g_eventsCache.onSyncCompleted += self.__onEventsUpdated
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        g_eventsCache.onSyncCompleted -= self.__onEventsUpdated
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SquadView, self)._dispose()

    def _setActionButtonState(self):
        functional = self.unitFunctional
        enabled = not (functional.getFlags().isInQueue() and functional.getPlayerInfo().isReady) and self.__canSendInvite()
        if enabled:
            enabled = False
            for slot in functional.getSlotsIterator(*functional.getUnit(unitIdx=functional.getUnitIdx())):
                if not slot.player:
                    enabled = True
                    break

        self.as_updateInviteBtnStateS(enabled)
        self.as_setActionButtonStateS(self.__getActionButtonStateVO())

    def _updateMembersData(self):
        functional = self.unitFunctional
        self.as_setMembersS(*vo_converters.makeSlotsVOs(functional, functional.getUnitIdx(), app=self.app, isFallout=self.__isFallout))
        self._setActionButtonState()

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeUnitVO(functional, unitIdx=functional.getUnitIdx(), app=self.app, isFallout=self.__isFallout)
        self.as_updateRallyS(data)
        falloutFilter = AccountSettings.getFilter(FALLOUT)
        wasShown = falloutFilter['wasShown']
        isNew = False
        isEventEnabled = g_eventsCache.isEventEnabled()
        if isEventEnabled:
            battleTypeName = i18n.makeString(MENU.HEADERBUTTONS_BATTLE_MENU_STANDART) + '\n' + i18n.makeString(MENU.HEADERBUTTONS_BATTLE_MENU_DOMINATION)
            tooltipStr = makeTooltip(body=TOOLTIPS.SQUADWINDOW_EVENT_DOMINATION, note=getEventVehiclesNamesStr())
            isNew = not wasShown
        else:
            battleTypeName = i18n.makeString(MENU.HEADERBUTTONS_BATTLE_MENU_STANDART)
            tooltipStr = ''
        self.as_updateBattleTypeInfoS(tooltipStr, isEventEnabled)
        self.as_updateBattleTypeS(battleTypeName, isEventEnabled, isNew)
        if isNew:
            falloutFilter['wasShown'] = True
            AccountSettings.setFilter(FALLOUT, falloutFilter)

    def __getActionButtonStateVO(self):
        unitFunctional = self.unitFunctional
        return SquadActionButtonStateVO(unitFunctional)

    def __canSendInvite(self):
        return self.unitFunctional.getPermissions().canSendInvite()

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)

    def __updateFalloutState(self):
        if g_eventsCache.isEventEnabled():
            slots = self.unitFunctional.getSlotsIterator(*self.unitFunctional.getUnit())
            creator = findFirst(lambda s: s.player is not None and s.player.isCreator, slots)
            self.__isFallout = None
            if creator is not None and creator.vehicle is not None:
                creatorVehicle = g_itemsCache.items.getItemByCD(creator.vehicle['vehTypeCompDescr'])
                self.__isFallout = creatorVehicle.isEvent
        return

    def __onEventsUpdated(self):
        self.__updateFalloutState()
        self._updateRallyData()

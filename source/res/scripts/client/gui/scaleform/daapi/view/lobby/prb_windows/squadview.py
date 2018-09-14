# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadView.py
from gui.Scaleform.daapi.view.lobby.prb_windows.SquadActionButtonStateVO import SquadActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import g_eventsCache
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.prb_control.context import unit_ctx
from gui.Scaleform.daapi.view.meta.SquadViewMeta import SquadViewMeta
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE, FUNCTIONAL_FLAG
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters.ranges import toRomanRangeString
from helpers import i18n, int2roman
from gui.prb_control import settings

class SquadView(SquadViewMeta):

    def __init__(self):
        super(SquadView, self).__init__()
        self.__isFallout = False
        self.__falloutType = 0
        self.__falloutCfg = None
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
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if not vInfo.isEmpty():
                vehicleVO = makeVehicleVO(g_itemsCache.items.getItemByCD(vInfo.vehTypeCD), functional.getRosterSettings().getLevelsRange(), isCurrentPlayer=pInfo.isCurrentPlayer())
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
        self.prbDispatcher.doLeaveAction(unit_ctx.LeaveUnitCtx(waitingID='prebattle/leave', flags=FUNCTIONAL_FLAG.UNDEFINED))

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
        self._updateRallyData()
        self._setActionButtonState()

    def onUnitExtraChanged(self, extra):
        super(SquadView, self).onUnitExtraChanged(extra)
        self.__updateFalloutState()
        self._updateRallyData()
        self._setActionButtonState()
        self.__updateHeader()

    def onUnitRejoin(self):
        self.__updateFalloutState()
        super(SquadView, self).onUnitRejoin()
        self.__updateHeader()

    def getCoolDownRequests(self):
        requests = super(SquadView, self).getCoolDownRequests()
        requests.append(REQUEST_TYPE.SET_ES_PLAYER_STATE)
        return requests

    def _populate(self):
        self.__updateFalloutState()
        self.as_isFalloutS(self.__isFallout)
        super(SquadView, self)._populate()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__updateHeader()

    def _dispose(self):
        self.__falloutCfg = None
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SquadView, self)._dispose()
        return

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
        self.as_setMembersS(*vo_converters.makeSlotsVOs(functional, functional.getUnitIdx(), app=self.app))
        self._setActionButtonState()

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeUnitVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        self.as_updateRallyS(data)
        if self.__isFallout:
            battleTypeName = text_styles.standard('#menu:headerButtons/battle/menu/fallout') + '\n' + i18n.makeString('#menu:headerButtons/battle/menu/fallout/%d' % self.__falloutType)
        else:
            battleTypeName = text_styles.main(MESSENGER.DIALOGS_SQUADCHANNEL_BATTLETYPE) + '\n' + i18n.makeString(MENU.HEADERBUTTONS_BATTLE_MENU_STANDART)
        self.as_updateBattleTypeInfoS('', False)
        self.as_updateBattleTypeS(battleTypeName, self.__isFallout, False)

    def __getActionButtonStateVO(self):
        unitFunctional = self.unitFunctional
        return SquadActionButtonStateVO(unitFunctional)

    def __canSendInvite(self):
        return self.unitFunctional.getPermissions().canSendInvite()

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)

    def __updateFalloutState(self):
        self.__falloutType = self.unitFunctional.getExtra().eventType
        self.__isFallout = self.__falloutType > 0
        self.__falloutCfg = g_eventsCache.getFalloutConfig(self.__falloutType)

    def __updateHeader(self):
        if self.__isFallout:
            allowedLevelsList = list(self.__falloutCfg.allowedLevels)
            allowedLevelsStr = toRomanRangeString(allowedLevelsList, 1)
            vehicleLbl = i18n.makeString(CYBERSPORT.WINDOW_UNIT_TEAMVEHICLESLBL, levelsRange=text_styles.main(allowedLevelsStr))
            tooltipData = {}
            if len(allowedLevelsList) > 1:
                tooltipData = self.__dominationVehicleInfoTooltip(self.__falloutCfg.vehicleLevelRequired, allowedLevelsStr)
            self.as_setVehiclesTitleS(vehicleLbl, tooltipData)

    def __dominationVehicleInfoTooltip(self, requiredLevel, allowedLevelsStr):
        return {'id': TOOLTIPS.SQUADWINDOW_DOMINATION_VEHICLESINFOICON,
         'header': {},
         'body': {'level': int2roman(requiredLevel),
                  'allowedLevels': allowedLevelsStr}}

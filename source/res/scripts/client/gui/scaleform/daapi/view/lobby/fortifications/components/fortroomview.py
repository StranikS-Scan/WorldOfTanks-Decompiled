# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortRoomView.py
from UnitBase import UNIT_OP
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters, rally_dps
from gui.Scaleform.daapi.view.meta.FortRoomMeta import FortRoomMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.prb_control import settings
from gui.prb_control.items.sortie_items import getDivisionNameByType, getDivisionLevel
from gui.prb_control.prb_helpers import UnitListener
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared import events
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE

class FortRoomView(FortRoomMeta, UnitListener):

    def __init__(self):
        super(FortRoomView, self).__init__()

    def _populate(self):
        super(FortRoomView, self)._populate()
        minLevel, maxLvl = self._getDivisionLvls()
        self._updateVehiclesLabel(minLevel, maxLvl)

    def _dispose(self):
        super(FortRoomView, self)._dispose()

    def onUnitStateChanged(self, unitState, timeLeft):
        self._setActionButtonState()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.unitFunctional.getCensoredComment())
        elif opCode in [UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT]:
            self._setActionButtonState()

    def onUnitVehicleChanged(self, dbID, vInfo):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo(dbID=dbID)
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if not vInfo.isEmpty():
                vehicleVO = makeVehicleVO(g_itemsCache.items.getItemByCD(vInfo.vehTypeCD))
                slotCost = vInfo.vehLevel
            else:
                slotState = functional.getSlotState(slotIdx)
                vehicleVO = None
                if slotState.isClosed:
                    slotCost = settings.UNIT_CLOSED_SLOT_COST
                else:
                    slotCost = 0
            self.as_setMemberVehicleS(slotIdx, slotCost, vehicleVO)
        if pInfo.isCreator() or pInfo.isCurrentPlayer():
            self._setActionButtonState()
        return

    def onUnitMembersListChanged(self):
        functional = self.unitFunctional
        if self._candidatesDP:
            self._candidatesDP.rebuild(functional.getCandidates())
        self._updateMembersData()
        self._setActionButtonState()

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.SortieCandidatesDP()
        self._candidatesDP.init(self.as_getCandidatesDPS(), self.unitFunctional.getCandidates())

    def rebuildCandidatesDP(self):
        self._candidatesDP.rebuild(self.unitFunctional.getCandidates())

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeSortieVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        self.as_updateRallyS(data)

    def _getDivisionLvls(self):
        _, unit = self.unitFunctional.getUnit(self.unitFunctional.getUnitIdx())
        division = getDivisionNameByType(unit.getRosterTypeID())
        level = getDivisionLevel(division)
        minLevel = fort_formatters.getTextLevel(1)
        maxLevel = fort_formatters.getTextLevel(level)
        return (minLevel, maxLevel)

    def _getVehicleSelectorDescription(self):
        return FORTIFICATIONS.SORTIE_VEHICLESELECTOR_DESCRIPTION

    def inviteFriendRequest(self):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_SEND_INVITES_WINDOW, {'prbName': 'unit',
         'ctrlType': CTRL_ENTITY_TYPE.UNIT,
         'showClanOnly': True}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _setActionButtonState(self):
        self.as_setActionButtonStateS(vo_converters.makeSortieActionButtonVO(self.unitFunctional))

# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortBattlesRoomView.py
import BigWorld
from helpers import i18n
from UnitBase import UNIT_OP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import event_dispatcher
from gui.shared.formatters import icons, text_styles
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters, rally_dps
from gui.Scaleform.daapi.view.meta.FortRoomMeta import FortRoomMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.prb_control.prb_helpers import UnitListener
from gui.prb_control import settings
from gui.prb_control.items.sortie_items import getDivisionNameByType, getDivisionLevel
from gui.prb_control.items.sortie_items import getDivisionLevelByUnit
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared.ItemsCache import g_itemsCache
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE

class FortBattlesRoomView(FortRoomMeta, FortViewHelper, UnitListener):

    def __init__(self):
        super(FortBattlesRoomView, self).__init__()
        self._changeDivisionCooldown = None
        return

    def showChangeDivisionWindow(self):
        _, unit = self.unitFunctional.getUnit(self.unitFunctional.getUnitIdx())
        event_dispatcher.showChangeDivisionWindow(getDivisionLevelByUnit(unit))

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        self.__updateOrdersBg()

    def onConsumablesChanged(self, unitMgrID):
        self.__updateOrdersBg()

    def onUnitExtraChanged(self, extra):
        self.__updateOrdersBg()

    def onUnitPlayersListChanged(self):
        super(FortBattlesRoomView, self).onUnitPlayersListChanged()
        self.__updateLabels()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self._setActionButtonState()
        self._updateRallyData()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.unitFunctional.getCensoredComment())
        elif opCode in (UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT):
            self._setActionButtonState()
        elif opCode == UNIT_OP.CHANGE_DIVISION:
            functional = self.unitFunctional
            data = vo_converters.makeSortieVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
            self.as_updateRallyS(data)

    def onUnitVehicleChanged(self, dbID, vInfo):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo(dbID=dbID)
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if not vInfo.isEmpty():
                vehicleVO = makeVehicleVO(g_itemsCache.items.getItemByCD(vInfo.vehTypeCD), functional.getRosterSettings().getLevelsRange())
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

    def onUnitRejoin(self):
        super(FortBattlesRoomView, self).onUnitRejoin()
        functional = self.unitFunctional
        if self._candidatesDP:
            self._candidatesDP.rebuild(functional.getCandidates())
        self._updateMembersData()
        self.__updateLabels()

    def onSlotsHighlihgtingNeed(self, databaseID):
        functional = self.unitFunctional
        availableSlots = list(functional.getPlayerInfo(databaseID).getAvailableSlots(True))
        pInfo = functional.getPlayerInfo(dbID=databaseID)
        if not pInfo.isInSlot and pInfo.isLegionary():
            _, unit = functional.getUnit()
            if unit.getLegionaryCount() >= unit.getLegionaryMaxCount():
                legionariesSlots = unit.getLegionarySlots().values()
                self.as_highlightSlotsS(legionariesSlots)
                return legionariesSlots
        self.as_highlightSlotsS(availableSlots)
        return availableSlots

    def isPlayerLeginary(self, databaseID = None):
        pInfo = self.unitFunctional.getPlayerInfo(dbID=databaseID)
        return pInfo.isLegionary

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.SortieCandidatesLegionariesDP()
        self._candidatesDP.init(self.app, self.as_getCandidatesDPS(), self.unitFunctional.getCandidates())

    def rebuildCandidatesDP(self):
        self._candidatesDP.rebuild(self.unitFunctional.getCandidates())

    def _updateMembersData(self):
        functional = self.unitFunctional
        dataOne, slots = vo_converters.makeSlotsVOs(functional, functional.getUnitIdx(), app=self.app)
        self.__updateLabels()
        self.as_setMembersS(dataOne, slots)
        self._setActionButtonState()

    def _populate(self):
        super(FortBattlesRoomView, self)._populate()
        minLevel, maxLvl = self._getDivisionLvls()
        self._updateVehiclesLabel(minLevel, maxLvl)
        self.addListener(events.CoolDownEvent.PREBATTLE, self._handleChangedDivision, scope=EVENT_BUS_SCOPE.LOBBY)
        self._setChangeDivisionCooldown()

    def _dispose(self):
        super(FortBattlesRoomView, self)._dispose()
        self.removeListener(events.CoolDownEvent.PREBATTLE, self._handleChangedDivision, scope=EVENT_BUS_SCOPE.LOBBY)
        self._cancelChangeDivisionCooldown()

    def _changeDivisionCallback(self):
        self._cancelChangeDivisionCooldown()
        self.as_setChangeDivisionButtonEnabledS(True)

    def _setChangeDivisionCooldown(self):
        cooldown = self.unitFunctional.getCooldownTime(REQUEST_TYPE.CHANGE_DIVISION)
        if cooldown > 0:
            self.as_setChangeDivisionButtonEnabledS(False)
            self._changeDivisionCooldown = BigWorld.callback(cooldown, self._changeDivisionCallback)

    def _cancelChangeDivisionCooldown(self):
        if self._changeDivisionCooldown is not None:
            BigWorld.cancelCallback(self._changeDivisionCooldown)
            self._changeDivisionCooldown = None
        return

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeSortieVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        self.__updateLabels()
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

    def _handleChangedDivision(self, event):
        if event.requestID == REQUEST_TYPE.CHANGE_DIVISION:
            self.as_setChangeDivisionButtonEnabledS(False)
            self._setChangeDivisionCooldown()

    def _setActionButtonState(self):
        self.as_setActionButtonStateS(ActionButtonStateVO(self.unitFunctional))

    def __updateLabels(self):
        if not self.isPlayerInSlot() and self.isPlayerLeginary():
            self.as_showLegionariesToolTipS(True)
        else:
            self.as_showLegionariesToolTipS(False)
        _, unit = self.unitFunctional.getUnit()
        if unit and (unit.getLegionaryCount() or self._candidatesDP.legionariesCount > 0):
            self.as_showLegionariesCountS(True, self.__playersLabel(unit.getLegionaryCount(), unit.getLegionaryMaxCount()), i18n.makeString(TOOLTIPS.FORTIFICATION_SORTIE_BATTLEROOM_LEGIONARIESCOUNT_BODY, count=unit.getLegionaryMaxCount()))
        else:
            self.as_showLegionariesCountS(False, None, None)
        return

    def __playersLabel(self, playerCount, limit):
        if playerCount == 0:
            players = text_styles.standard(str(playerCount))
        else:
            players = text_styles.main(str(playerCount))
        resultCount = ''.join((players, text_styles.standard(' / {0} )'.format(limit))))
        legionariesIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_LEGIONNAIRE, 16, 16, -4, 0)
        leftBrace = text_styles.standard('( ')
        result = leftBrace + legionariesIcon + resultCount
        return result

    def __getSlots(self):
        functional = self.unitFunctional
        _, slots = vo_converters.makeSlotsVOs(functional, functional.getUnitIdx(), app=self.app)
        return slots

    def __updateOrdersBg(self):
        unitPermissions = self.unitFunctional.getPermissions()
        activeConsumes = self.unitFunctional.getExtra().getConsumables()
        self.as_showOrdersBgS(bool(not unitPermissions.canChangeConsumables() and len(activeConsumes)))

# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortRoomView.py
import BigWorld
from UnitBase import UNIT_OP
import account_helpers
from debug_utils import LOG_DEBUG
from fortified_regions import g_cache as g_fortCache
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text, fort_formatters
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters, rally_dps
from gui.Scaleform.daapi.view.meta.FortRoomMeta import FortRoomMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import UtilsManager, ImageUrlProperties
from gui.prb_control import settings
from gui.prb_control.items.sortie_items import getDivisionNameByType, getDivisionLevel
from gui.shared.ItemsCache import g_itemsCache
from helpers import i18n

class FortRoomView(FortRoomMeta):

    def __init__(self):
        super(FortRoomView, self).__init__()
        self.currentDBID = BigWorld.player().databaseID
        self.__isLegionaries = False
        pInfo = self.unitFunctional.getPlayerInfo(dbID=self.currentDBID)
        if pInfo.isLegionary():
            self.__isLegionaries = True

    def _populate(self):
        super(FortRoomView, self)._populate()
        minLevel, maxLvl = self._getDivisionLvls()
        self._updateVehiclesLabel(minLevel, maxLvl)

    def isInSlot(self):
        pInfo = self.unitFunctional.getPlayerInfo(dbID=self.currentDBID)
        return pInfo.isInSlot

    def _dispose(self):
        super(FortRoomView, self)._dispose()

    def onUnitPlayersListChanged(self):
        super(FortRoomView, self).onUnitPlayersListChanged()
        self.__updateLabels(self.__getSlots())

    def onUnitStateChanged(self, unitState, timeLeft):
        self._setActionButtonState()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.unitFunctional.getCensoredComment())
        elif opCode in (UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT):
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

    def _updateMembersData(self):
        functional = self.unitFunctional
        dataOne, slots = vo_converters.makeSlotsVOs(functional, functional.getUnitIdx(), app=self.app)
        self._updateData(slots)
        self.as_setMembersS(dataOne, slots)
        self._setActionButtonState()

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.SortieCandidatesLegionariesDP()
        self._candidatesDP.init(self.as_getCandidatesDPS(), self.unitFunctional.getCandidates())

    def rebuildCandidatesDP(self):
        self._candidatesDP.rebuild(self.unitFunctional.getCandidates())

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeSortieVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        self._updateData(data['slots'])
        self.as_updateRallyS(data)

    def _getDivisionLvls(self):
        _, unit = self.unitFunctional.getUnit(self.unitFunctional.getUnitIdx())
        division = getDivisionNameByType(unit.getRosterTypeID())
        level = getDivisionLevel(division)
        minLevel = fort_formatters.getTextLevel(1)
        maxLevel = fort_formatters.getTextLevel(level)
        return (minLevel, maxLevel)

    def _updateData(self, slots):
        self.__updateLabels(slots)
        if self.isInSlot():
            return
        if self.__isLegionaries:
            for value in slots:
                if value['canBeTaken']:
                    value['canBeTaken'] = False

    def _getVehicleSelectorDescription(self):
        return FORTIFICATIONS.SORTIE_VEHICLESELECTOR_DESCRIPTION

    def assignSlotRequest(self, slotIndex, playerId):
        if playerId == -1:
            if self.unitFunctional.getPlayerInfo().isCreator():
                LOG_DEBUG('Request to assign is ignored. Creator can not move to another slots')
                return
            playerId = account_helpers.getPlayerDatabaseID()
        elif not self.isPlayerInUnit(playerId):
            return
        self.requestToAssign(playerId, slotIndex)

    def onSlotsHighlihgtingNeed(self, databaseID):
        availableSlots = list(self.unitFunctional.getPlayerInfo(databaseID).getAvailableSlots(True))
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo(dbID=databaseID)
        data = vo_converters.makeSortieVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        if pInfo.isInSlot:
            self.as_highlightSlotsS(availableSlots)
            return availableSlots
        else:
            isLegionariesDrag = pInfo.isLegionary()
            slotIndexies = []
            if isLegionariesDrag:
                slots = data['slots']
                slotCount = 0
                for slot in slots:
                    player = slot['player']
                    if not player:
                        slotCount += 1
                        continue
                    isLeg = player['isLegionaries']
                    if isLeg and len(slotIndexies) <= g_fortCache.maxLegionariesCount:
                        slotIndexies.append(slotCount)
                    slotCount += 1

                if len(slotIndexies) < g_fortCache.maxLegionariesCount:
                    self.as_highlightSlotsS(availableSlots)
                    return availableSlots
                self.as_highlightSlotsS(slotIndexies)
                return slotIndexies
            self.as_highlightSlotsS(availableSlots)
            return availableSlots

    def _setActionButtonState(self):
        self.as_setActionButtonStateS(vo_converters.makeSortieActionButtonVO(self.unitFunctional))

    def __updateLabels(self, slots):
        countLegionariesInSlots = 0
        for val in slots:
            player = val['player']
            if player and player['isLegionaries']:
                countLegionariesInSlots += 1

        if not self.isInSlot() and self.__isLegionaries:
            self.as_showLegionariesToolTipS(True)
        else:
            self.as_showLegionariesToolTipS(False)
        if countLegionariesInSlots > 0 or self._candidatesDP.legionariesCount > 0:
            self.as_showLegionariesCountS(True, self.__playersLabel(countLegionariesInSlots, g_fortCache.maxLegionariesCount))
        else:
            self.as_showLegionariesCountS(False, None)
        return

    def __playersLabel(self, playerCount, limit):
        concat = ' / ' + str(limit)
        currentPlayerColor = fort_text.MAIN_TEXT
        if playerCount == 0:
            currentPlayerColor = fort_text.STANDARD_TEXT
        resultCount = fort_text.concatStyles(((currentPlayerColor, str(playerCount)), (fort_text.STANDARD_TEXT, concat)))
        units = UtilsManager()
        legionariesIcon = units.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_LEGIONNAIRE, 16, 16, -4, 0))
        legionariesMSG = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTBATTLEROOM_LEGIONARIESCOUNT))
        result = legionariesIcon + ' ' + legionariesMSG + ' ' + resultCount
        return result

    def __getSlots(self):
        functional = self.unitFunctional
        _, slots = vo_converters.makeSlotsVOs(functional, functional.getUnitIdx(), app=self.app)
        return slots

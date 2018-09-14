# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortBattlesRoomView.py
import BigWorld
from UnitBase import UNIT_OP
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters, rally_dps
from gui.Scaleform.daapi.view.meta.FortRoomMeta import FortRoomMeta
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.prb_control import settings
from gui.prb_control.items.sortie_items import getDivisionNameByType, getDivisionLevel
from gui.shared.ItemsCache import g_itemsCache
from helpers import i18n
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.prb_control.prb_helpers import UnitListener

class FortBattlesRoomView(FortRoomMeta, FortViewHelper, UnitListener):

    def __init__(self):
        super(FortBattlesRoomView, self).__init__()
        self.currentDBID = BigWorld.player().databaseID
        self.__isLegionaries = False
        pInfo = self.unitFunctional.getPlayerInfo(dbID=self.currentDBID)
        if pInfo.isLegionary():
            self.__isLegionaries = True

    def _populate(self):
        super(FortBattlesRoomView, self)._populate()
        minLevel, maxLvl = self._getDivisionLvls()
        self._updateVehiclesLabel(minLevel, maxLvl)

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        self.__updateOrdersBg()

    def onConsumablesChanged(self, unitMgrID):
        self.__updateOrdersBg()

    def onUnitExtraChanged(self, extra):
        self.__updateOrdersBg()

    def __updateOrdersBg(self):
        unitPermissions = self.unitFunctional.getPermissions()
        activeConsumes = self.unitFunctional.getExtra().getConsumables()
        self.as_showOrdersBgS(bool(not unitPermissions.canChangeConsumables() and len(activeConsumes)))

    def onUnitPlayersListChanged(self):
        super(FortBattlesRoomView, self).onUnitPlayersListChanged()
        self.__updateLabels(self.__getSlots())

    def onUnitStateChanged(self, unitState, timeLeft):
        self._setActionButtonState()
        self._updateRallyData()

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
        self.__updateLabels(self.__getSlots())

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
        if self.isPlayerInSlot():
            return
        if self.__isLegionaries:
            for value in slots:
                if value['canBeTaken']:
                    value['canBeTaken'] = False

    def _getVehicleSelectorDescription(self):
        return FORTIFICATIONS.SORTIE_VEHICLESELECTOR_DESCRIPTION

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

    def _setActionButtonState(self):
        self.as_setActionButtonStateS(ActionButtonStateVO(self.unitFunctional))

    def __updateLabels(self, slots):
        if not self.isPlayerInSlot() and self.__isLegionaries:
            self.as_showLegionariesToolTipS(True)
        else:
            self.as_showLegionariesToolTipS(False)
        _, unit = self.unitFunctional.getUnit()
        if unit.getLegionaryCount() or self._candidatesDP.legionariesCount > 0:
            self.as_showLegionariesCountS(True, self.__playersLabel(unit.getLegionaryCount(), unit.getLegionaryMaxCount()))
        else:
            self.as_showLegionariesCountS(False, None)
        return

    def __playersLabel(self, playerCount, limit):
        concat = ' / ' + str(limit)
        currentPlayerColor = TextType.MAIN_TEXT
        if playerCount == 0:
            currentPlayerColor = TextType.STANDARD_TEXT
        resultCount = self.app.utilsManager.textManager.concatStyles(((currentPlayerColor, str(playerCount)), (TextType.STANDARD_TEXT, concat)))
        units = self.app.utilsManager
        legionariesIcon = units.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_LEGIONNAIRE, 16, 16, -4, 0))
        legionariesMSG = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTBATTLEROOM_LEGIONARIESCOUNT))
        result = legionariesIcon + ' ' + legionariesMSG + ' ' + resultCount
        return result

    def __getSlots(self):
        functional = self.unitFunctional
        _, slots = vo_converters.makeSlotsVOs(functional, functional.getUnitIdx(), app=self.app)
        return slots

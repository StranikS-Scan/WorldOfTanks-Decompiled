# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportUnitView.py
from UnitBase import UNIT_OP
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters, rally_dps
from gui.Scaleform.daapi.view.meta.CyberSportUnitMeta import CyberSportUnitMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.prb_control import settings
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache
from gui.shared.formatters import text_styles
from helpers import int2roman, i18n

class CyberSportUnitView(CyberSportUnitMeta):

    def getCoolDownRequests(self):
        requests = super(CyberSportUnitView, self).getCoolDownRequests()
        requests.append(REQUEST_TYPE.CLOSE_SLOT)
        return requests

    def onUnitFlagsChanged(self, flags, timeLeft):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo()
        rosterSettings = functional.getRosterSettings()
        isCreator = pInfo.isCreator()
        if flags.isLockedStateChanged():
            vehGetter = pInfo.getVehiclesToSlot
            slotGetter = functional.getSlotState
            slotLabels = map(lambda idx: vo_converters.makeSlotLabel(flags, slotGetter(idx), isCreator, len(vehGetter(idx))), rosterSettings.getAllSlotsRange())
            self.as_lockUnitS(flags.isLocked(), slotLabels)
        if isCreator and flags.isOpenedStateChanged():
            self.as_setOpenedS(flags.isOpened(), vo_converters.makeUnitStateLabel(flags))
        self._setActionButtonState()
        if flags.isChanged():
            self._updateMembersData()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.unitFunctional.getCensoredComment())
        elif opCode in [UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT]:
            functional = self.unitFunctional
            unitFlags = functional.getFlags()
            slotState = functional.getSlotState(value)
            pInfo = functional.getPlayerInfo()
            canAssign, vehicles = pInfo.canAssignToSlot(value)
            vehCount = len(vehicles)
            slotLabel = vo_converters.makeSlotLabel(unitFlags, slotState, pInfo.isCreator(), vehCount)
            if opCode == UNIT_OP.CLOSE_SLOT:
                self.as_closeSlotS(value, settings.UNIT_CLOSED_SLOT_COST, slotLabel)
            else:
                self.as_openSlotS(value, canAssign, slotLabel, vehCount)
            unitStats = functional.getStats()
            canDoAction, restriction = functional.validateLevels(stats=unitStats)
            self.as_setTotalLabelS(canDoAction, vo_converters.makeTotalLevelLabel(unitStats, restriction), unitStats.curTotalLevel)
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
            unitStats = functional.getStats()
            canDoAction, restriction = functional.validateLevels(stats=unitStats)
            self.as_setTotalLabelS(canDoAction, vo_converters.makeTotalLevelLabel(unitStats, restriction), unitStats.curTotalLevel)
        if pInfo.isCurrentPlayer() or functional.getPlayerInfo().isCreator():
            self._setActionButtonState()
        return

    def onUnitMembersListChanged(self):
        functional = self.unitFunctional
        if self._candidatesDP:
            self._candidatesDP.rebuild(functional.getCandidates())
        self._updateMembersData()
        self._setActionButtonState()
        unitStats = functional.getStats()
        canDoAction, restriction = functional.validateLevels(stats=unitStats)
        self.as_setTotalLabelS(canDoAction, vo_converters.makeTotalLevelLabel(unitStats, restriction), unitStats.curTotalLevel)
        self._updateLabels(functional)

    def onUnitRejoin(self):
        super(CyberSportUnitView, self).onUnitRejoin()
        functional = self.unitFunctional
        if self._candidatesDP:
            self._candidatesDP.rebuild(functional.getCandidates())
        self._updateMembersData()
        unitStats = functional.getStats()
        canDoAction, restriction = functional.validateLevels(stats=unitStats)
        self.as_setTotalLabelS(canDoAction, vo_converters.makeTotalLevelLabel(unitStats, restriction), unitStats.curTotalLevel)
        self._updateLabels(functional)

    def toggleFreezeRequest(self):
        self.requestToLock(not self.unitFunctional.getFlags().isLocked())

    def toggleStatusRequest(self):
        self.requestToOpen(not self.unitFunctional.getFlags().isOpened())

    def showSettingsRoster(self, slots):
        container = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY})
        if window is not None:
            window.updateSlots(slots)
        else:
            levelsRange = self.unitFunctional.getRosterSettings().getLevelsRange()
            self.fireEvent(events.LoadViewEvent(CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY, ctx={'settings': slots,
             'section': 'cs_unit_view_settings',
             'levelsRange': levelsRange}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def cancelRosterSlotsSettings(self):
        self._destroyRelatedView(ViewTypes.TOP_WINDOW, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY)

    def resultRosterSlotsSettings(self, value):
        self.requestToUpdateRoster(value)
        self._destroyRelatedView(ViewTypes.TOP_WINDOW, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY)

    def lockSlotRequest(self, slotIndex):
        self.requestToCloseSlot(slotIndex)

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeUnitVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        self.as_updateRallyS(data)
        self._updateLabels(functional)

    def _updateLabels(self, functional):
        _, unit = functional.getUnit()
        if unit is None:
            return
        else:
            slotsBusy = len(unit.getMembers())
            slotsBusy = text_styles.main(str(slotsBusy))
            maxSlots = unit.getMaxSlotCount()
            teamLbl = i18n.makeString(CYBERSPORT.WINDOW_UNIT_TEAMMEMBERS, current=slotsBusy, max=str(maxSlots))
            teamLbl = text_styles.standard(teamLbl)
            self.as_setPlayerCountLblS(teamLbl)
            return

    def _setActionButtonState(self):
        self.as_setActionButtonStateS(ActionButtonStateVO(self.unitFunctional))

    def _getVehicleSelectorDescription(self):
        return CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_UNIT

    def _populate(self):
        super(CyberSportUnitView, self)._populate()
        self.addListener(events.CSRosterSlotSettingsWindow.APPLY_SLOT_SETTINGS, self.__applyRosterSettings)
        settings = self.unitFunctional.getRosterSettings()
        self._updateVehiclesLabel(int2roman(settings.getMinLevel()), int2roman(settings.getMaxLevel()))

    def _dispose(self):
        self._destroyRelatedView(ViewTypes.TOP_WINDOW, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY)
        self.removeListener(events.CSRosterSlotSettingsWindow.APPLY_SLOT_SETTINGS, self.__applyRosterSettings)
        super(CyberSportUnitView, self)._dispose()

    def __applyRosterSettings(self, event):
        self.as_updateSlotSettingsS(event.ctx)

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.CandidatesDataProvider()
        self._candidatesDP.init(self.app, self.as_getCandidatesDPS(), self.unitFunctional.getCandidates())

    def rebuildCandidatesDP(self):
        self._candidatesDP.rebuild(self.unitFunctional.getCandidates())

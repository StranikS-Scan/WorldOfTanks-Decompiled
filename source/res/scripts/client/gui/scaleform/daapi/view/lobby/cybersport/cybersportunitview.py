# Python bytecode 2.7 (decompiled from Python 2.7)
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
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from helpers import int2roman, i18n

class CyberSportUnitView(CyberSportUnitMeta):

    def getCoolDownRequests(self):
        requests = super(CyberSportUnitView, self).getCoolDownRequests()
        requests.append(REQUEST_TYPE.CLOSE_SLOT)
        return requests

    def onUnitFlagsChanged(self, flags, timeLeft):
        entity = self.prbEntity
        pInfo = entity.getPlayerInfo()
        rosterSettings = entity.getRosterSettings()
        isCreator = pInfo.isCommander()
        if flags.isLockedStateChanged():
            vehGetter = pInfo.getVehiclesToSlot
            slotGetter = entity.getSlotState
            slotLabels = map(lambda idx: vo_converters.makeSlotLabel(flags, slotGetter(idx), isCreator, len(vehGetter(idx))), rosterSettings.getAllSlotsRange())
            self.as_lockUnitS(flags.isLocked(), slotLabels)
            self._updateRallyData()
        if isCreator and flags.isOpenedStateChanged():
            self.as_setOpenedS(flags.isOpened(), vo_converters.makeUnitStateLabel(flags))
        self._setActionButtonState()
        if flags.isChanged():
            self._updateMembersData()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.prbEntity.getCensoredComment())
        elif opCode in [UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT]:
            entity = self.prbEntity
            unitFlags = entity.getFlags()
            slotState = entity.getSlotState(value)
            pInfo = entity.getPlayerInfo()
            canAssign, vehicles = pInfo.canAssignToSlot(value)
            vehCount = len(vehicles)
            slotLabel = vo_converters.makeSlotLabel(unitFlags, slotState, pInfo.isCommander(), vehCount)
            if opCode == UNIT_OP.CLOSE_SLOT:
                self.as_closeSlotS(value, settings.UNIT_CLOSED_SLOT_COST, slotLabel)
            else:
                self.as_openSlotS(value, canAssign, slotLabel, vehCount)
            unitStats = entity.getStats()
            result = entity.validateLevels()
            self.as_setTotalLabelS(result.isValid, vo_converters.makeTotalLevelLabel(unitStats, result.restriction), unitStats.curTotalLevel)
            self._setActionButtonState()

    def onUnitVehiclesChanged(self, dbID, vInfos):
        entity = self.prbEntity
        pInfo = entity.getPlayerInfo(dbID=dbID)
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if vInfos and not vInfos[0].isEmpty():
                vInfo = vInfos[0]
                vehicleVO = makeVehicleVO(self.itemsCache.items.getItemByCD(vInfo.vehTypeCD), entity.getRosterSettings().getLevelsRange())
                slotCost = vInfo.vehLevel
            else:
                slotState = entity.getSlotState(slotIdx)
                vehicleVO = None
                if slotState.isClosed:
                    slotCost = settings.UNIT_CLOSED_SLOT_COST
                else:
                    slotCost = 0
            self.as_setMemberVehicleS(slotIdx, slotCost, vehicleVO)
            unitStats = entity.getStats()
            result = entity.validateLevels()
            self.as_setTotalLabelS(result.isValid, vo_converters.makeTotalLevelLabel(unitStats, result.restriction), unitStats.curTotalLevel)
        self._setActionButtonState()
        return

    def onUnitMembersListChanged(self):
        entity = self.prbEntity
        if self._candidatesDP:
            self._candidatesDP.rebuild(entity.getCandidates())
        self._updateMembersData()
        self._setActionButtonState()
        unitStats = entity.getStats()
        result = entity.validateLevels()
        self.as_setTotalLabelS(result.isValid, vo_converters.makeTotalLevelLabel(unitStats, result.restriction), unitStats.curTotalLevel)
        self._updateLabels(entity)

    def onUnitRejoin(self):
        super(CyberSportUnitView, self).onUnitRejoin()
        entity = self.prbEntity
        if self._candidatesDP:
            self._candidatesDP.rebuild(entity.getCandidates())
        self._updateMembersData()
        unitStats = entity.getStats()
        result = entity.validateLevels()
        self.as_setTotalLabelS(result.isValid, vo_converters.makeTotalLevelLabel(unitStats, result.restriction), unitStats.curTotalLevel)
        self._updateLabels(entity)

    def toggleFreezeRequest(self):
        self.requestToLock(not self.prbEntity.getFlags().isLocked())

    def toggleStatusRequest(self):
        self.requestToOpen(not self.prbEntity.getFlags().isOpened())

    def showSettingsRoster(self, slots):
        container = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY})
        if window is not None:
            window.updateSlots(slots)
        else:
            levelsRange = self.prbEntity.getRosterSettings().getLevelsRange()
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
        entity = self.prbEntity
        data = vo_converters.makeUnitVO(entity, unitMgrID=entity.getID(), app=self.app)
        self.as_updateRallyS(data)
        self._updateLabels(entity)

    def _updateLabels(self, entity):
        _, unit = entity.getUnit()
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
        self.as_setActionButtonStateS(ActionButtonStateVO(self.prbEntity))

    def _getVehicleSelectorDescription(self):
        return CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_UNIT

    def _populate(self):
        super(CyberSportUnitView, self)._populate()
        self.addListener(events.CSRosterSlotSettingsWindow.APPLY_SLOT_SETTINGS, self.__applyRosterSettings)
        settings = self.prbEntity.getRosterSettings()
        self._updateVehiclesLabel(int2roman(settings.getMinLevel()), int2roman(settings.getMaxLevel()))

    def _dispose(self):
        self._destroyRelatedView(ViewTypes.TOP_WINDOW, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY)
        self.removeListener(events.CSRosterSlotSettingsWindow.APPLY_SLOT_SETTINGS, self.__applyRosterSettings)
        super(CyberSportUnitView, self)._dispose()

    def __applyRosterSettings(self, event):
        self.as_updateSlotSettingsS(event.ctx)

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.CandidatesDataProvider()
        self._candidatesDP.init(self.app, self.as_getCandidatesDPS(), self.prbEntity.getCandidates())

    def rebuildCandidatesDP(self):
        self._candidatesDP.rebuild(self.prbEntity.getCandidates())

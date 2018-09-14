# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/StaticFormationUnitView.py
import BigWorld
from UnitBase import UNIT_OP
from gui import makeHtmlString
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters, rally_dps
from gui.Scaleform.daapi.view.meta.StaticFormationUnitMeta import StaticFormationUnitMeta
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clubs import events_dispatcher as club_events
from gui.clubs.club_helpers import ClubListener
from gui.clubs.settings import getLadderChevron64x64, getLadderBackground
from gui.prb_control import settings
from gui.prb_control.context import unit_ctx
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared import g_itemsCache
from gui.shared.view_helpers.emblems import ClubEmblemsHelper
from gui.game_control.battle_availability import isHourInForbiddenList
from helpers import int2roman

class StaticFormationUnitView(StaticFormationUnitMeta, ClubListener, ClubEmblemsHelper):
    ABSENT_VALUES = '--'

    def __init__(self):
        super(StaticFormationUnitView, self).__init__()
        self.__extra = self.unitFunctional.getExtra()
        self.__clubDBID = self.__extra.clubDBID

    def getCoolDownRequests(self):
        requests = super(StaticFormationUnitView, self).getCoolDownRequests()
        requests.extend((REQUEST_TYPE.CLOSE_SLOT, REQUEST_TYPE.CHANGE_RATED))
        return requests

    def onClubEmblem64x64Received(self, clubDbID, emblem):
        if emblem:
            self.as_setTeamIconS(self.getMemoryTexturePath(emblem))

    def onClubMembersChanged(self, members):
        self.__updateHeader()
        self._updateMembersData()

    def onClubUpdated(self, club):
        self.__updateHeader()

    def onAccountClubStateChanged(self, state):
        self.__updateHeader()

    def onAccountClubRestrictionsChanged(self):
        self.__updateHeader()

    def onClubNameChanged(self, name):
        self.__updateHeader()

    def onClubLadderInfoChanged(self, ladderInfo):
        self.__updateHeader()

    def onClubsSeasonStateChanged(self, seasonState):
        self.__updateHeader()

    def onStatusChanged(self):
        self.__updateHeader()

    def __makeLegionnairesCountString(self, unit):
        legionnairesString = makeHtmlString('html_templates:lobby/cyberSport/staticFormationUnitView', 'legionnairesCount', {'cur': unit.getLegionaryCount(),
         'max': unit.getLegionaryMaxCount()})
        return legionnairesString

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        functional = self.unitFunctional
        _, unit = functional.getUnit()
        if self._candidatesDP is not None:
            self._candidatesDP.rebuild(functional.getCandidates())
        self.as_setLegionnairesCountS(False, self.__makeLegionnairesCountString(unit))
        self.__updateHeader()
        self._updateMembersData()
        self.__updateTotalData()
        return

    def onUnitFlagsChanged(self, flags, timeLeft):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo()
        isCreator = pInfo.isCreator()
        if isCreator and flags.isOpenedStateChanged():
            self.as_setOpenedS(flags.isOpened(), vo_converters.makeStaticFormationStatusLbl(flags))
        if flags.isChanged():
            self._updateMembersData()
        else:
            self._setActionButtonState()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.unitFunctional.getCensoredComment())
        elif opCode in [UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT]:
            functional = self.unitFunctional
            _, unit = functional.getUnit()
            unitFlags = functional.getFlags()
            slotState = functional.getSlotState(value)
            pInfo = functional.getPlayerInfo()
            canAssign, vehicles = pInfo.canAssignToSlot(value)
            canTakeSlot = not (pInfo.isLegionary() and unit.isClub())
            vehCount = len(vehicles)
            slotLabel = vo_converters.makeStaticSlotLabel(unitFlags, slotState, pInfo.isCreator(), vehCount, pInfo.isLegionary(), unit.isRated())
            if opCode == UNIT_OP.CLOSE_SLOT:
                self.as_closeSlotS(value, settings.UNIT_CLOSED_SLOT_COST, slotLabel)
            else:
                self.as_openSlotS(value, canAssign and canTakeSlot, slotLabel, vehCount)
            self.__updateTotalData()
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
            self.__updateTotalData()
        if pInfo.isCurrentPlayer() or functional.getPlayerInfo().isCreator():
            self._setActionButtonState()
        return

    def onUnitMembersListChanged(self):
        functional = self.unitFunctional
        _, unit = functional.getUnit()
        if self._candidatesDP is not None:
            self._candidatesDP.rebuild(functional.getCandidates())
        self.as_setLegionnairesCountS(False, self.__makeLegionnairesCountString(unit))
        self.__updateHeader()
        self._updateMembersData()
        self.__updateTotalData()
        return

    def onUnitExtraChanged(self, extra):
        self.__extra = self.unitFunctional.getExtra()
        self.__updateHeader()
        self._updateMembersData()
        self.__updateTotalData()

    def onUnitRejoin(self):
        super(StaticFormationUnitView, self).onUnitRejoin()
        functional = self.unitFunctional
        _, unit = functional.getUnit()
        if self._candidatesDP is not None:
            self._candidatesDP.rebuild(functional.getCandidates())
        self.as_setLegionnairesCountS(False, self.__makeLegionnairesCountString(unit))
        self.__updateHeader()
        self._updateMembersData()
        self.__updateTotalData()
        return

    def toggleStatusRequest(self):
        self.requestToOpen(not self.unitFunctional.getFlags().isOpened())

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.StaticFormationCandidatesDP()
        self._candidatesDP.init(self.app, self.as_getCandidatesDPS(), self.unitFunctional.getCandidates())

    def rebuildCandidatesDP(self):
        self._candidatesDP.rebuild(self.unitFunctional.getCandidates())

    def setRankedMode(self, isRated):
        self.sendRequest(unit_ctx.ChangeRatedUnitCtx(isRated, 'prebattle/change_settings'))

    def showTeamCard(self):
        club_events.showClubProfile(self.__clubDBID)

    def onSlotsHighlihgtingNeed(self, databaseID):
        functional = self.unitFunctional
        availableSlots = list(functional.getPlayerInfo(databaseID).getAvailableSlots(True))
        pInfo = functional.getPlayerInfo(dbID=databaseID)
        if not pInfo.isInSlot and pInfo.isLegionary():
            _, unit = functional.getUnit()
            if unit.isRated():
                self.as_highlightSlotsS([])
                return []
            if unit.getLegionaryCount() >= unit.getLegionaryMaxCount():
                legionariesSlots = unit.getLegionarySlots().values()
                self.as_highlightSlotsS(legionariesSlots)
                return legionariesSlots
        self.as_highlightSlotsS(availableSlots)
        return availableSlots

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeStaticFormationUnitVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        self.as_updateRallyS(data)

    def _setActionButtonState(self):
        self.as_setActionButtonStateS(ActionButtonStateVO(self.unitFunctional))

    def _getVehicleSelectorDescription(self):
        return CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_UNIT

    def _populate(self):
        super(StaticFormationUnitView, self)._populate()
        self.startClubListening(self.__clubDBID)
        settings = self.unitFunctional.getRosterSettings()
        self._updateVehiclesLabel(int2roman(settings.getMinLevel()), int2roman(settings.getMaxLevel()))
        self.__updateHeader()
        _, unit = self.unitFunctional.getUnit()
        self.as_setLegionnairesCountS(False, self.__makeLegionnairesCountString(unit))
        self._updateVehiclesLabel(int2roman(settings.getMinLevel()), int2roman(settings.getMaxLevel()))
        self.clubsCtrl.getAvailabilityCtrl().onStatusChanged += self.onStatusChanged

    def _dispose(self):
        self.ABSENT_VALUES = None
        self.__extra = None
        self.stopClubListening(self.__clubDBID)
        self.clubsCtrl.getAvailabilityCtrl().onStatusChanged -= self.onStatusChanged
        super(StaticFormationUnitView, self)._dispose()
        return

    def __updateHeader(self):
        club = self.clubsCtrl.getClub(self.__clubDBID)
        canSetRanked = club is not None and club.getPermissions().canSetRanked()
        seasonState = self.clubsCtrl.getSeasonState()
        modeLabel = ''
        modeTooltip = ''
        modeTooltipType = ''
        isFixedMode = True
        isModeTooltip = False
        if self.__extra.isRatedBattle:
            isFixedMode = not canSetRanked
            if canSetRanked:
                modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_SETUNRANKEDMODE
            else:
                modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_RANKEDMODE
        elif seasonState.isSuspended():
            modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_SEASONPAUSED
            isModeTooltip = True
            modeTooltipType = TOOLTIPS_CONSTANTS.COMPLEX
            modeTooltip = makeTooltip(CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_SEASONPAUSEDTOOLTIP_HEADER, CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_SEASONPAUSEDTOOLTIP_BODY)
        elif seasonState.isFinished():
            modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_SEASONFINISHED
            isModeTooltip = True
            modeTooltipType = TOOLTIPS_CONSTANTS.COMPLEX
            modeTooltip = makeTooltip(CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_SEASONFINISHEDTOOLTIP_HEADER, CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_SEASONFINISHEDTOOLTIP_BODY)
        elif canSetRanked:
            isFixedMode = False
            modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_SETRANKEDMODE
        if len(modeLabel):
            if canSetRanked and seasonState.isActive() or self.__extra.isRatedBattle:
                modeLabel = text_styles.neutral(modeLabel)
            else:
                modeLabel = text_styles.standard(modeLabel)
        if isHourInForbiddenList(self.clubsCtrl.getAvailabilityCtrl().getForbiddenHours()):
            modeLabel = '{0}{1}'.format(icons.alert(), text_styles.main(CYBERSPORT.LADDERREGULATIONS_WARNING))
            isFixedMode = True
            isModeTooltip = True
            modeTooltipType = TOOLTIPS_CONSTANTS.LADDER_REGULATIONS
        bgSource = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_LEAGUERIBBONS_UNRANKED
        battles = self.ABSENT_VALUES
        winRate = self.ABSENT_VALUES
        leagueIcon = getLadderChevron64x64()
        enableWinRateTF = False
        if club is not None:
            clubTotalStats = club.getTotalDossier().getTotalStats()
            battles = BigWorld.wg_getNiceNumberFormat(clubTotalStats.getBattlesCount())
            division = club.getLadderInfo().division
            leagueIcon = getLadderChevron64x64(division)
            winRateValue = ProfileUtils.getValueOrUnavailable(clubTotalStats.getWinsEfficiency())
            if winRateValue != ProfileUtils.UNAVAILABLE_VALUE:
                enableWinRateTF = True
                winRate = ProfileUtils.formatFloatPercent(winRateValue)
            else:
                winRate = self.ABSENT_VALUES
            if self.__extra.isRatedBattle:
                bgSource = getLadderBackground(division)
            self.requestClubEmblem64x64(club.getClubDbID(), club.getEmblem64x64())
        self.as_setHeaderDataS({'clubId': self.__extra.clubDBID,
         'teamName': self.__extra.clubName,
         'isRankedMode': bool(self.__extra.isRatedBattle),
         'battles': battles,
         'winRate': winRate,
         'enableWinRateTF': enableWinRateTF,
         'leagueIcon': leagueIcon,
         'isFixedMode': isFixedMode,
         'modeLabel': modeLabel,
         'modeTooltip': modeTooltip,
         'bgSource': bgSource,
         'modeTooltipType': modeTooltipType,
         'isModeTooltip': isModeTooltip})
        return

    def __updateTotalData(self):
        functional = self.unitFunctional
        unitStats = functional.getStats()
        canDoAction, restriction = functional.validateLevels(stats=unitStats)
        self.as_setTotalLabelS(canDoAction, vo_converters.makeTotalLevelLabel(unitStats, restriction), unitStats.curTotalLevel)

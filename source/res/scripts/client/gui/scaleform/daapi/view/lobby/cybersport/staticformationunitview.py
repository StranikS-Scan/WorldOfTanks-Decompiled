# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/StaticFormationUnitView.py
import BigWorld
from UnitBase import UNIT_OP
from gui.Scaleform.framework.managers.TextManager import TextType, TextManager
from helpers import int2roman
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters, rally_dps
from gui.Scaleform.daapi.view.meta.StaticFormationUnitMeta import StaticFormationUnitMeta
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clubs import events_dispatcher as club_events
from gui.clubs.club_helpers import isSeasonInProgress, ClubListener
from gui.clubs.settings import getLadderChevron64x64, getLadderBackground
from gui.prb_control import settings
from gui.prb_control.context import unit_ctx
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared import g_itemsCache
from gui.shared.view_helpers.emblems import ClubEmblemsHelper

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

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        functional = self.unitFunctional
        _, unit = functional.getUnit()
        if self._candidatesDP is not None:
            self._candidatesDP.rebuild(functional.getCandidates())
        self.as_setLegionnairesCountS(_ms(CYBERSPORT.STATICFORMATION_UNITVIEW_LEGIONNAIRESTOTAL, cur=unit.getLegionaryCount(), max=unit.getLegionaryMaxCount()))
        self.__updateHeader()
        self._updateMembersData()
        self.__updateTotalData()
        return

    def onUnitStateChanged(self, unitState, timeLeft):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo()
        isCreator = pInfo.isCreator()
        if isCreator and unitState.isOpenedStateChanged():
            self.as_setOpenedS(unitState.isOpened(), vo_converters.makeStaticFormationStatusLbl(unitState))
        if unitState.isChanged():
            self._updateMembersData()
        else:
            self._setActionButtonState()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.unitFunctional.getCensoredComment())
        elif opCode in [UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT]:
            functional = self.unitFunctional
            _, unit = functional.getUnit()
            unitState = functional.getState()
            slotState = functional.getSlotState(value)
            pInfo = functional.getPlayerInfo()
            canAssign, vehicles = pInfo.canAssignToSlot(value)
            canTakeSlot = not (pInfo.isLegionary() and unit.isClub())
            vehCount = len(vehicles)
            slotLabel = vo_converters.makeStaticSlotLabel(unitState, slotState, pInfo.isCreator(), vehCount, pInfo.isLegionary(), unit.isRated())
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
        self.as_setLegionnairesCountS(_ms(CYBERSPORT.STATICFORMATION_UNITVIEW_LEGIONNAIRESTOTAL, cur=unit.getLegionaryCount(), max=unit.getLegionaryMaxCount()))
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
        self.as_setLegionnairesCountS(_ms(CYBERSPORT.STATICFORMATION_UNITVIEW_LEGIONNAIRESTOTAL, cur=unit.getLegionaryCount(), max=unit.getLegionaryMaxCount()))
        self.__updateHeader()
        self._updateMembersData()
        self.__updateTotalData()
        return

    def toggleStatusRequest(self):
        self.requestToOpen(not self.unitFunctional.getState().isOpened())

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.StaticFormationCandidatesDP()
        self._candidatesDP.init(self.as_getCandidatesDPS(), self.unitFunctional.getCandidates())

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
        self.as_setLegionnairesCountS(_ms(CYBERSPORT.STATICFORMATION_UNITVIEW_LEGIONNAIRESTOTAL, cur=unit.getLegionaryCount(), max=unit.getLegionaryMaxCount()))

    def _dispose(self):
        self.ABSENT_VALUES = None
        self.__extra = None
        self.stopClubListening(self.__clubDBID)
        super(StaticFormationUnitView, self)._dispose()
        return

    def __updateHeader(self):
        isCreator = self.unitFunctional.getPlayerInfo().isCreator() if self.unitFunctional is not None else False
        club = self.clubsCtrl.getClub(self.__clubDBID)
        hasRankForModeChange = club is not None and club.getPermissions().canSetRanked()
        seasonActive = isSeasonInProgress()
        modeLabel = ''
        modeTooltip = ''
        modeTextStyle = TextType.STANDARD_TEXT
        if not seasonActive:
            modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_NOSEASON
            modeTooltip = CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_NOSEASONTOOLTIP
        elif isCreator:
            if not hasRankForModeChange:
                modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_LOWRANK
                modeTooltip = CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_LOWRANKTOOLTIP
            elif self.__extra.isRatedBattle:
                modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_SETUNRANKEDMODE
            else:
                modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_SETRANKEDMODE
        elif self.__extra.isRatedBattle:
            modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_RANKEDMODE
            modeTextStyle = TextType.NEUTRAL_TEXT
        else:
            modeLabel = CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_WRONGROLE
            modeTooltip = CYBERSPORT.STATICFORMATION_UNITVIEW_MODECHANGEWARNING_WRONGROLETOOLTIP
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
        self.as_setHeaderDataS({'teamName': self.__extra.clubName,
         'isRankedMode': bool(self.__extra.isRatedBattle),
         'battles': battles,
         'winRate': winRate,
         'enableWinRateTF': enableWinRateTF,
         'leagueIcon': leagueIcon,
         'isFixedMode': not seasonActive or not isCreator,
         'modeLabel': TextManager.getText(modeTextStyle, _ms(modeLabel)),
         'modeTooltip': modeTooltip,
         'bgSource': bgSource})
        return

    def __updateTotalData(self):
        functional = self.unitFunctional
        unitStats = functional.getStats()
        canDoAction, restriction = functional.validateLevels(stats=unitStats)
        self.as_setTotalLabelS(canDoAction, vo_converters.makeTotalLevelLabel(unitStats, restriction), unitStats.curTotalLevel)

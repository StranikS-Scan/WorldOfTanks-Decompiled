# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/ClubProfileWindow.py
import account_helpers
from adisp import process
from club_shared import RESTRICTION_REASONS_NAMES, RESTRICTION_REASONS
from gui import makeHtmlString, SystemMessages
from gui.Scaleform.daapi.view.meta.StaticFormationProfileWindowMeta import StaticFormationProfileWindowMeta
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.WAITING import WAITING
from gui.clubs import formatters as club_fmts
from gui.clubs.club_helpers import ClubListener, tryToConnectClubBattle
from gui.clubs.contexts import SendApplicationCtx, RevokeApplicationCtx
from gui.clubs.settings import CLIENT_CLUB_RESTRICTIONS, APPLICATIONS_COUNT, CLIENT_CLUB_STATE
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from gui.shared.view_helpers.emblems import ClubEmblemsHelper
from gui.shared.formatters import text_styles, icons
from gui.game_control.battle_availability import isHourInForbiddenList
from helpers import i18n
DEFAULT_WINDOW_SIZE = {'width': 1006,
 'height': 596}
STATE_BAR = [{'label': CYBERSPORT.STATICFORMATIONPROFILEWINDOW_TABSLBL_SUMMARY,
  'view': CYBER_SPORT_ALIASES.STATIC_FORMATION_SUMMARY_UI},
 {'label': CYBERSPORT.STATICFORMATIONPROFILEWINDOW_TABSLBL_STAFF,
  'view': CYBER_SPORT_ALIASES.STATIC_FORMATION_STAFF_UI},
 {'label': CYBERSPORT.STATICFORMATIONPROFILEWINDOW_TABSLBL_LADDER,
  'view': CYBER_SPORT_ALIASES.STATIC_FORMATION_LADDER_UI},
 {'label': CYBERSPORT.STATICFORMATIONPROFILEWINDOW_TABSLBL_STATS,
  'view': CYBER_SPORT_ALIASES.STATIC_FORMATION_STATS_UI}]

class ACTIONS(object):
    JOIN_CLUB_UNIT = 'joinClubUnit'
    SHOW_UNIT_WINDOW = 'showUnitWindow'
    SEND_APPLICATION = 'sendApplication'
    REVOKE_APPLICATION = 'revokeApplication'


STATE_MAP = [(CYBER_SPORT_ALIASES.STATIC_FORMATION_SUMMARY_UI, CYBER_SPORT_ALIASES.STATIC_FORMATION_SUMMARY_PY),
 (CYBER_SPORT_ALIASES.STATIC_FORMATION_STAFF_UI, CYBER_SPORT_ALIASES.STATIC_FORMATION_STAFF_PY),
 (CYBER_SPORT_ALIASES.STATIC_FORMATION_STATS_UI, CYBER_SPORT_ALIASES.STATIC_FORMATION_STATS_PY),
 (CYBER_SPORT_ALIASES.STATIC_FORMATION_LADDER_UI, CYBER_SPORT_ALIASES.STATIC_FORMATION_LADDER_PY)]

class ClubProfileWindow(StaticFormationProfileWindowMeta, ClubListener, GlobalListener, ClubEmblemsHelper):

    def __init__(self, ctx = None):
        super(ClubProfileWindow, self).__init__()
        self.__clubDbID = ctx.get('clubDbID', None)
        self.__viewToShow = ctx.get('viewIdx', -1)
        return

    def onClickHyperLink(self, value):
        g_eventBus.handleEvent(OpenLinkEvent(value))

    def onClubUpdated(self, club):
        if club is not None:
            self.__initializeGui(club)
        else:
            self.destroy()
        return

    def onUnitFunctionalInited(self):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def onUnitFunctionalFinished(self):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def showView(self, idx):
        self.as_showViewS(idx)

    def onClubNameChanged(self, name):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateFormationData(club)

    def onClubsSeasonStateChanged(self, seasonState):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateFormationData(club)

    def onClubMembersChanged(self, members):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def onClubEmblem64x64Received(self, clubDbID, emblem):
        if emblem and self.__clubDbID == clubDbID:
            self.as_setFormationEmblemS(self.getMemoryTexturePath(emblem))

    def onClubInvitesChanged(self, invites):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def onAccountClubStateChanged(self, state):
        if state.getStateID() == CLIENT_CLUB_STATE.UNKNOWN:
            return self.destroy()
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def onAccountClubRestrictionsChanged(self):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def onClubApplicantsChanged(self, applicants):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def onClubStateChanged(self, state):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def onClubUnitInfoChanged(self, unitInfo):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def onStatusChanged(self):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club:
            self.__updateActionButton(club)

    def actionBtnClickHandler(self, action):
        if action == ACTIONS.JOIN_CLUB_UNIT:
            self.__joinClubUnit()
        elif action == ACTIONS.SEND_APPLICATION:
            self.__sendApplication()
        elif action == ACTIONS.REVOKE_APPLICATION:
            self.__revokeApplication()
        elif action == ACTIONS.SHOW_UNIT_WINDOW and self._isMemberInClubUnit():
            self.unitFunctional.showGUI()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(ClubProfileWindow, self)._populate()
        self.as_setWindowSizeS(DEFAULT_WINDOW_SIZE['width'], DEFAULT_WINDOW_SIZE['height'])
        if self.__clubDbID is None:
            self.onWindowClose()
            return
        else:
            self.as_showWaitingS(WAITING.GETCLUBINFO, {})
            self.startClubListening(self.__clubDbID)
            self.startGlobalListening()
            club = self.clubsCtrl.getClub(self.__clubDbID)
            if club is not None:
                self.__initializeGui(club)
            self.clubsCtrl.getAvailabilityCtrl().onStatusChanged += self.onStatusChanged
            return

    def _dispose(self):
        self.stopClubListening(self.__clubDbID)
        self.stopGlobalListening()
        self.__clubDbID = None
        self.__viewToShow = None
        self.clubsCtrl.getAvailabilityCtrl().onStatusChanged -= self.onStatusChanged
        super(ClubProfileWindow, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in (CYBER_SPORT_ALIASES.STATIC_FORMATION_SUMMARY_PY,
         CYBER_SPORT_ALIASES.STATIC_FORMATION_STAFF_PY,
         CYBER_SPORT_ALIASES.STATIC_FORMATION_STATS_PY,
         CYBER_SPORT_ALIASES.STATIC_FORMATION_LADDER_PY):
            component = self.components.get(alias)
            if component:
                component.initClub(self.__clubDbID, self)

    def __initializeGui(self, club):
        self.__setTabsLabels()
        self.__updateActionButton(club)
        self.__updateFormationData(club)
        self.requestClubEmblem64x64(self.__clubDbID, club.getEmblem64x64())
        if self.__viewToShow != -1:
            self.showView(self.__viewToShow)
        self.as_hideWaitingS()

    @process
    def __sendApplication(self):
        result = yield self.clubsCtrl.sendRequest(SendApplicationCtx(self.__clubDbID, '', waitingID='clubs/app/send', confirmID='clubs/app/send'))
        if result.isSuccess():
            SystemMessages.pushMessage(club_fmts.getAppSentSysMsg(self.clubsCtrl.getClub(self.__clubDbID)))

    @process
    def __revokeApplication(self):
        self.as_showWaitingS(WAITING.CLUBS_APP_REVOKE, {})
        result = yield self.clubsCtrl.sendRequest(RevokeApplicationCtx(self.__clubDbID))
        if result.isSuccess():
            SystemMessages.pushMessage(club_fmts.getAppRevokeSysMsg(self.clubsCtrl.getClub(self.__clubDbID)))
        self.as_hideWaitingS()

    def __joinClubUnit(self):
        tryToConnectClubBattle(self.clubsCtrl.getClub(self.__clubDbID), self.clubsState.getJoiningTime())

    def __updateActionButton(self, club):
        labels, isEnableActionBtn, action = self.__getButtonInfo(club)
        data = {'buttonLabel': labels[0],
         'statusLbl': labels[1],
         'tooltipHeader': labels[2],
         'tooltipBody': labels[3],
         'action': action,
         'enabled': isEnableActionBtn}
        if isHourInForbiddenList(self.clubsCtrl.getAvailabilityCtrl().getForbiddenHours()):
            data['statusLbl'] = '{0}{1}'.format(icons.alert(), text_styles.main(CYBERSPORT.LADDERREGULATIONS_WARNING))
            data['isTooltipStatus'] = True
            data['tooltipStatus'] = TOOLTIPS_CONSTANTS.LADDER_REGULATIONS
        self.as_updateActionButtonS(data)

    def __getMemberBtnInfo(self, club):
        profile = self.clubsCtrl.getProfile()
        limits = self.clubsState.getLimits()
        if club.hasActiveUnit():
            canJoin, joinReason = limits.canJoinUnit(profile, club)
        else:
            canJoin, joinReason = limits.canCreateUnit(profile, club)
        action = ACTIONS.JOIN_CLUB_UNIT
        if canJoin:
            status = 'callClub'
            textFormatter = text_styles.main
            unitInfo = club.getUnitInfo()
            if unitInfo:
                if unitInfo.isInBattle():
                    status = 'clubInBattle'
                    textFormatter = lambda text: text_styles.main(icons.swords() + text)
                elif self._isMemberInClubUnit():
                    status = 'isInClubUnit'
                    action = ACTIONS.SHOW_UNIT_WINDOW
                else:
                    status = 'clubIsCalled'
        else:
            status = 'notEnoughPermissions'
            textFormatter = text_styles.error
            if joinReason == CLIENT_CLUB_RESTRICTIONS.NOT_ENOUGH_MEMBERS:
                status = 'notEnoughMembers'
        return (self.__getButtonLabels(status, textFormatter), canJoin, action)

    def __getNotMemberBtnInfo(self, club):
        limits = self.clubsState.getLimits()
        profile = self.clubsCtrl.getProfile()
        canSendApp, appReason = limits.canSendApplication(profile, club)
        canRevokeApp, revokeReason = limits.canRevokeApplication(profile, club)
        action = ACTIONS.SEND_APPLICATION
        status = 'joinRequest'
        isBtnEnabled = canSendApp
        textFormatter = text_styles.main
        statusArgs = {}
        tooltipArgs = {}
        if not canSendApp:
            if canRevokeApp:
                action = ACTIONS.REVOKE_APPLICATION
                status = 'joinRequestInProcess'
                textFormatter = text_styles.neutral
                isBtnEnabled = canRevokeApp
            elif appReason == CLIENT_CLUB_RESTRICTIONS.CLUB_IS_CLOSED:
                status = 'clubIsClosed'
            elif appReason == RESTRICTION_REASONS_NAMES[RESTRICTION_REASONS.APPLICATION_FOR_USER_EXCEEDED]:
                status = 'noFreeJoinRequests'
                statusArgs = {'count': APPLICATIONS_COUNT}
                textFormatter = text_styles.error
            elif appReason == RESTRICTION_REASONS_NAMES[RESTRICTION_REASONS.ACCOUNT_ALREADY_IN_TEAM]:
                status = 'inOtherClub'
                tooltipArgs = {'clubName': ''}
            elif appReason == RESTRICTION_REASONS_NAMES[RESTRICTION_REASONS.CANCEL_APPLICATION_COOLDOWN]:
                status = 'applicationCooldown'
        return (self.__getButtonLabels(status, textFormatter, statusArgs=statusArgs, tooltipArgs=tooltipArgs), isBtnEnabled, action)

    def __getButtonInfo(self, club):
        dbID = account_helpers.getAccountDatabaseID()
        if club.hasMember(dbID):
            return self.__getMemberBtnInfo(club)
        else:
            return self.__getNotMemberBtnInfo(club)

    def __getButtonLabels(self, state, formatter, statusArgs = None, tooltipArgs = None):
        statusArgs = statusArgs or {}
        tooltipArgs = tooltipArgs or {}
        actionBtnLbl = i18n.makeString('#cyberSport:StaticFormationProfileWindow/actionBtnLbl/%s' % state)
        statusLabel = i18n.makeString(('#cyberSport:StaticFormationProfileWindow/statusLbl/%s' % state), **statusArgs)
        statusLabel = formatter(statusLabel)
        tooltipHeader = i18n.makeString('#tooltips:StaticFormationProfileWindow/actionBtn/%s/header' % state)
        tooltipBody = i18n.makeString(('#tooltips:StaticFormationProfileWindow/actionBtn/%s/body' % state), **tooltipArgs)
        return (actionBtnLbl,
         statusLabel,
         tooltipHeader,
         tooltipBody)

    def _isMemberInClubUnit(self):
        _, unit = self.unitFunctional.getUnit(safe=True)
        return unit is not None and unit.isClub()

    def __updateFormationData(self, club):
        link = makeHtmlString('html_templates:lobby/clubs', 'link', {'text': i18n.makeString(CYBERSPORT.STATICFORMATIONPROFILEWINDOW_HYPERLINK_TEXT),
         'linkType': 'clubSettings'})
        seasonState = self.clubsCtrl.getSeasonState()
        if not seasonState.isActive():
            stateDescr = '#cybersport:StaticFormationSummaryView/season/state/%s' % seasonState.getStateString()
            seasonStateString = '\n'.join([text_styles.middleTitle(club_fmts.getSeasonStateUserString(seasonState)), text_styles.main(stateDescr)])
        else:
            seasonStateString = None
        profile = self.clubsCtrl.getProfile()
        canChange = self.clubsState.getLimits().canChangeWebSettings(profile, club).success
        self.as_updateFormationInfoS({'isShowLink': canChange,
         'seasonText': seasonStateString,
         'editLinkText': text_styles.main(link),
         'formationNameText': club.getUserName()})
        return

    def __setTabsLabels(self):
        self.as_setDataS({'stateMap': STATE_MAP,
         'stateBar': STATE_BAR})


class ClubPage(ClubListener):

    def __init__(self):
        self._owner = None
        self._clubDbID = None
        return

    def showWaiting(self, msg):
        if self._owner is not None:
            self._owner.as_showWaitingS(msg, {})
        return

    def hideWaiting(self):
        if self._owner is not None:
            self._owner.as_hideWaitingS()
        return

    def initClub(self, clubDbID, owner):
        self._clubDbID = clubDbID
        self._owner = owner
        self.startClubListening(self._clubDbID)
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club is not None:
            self._initializeGui(club)
        return

    def clearClub(self):
        self.stopClubListening(self._clubDbID)
        self._clubDbID = None
        self._owner = None
        return

    def _initializeGui(self, club):
        pass

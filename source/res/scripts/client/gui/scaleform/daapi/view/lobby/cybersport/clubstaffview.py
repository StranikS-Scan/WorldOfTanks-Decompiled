# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/ClubStaffView.py
import BigWorld
from adisp import process
from club_shared import CLUB_LIMITS
from account_helpers import getAccountDatabaseID
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubProfileWindow import ClubPage
from gui.Scaleform.locale.WAITING import WAITING
from gui.game_control import getIGRCtrl
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from helpers.i18n import makeString as _ms
from gui import DialogsInterface, SystemMessages
from gui.clubs import events_dispatcher as club_events, formatters as club_fmts
from gui.clubs.contexts import OpenCloseClubCtx, AssignOfficerCtx, AssignPrivateCtx, KickMemberCtx, DestroyClubCtx, LeaveClubCtx
from gui.clubs.settings import CLUB_REQUEST_TYPE
from gui.shared import events, formatters as shared_fmts
from gui.shared.formatters import text_styles
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.StaticFormationStaffViewMeta import StaticFormationStaffViewMeta
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.genConsts.FORMATION_MEMBER_TYPE import FORMATION_MEMBER_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from account_helpers.AccountSettings import AccountSettings, JOIN_COMMAND_PRESSED
from account_helpers.AccountSettings import SHOW_INVITE_COMMAND_BTN_ANIMATION

def _getFlashMemberType(member):
    if member.isOwner():
        return FORMATION_MEMBER_TYPE.OWNER
    elif member.isOfficer():
        return FORMATION_MEMBER_TYPE.OFFICER
    else:
        return FORMATION_MEMBER_TYPE.SOLDIER


def _packAppointment(profile, club, member, memberType, limits):
    return {'memberType': memberType,
     'canPromoted': member.isPrivate() and limits.canAssignOfficer(profile, club).success,
     'canDemoted': member.isOfficer() and limits.canAssignPrivate(profile, club).success,
     'promoteBtnIcon': RES_ICONS.MAPS_ICONS_BUTTONS_LEVEL_UP,
     'officerIcon': RES_ICONS.MAPS_ICONS_LIBRARY_COMMANDERICON,
     'demoteBtnIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CROSS,
     'ownerIcon': RES_ICONS.MAPS_ICONS_LIBRARY_OWNERICON,
     'officerIconTooltip': TOOLTIPS.STATICFORMATION_OFFICERICON,
     'ownerIconTooltip': TOOLTIPS.STATICFORMATION_OWNERICON,
     'demoteBtnTooltip': TOOLTIPS.STATICFORMATION_DEMOTEBTN,
     'promoteBtnTooltip': TOOLTIPS.STATICFORMATION_PROMOTEBTN}


def _packTableHeaderItem(tooltip, id, buttonWidth, label = '', icon = None, sortOrder = 0, sortType = 'numeric', inverted = False, enabled = True):
    return {'label': text_styles.standard(label) if label else '',
     'buttonWidth': buttonWidth,
     'enabled': enabled,
     'inverted': inverted,
     'sortType': sortType,
     'toolTip': tooltip,
     'sortOrder': sortOrder,
     'id': id,
     'iconSource': icon}


def _packTableHeaders():
    return [_packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAPPOINTMENT, 'appointmentSortValue', 126, label=CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERAPPOINTMENT_TEXT, sortOrder=1, inverted=True),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERNAME, 'userDataSortValue', 173, label=CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERNAME_TEXT, sortOrder=2, sortType='string'),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERRATING, 'ratingSortValue', 70, icon=RES_ICONS.MAPS_ICONS_STATISTIC_RATING24),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERBATTLESCOUNT, 'battlesCountSortValue', 70, icon=RES_ICONS.MAPS_ICONS_STATISTIC_BATTLES24),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERDAMAGECOEF, 'damageCoefSortValue', 70, icon=RES_ICONS.MAPS_ICONS_STATISTIC_DMGRATIO24),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVRDAMAGE, 'avrDamageSortValue', 70, icon=RES_ICONS.MAPS_ICONS_STATISTIC_AVGDAMAGE24),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVREXPIRIENCE, 'avrExperienceSortValue', 70, icon=RES_ICONS.MAPS_ICONS_STATISTIC_AVGEXP24),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVRASSISTDAMAGE, 'avrAssistDamageSortValue', 70, icon=RES_ICONS.MAPS_ICONS_STATISTIC_ASSIST24),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERTAUNT, 'tauntSortValue', 70, icon=RES_ICONS.MAPS_ICONS_STATISTIC_ARMORUSING24),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERJOINDATE, 'joinDateSortValue', 122, label=CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERJOINDATE_TEXT, sortOrder=3),
     _packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERREMOVEMEMBER, 'canDelete', 40, enabled=False)]


class ClubStaffView(StaticFormationStaffViewMeta, UsersInfoHelper, ClubPage):

    def __init__(self):
        StaticFormationStaffViewMeta.__init__(self)
        UsersInfoHelper.__init__(self)
        ClubPage.__init__(self)
        self.__openCloseCallbackID = None
        self.__viewerDbID = getAccountDatabaseID()
        self.addListener(events.CoolDownEvent.CLUB, self.__handleClubCooldown, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def onClubUpdated(self, club):
        if club is not None:
            self._initializeGui(club)
        return

    def onClubOwnerChanged(self, ownerDbID):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_setStaticHeaderDataS(self.__packStaticHeaderData(club))
            self.as_updateHeaderDataS(self.__packHeaderSettings(club))

    def showInviteWindow(self):
        AccountSettings.setFilter(SHOW_INVITE_COMMAND_BTN_ANIMATION, False)
        self.onClubStateChanged(None)
        club_events.showClubInvitesWindow(self._clubDbID)
        return

    def showRecriutmentWindow(self):
        club_events.showClubApplicationsWindow(self._clubDbID)

    def onClubStateChanged(self, state):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_updateHeaderDataS(self.__packHeaderSettings(club))

    def onClubRestrictionsChanged(self, restrictions):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_updateHeaderDataS(self.__packHeaderSettings(club))

    def onClubMembersChanged(self, members):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_updateHeaderDataS(self.__packHeaderSettings(club))
            self.as_updateStaffDataS(self.__packStaffData(club, syncUserInfo=True))
            self.as_setStaticHeaderDataS(self.__packStaticHeaderData(club))

    def onUserNamesReceived(self, names):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_updateStaffDataS(self.__packStaffData(club))

    def onUserRatingsReceived(self, ratings):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_updateStaffDataS(self.__packStaffData(club))

    def onClubApplicantsChanged(self, applicants):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_setStaticHeaderDataS(self.__packStaticHeaderData(club))

    @process
    def assignOfficer(self, memberDbID, userName):
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('staticFormation/staffView/promoteConfirmation', messageCtx={'userName': userName}))
        if isOk:
            self.showWaiting(WAITING.CLUBS_ASSIGNOFFICER)
            result = yield self.clubsCtrl.sendRequest(AssignOfficerCtx(self._clubDbID, int(memberDbID)))
            if result.isSuccess():
                SystemMessages.pushMessage(club_fmts.getAssignOfficerSysMsg(self.getUserFullName(int(memberDbID))))
            self.hideWaiting()

    @process
    def assignPrivate(self, memberDbID, userName):
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('staticFormation/staffView/demoteConfirmation', messageCtx={'userName': userName}))
        if isOk:
            self.showWaiting(WAITING.CLUBS_ASSIGNPRIVATE)
            results = yield self.clubsCtrl.sendRequest(AssignPrivateCtx(self._clubDbID, int(memberDbID)))
            if results.isSuccess():
                SystemMessages.pushMessage(club_fmts.getAssignPrivateSysMsg(self.getUserFullName(int(memberDbID))))
            self.hideWaiting()

    def removeMe(self):
        club = self.clubsCtrl.getClub(self._clubDbID)
        profile = self.clubsCtrl.getProfile()
        limits = self.clubsState.getLimits()
        if club:
            if limits.canDestroyClub(profile, club).success:
                self._disbandClub(club)
            else:
                self._leaveClub()

    def removeMember(self, memberDbID, userName):
        if memberDbID == self.__viewerDbID:
            self.removeMe()
        else:
            self._kickMember(memberDbID, userName)

    @process
    def setRecruitmentOpened(self, opened):
        AccountSettings.setFilter(JOIN_COMMAND_PRESSED, True)
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club.getState().isOpened() != opened:
            sendRequest = True
            if not opened and len(club.getApplicants(onlyActive=True)):
                sendRequest = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('staticFormation/staffView/closeClub'))
            if sendRequest:
                waitingID = WAITING.CLUBS_OPENCLUB if opened else WAITING.CLUBS_CLOSECLUB
                self.showWaiting(waitingID)
                result = yield self.clubsCtrl.sendRequest(OpenCloseClubCtx(opened, self._clubDbID))
                if result.isSuccess():
                    SystemMessages.pushMessage(club_fmts.getOpenClubSysMsg(opened))
                self.hideWaiting()
        self.as_updateHeaderDataS(self.__packHeaderSettings(club))

    def _disbandClub(self, club):
        if len(club.getMembers()) > 1:
            i18nKey = 'discontinuingFormationConfirmation'
        else:
            i18nKey = 'discontinuingEmptyFormationConfirmation'
        sysMsg = club_fmts.getDestroyClubSysMsg(self.clubsCtrl.getClub(self._clubDbID))
        self._doExitAction(DestroyClubCtx(self._clubDbID), I18nConfirmDialogMeta('staticFormation/staffView/%s' % i18nKey, focusedID=DIALOG_BUTTON_ID.CLOSE), WAITING.CLUBS_DESTROYCLUB, sysMsg)

    def _leaveClub(self):
        sysMsg = club_fmts.getLeaveClubSysMsg(self.clubsCtrl.getClub(self._clubDbID))
        self._doExitAction(LeaveClubCtx(self._clubDbID), I18nConfirmDialogMeta('staticFormation/staffView/leaveClubConfirmation', focusedID=DIALOG_BUTTON_ID.CLOSE), WAITING.CLUBS_LEAVECLUB, sysMsg)

    def _kickMember(self, memberDbID, memberUserName):
        sysMsg = club_fmts.getKickMemberSysMsg(memberUserName)
        self._doExitAction(KickMemberCtx(self._clubDbID, memberDbID), I18nConfirmDialogMeta('staticFormation/staffView/removeMemberConfirmation', messageCtx={'userName': memberUserName}, focusedID=DIALOG_BUTTON_ID.CLOSE), WAITING.CLUBS_CLUBKICKMEMBER, sysMsg)

    @process
    def _doExitAction(self, ctx, dialogMeta, waiting, sysMsg):
        isOk = yield DialogsInterface.showDialog(dialogMeta)
        if isOk:
            self.showWaiting(waiting)
            result = yield self.clubsCtrl.sendRequest(ctx)
            if result.isSuccess():
                SystemMessages.pushMessage(sysMsg)
            self.hideWaiting()

    def _dispose(self):
        self.clearClub()
        self.__viewerDbID = None
        self.removeListener(events.CoolDownEvent.CLUB, self.__handleClubCooldown, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__openCloseCallbackID:
            BigWorld.cancelCallback(self.__openCloseCallbackID)
            self.__openCloseCallbackID = None
        super(ClubStaffView, self)._dispose()
        return

    def _initializeGui(self, club):
        self.as_setStaticHeaderDataS(self.__packStaticHeaderData(club))
        self.as_updateHeaderDataS(self.__packHeaderSettings(club))
        self.as_updateStaffDataS(self.__packStaffData(club, syncUserInfo=True))

    def __packHeaderSettings(self, club):
        isInStaff = club.hasMember(self.__viewerDbID)
        isEnoughPlayers = club.isStaffed()
        profile = self.clubsCtrl.getProfile()
        limits = self.clubsState.getLimits()
        canSendInvite = limits.canSendInvite(profile, club).success
        canSeeApplicants = limits.canSeeApplicants(profile, club).success
        if isEnoughPlayers:
            btnInviteTooltip = TOOLTIPS.STATICFORMATIONSTAFFVIEW_INVITEBTNDIS
        else:
            btnInviteTooltip = TOOLTIPS.STATICFORMATIONSTAFFVIEW_INVITEBTN
        removeBtnVisible = limits.canDestroyClub(profile, club).success or limits.canLeaveClub(profile, club).success
        return {'lblDescriptionVisible': not isInStaff,
         'lblStaffedVisible': isEnoughPlayers and isInStaff,
         'btnRemoveVisible': removeBtnVisible,
         'btnInviteVisible': canSendInvite,
         'btnInviteEnable': not isEnoughPlayers,
         'showInviteBtnAnimation': not isEnoughPlayers and AccountSettings.getFilter(SHOW_INVITE_COMMAND_BTN_ANIMATION) and canSendInvite,
         'btnInviteTooltip': btnInviteTooltip,
         'isRecruitmentOpened': club.getState().isOpened(),
         'btnRecruitmentVisible': canSeeApplicants,
         'isCheckBoxPressed': not AccountSettings.getFilter(JOIN_COMMAND_PRESSED),
         'cbOpenedVisible': limits.canOpenClub(profile, club).success}

    def __packStaticHeaderData(self, club):
        profile = self.clubsCtrl.getProfile()
        limits = self.clubsState.getLimits()
        if limits.canDestroyClub(profile, club).success:
            btnDestroyText = _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_DESTROYSTATIC_TEXT)
        elif limits.canLeaveClub(profile, club).success:
            btnDestroyText = _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_EXITSTATIC_TEXT)
        else:
            btnDestroyText = ''
        if club.canParticipateBattles():
            lblStaffedText = ''.join([text_styles.success(CYBERSPORT.STATICFORMATION_STAFFVIEW_LBLSTAFFED_TEXT),
             text_styles.standard(' ('),
             text_styles.main(str(len(club.getMembers()))),
             text_styles.standard('/%d)' % CLUB_LIMITS.MAX_MEMBERS)])
        else:
            lblStaffedText = ''
        return {'lblTitleText': text_styles.highTitle(CYBERSPORT.STATICFORMATION_STAFFVIEW_TITLE_TEXT),
         'lblDescriptionText': text_styles.standard(_ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_DESCRIPTION_OTHER_TEXT, clubName=club.getUserName())),
         'btnRecruitmentText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_RECRUITMENTBTN_TEXT, count=len(club.getApplicants(onlyActive=True))),
         'btnRecruitmentTooltip': TOOLTIPS.STATICFORMATIONSTAFFVIEW_RECRUITMENTBTN,
         'btnInviteText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_INVITEBTN_TEXT),
         'btnRemoveText': btnDestroyText,
         'cbOpenedText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_RECRUITMENTOPENEDCHKBX_TEXT),
         'lblStaffedText': lblStaffedText,
         'lblStaffedTooltip': TOOLTIPS.STATICFORMATIONSTAFFVIEW_LBLSTAFFED,
         'tableHeader': _packTableHeaders()}

    def __handleClubCooldown(self, event):
        if event.requestID in (CLUB_REQUEST_TYPE.OPEN_CLUB, CLUB_REQUEST_TYPE.CLOSE_CLUB):
            if self.__openCloseCallbackID:
                BigWorld.cancelCallback(self.__openCloseCallbackID)
                self.__openCloseCallbackID = None
            self.__openCloseCallbackID = BigWorld.callback(event.coolDown, self.__resetCooldown)
            self.as_setRecruitmentAvailabilityS(False)
        return

    def __resetCooldown(self):
        self.__openCloseCallbackID = None
        self.as_setRecruitmentAvailabilityS(True)
        return

    def __packStaffData(self, club, syncUserInfo = False):
        members = []
        membersDict = club.getMembers()
        membersCount = len(membersDict)
        for dbID, member in membersDict.iteritems():
            memberType = _getFlashMemberType(member)
            isSelf = dbID == self.__viewerDbID
            limits = self.clubsState.getLimits()
            profile = self.clubsCtrl.getProfile()
            memberStats = member.getSeasonDossier().getRated7x7Stats()
            battlesCount = memberStats.getBattlesCount()
            rating = self.getUserRating(dbID)
            damageCoef = memberStats.getDamageEfficiency() or 0
            avgDamage = memberStats.getAvgDamage() or 0
            avgAssistDamage = memberStats.getDamageAssistedEfficiency() or 0
            avgExperience = memberStats.getAvgXP() or 0
            armorUsingEfficiency = memberStats.getArmorUsingEfficiency() or 0
            joinDate = member.getJoiningTime()
            if isSelf:
                removeBtnTooltip = TOOLTIPS.STATICFORMATIONSTAFFVIEW_REMOVEHIMSELFBTN
            else:
                removeBtnTooltip = TOOLTIPS.STATICFORMATIONSTAFFVIEW_REMOVEMEMBERBTN
            userData = self.getGuiUserData(dbID)
            userData.update({'igrType': getIGRCtrl().getRoomType()})
            members.append({'memberId': dbID,
             'canRemoved': self.__canBeRemoved(profile, club, member, membersCount, limits),
             'canPassOwnership': limits.canTransferOwnership(profile, club).success,
             'canShowContextMenu': not isSelf,
             'removeMemberBtnIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CROSS,
             'removeMemberBtnTooltip': removeBtnTooltip,
             'appointmentSortValue': memberType,
             'appointment': _packAppointment(profile, club, member, memberType, limits),
             'ratingSortValue': rating,
             'rating': self.getGuiUserRating(dbID, text_styles.neutral),
             'battlesCountSortValue': battlesCount,
             'battlesCount': text_styles.main(BigWorld.wg_getIntegralFormat(battlesCount)),
             'damageCoefSortValue': damageCoef,
             'damageCoef': text_styles.main(BigWorld.wg_getNiceNumberFormat(damageCoef)),
             'avrDamageSortValue': avgDamage,
             'avrDamage': text_styles.main(BigWorld.wg_getIntegralFormat(avgDamage)),
             'avrAssistDamageSortValue': avgAssistDamage,
             'avrAssistDamage': text_styles.main(BigWorld.wg_getNiceNumberFormat(avgAssistDamage)),
             'avrExperienceSortValue': avgExperience,
             'avrExperience': text_styles.main(BigWorld.wg_getIntegralFormat(avgExperience)),
             'tauntSortValue': armorUsingEfficiency,
             'taunt': text_styles.main(BigWorld.wg_getNiceNumberFormat(armorUsingEfficiency)),
             'joinDateSortValue': joinDate,
             'joinDate': text_styles.standard(BigWorld.wg_getShortDateFormat(joinDate)),
             'userDataSortValue': self.getUserFullName(dbID).lower(),
             'userData': userData,
             'clubDbID': self._clubDbID})

        if syncUserInfo:
            self.syncUsersInfo()
        return {'members': sorted(members, key=lambda k: k['userDataSortValue'].lower())}

    def __canBeRemoved(self, profile, club, member, membersCount, limits):
        isSelf = member.getDbID() == self.__viewerDbID
        if isSelf:
            if member.isOwner():
                return membersCount == 1
            else:
                return True
        else:
            return limits.canKickMember(profile, club).success

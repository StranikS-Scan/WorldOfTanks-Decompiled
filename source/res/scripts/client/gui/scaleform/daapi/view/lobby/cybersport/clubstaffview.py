# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/ClubStaffView.py
import BigWorld
from adisp import process
from account_helpers import getPlayerDatabaseID
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubProfileWindow import ClubPage
from gui.Scaleform.locale.WAITING import WAITING
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
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta

class ClubStaffView(StaticFormationStaffViewMeta, UsersInfoHelper, ClubPage):

    def __init__(self):
        StaticFormationStaffViewMeta.__init__(self)
        UsersInfoHelper.__init__(self)
        ClubPage.__init__(self)
        self.__openCloseCallbackID = None
        self.__viewerDbID = getPlayerDatabaseID()
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
        club_events.showClubInvitesWindow(self._clubDbID)

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
            self.as_updateStaffDataS(self.__packStaffData(club, syncUserInfo=True))

    def onUserNamesReceived(self, names):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_updateStaffDataS(self.__packStaffData(club))

    def onUserRatingsReceived(self, ratings):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club:
            self.as_updateStaffDataS(self.__packStaffData(club))

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

    @process
    def removeMember(self, memberDbID, userName):
        member = self.clubsCtrl.getClub(self._clubDbID).getMember(memberDbID)
        if member.isOwner():
            i18nId = 'staticFormation/staffView/discontinuingFormationConfirmation'
        elif self.__viewerDbID == memberDbID:
            i18nId = 'staticFormation/staffView/leaveClubConfirmation'
        else:
            i18nId = 'staticFormation/staffView/removeMemberConfirmation'
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta(i18nId, messageCtx={'userName': userName}))
        if isOk:
            if member.isOwner():
                ctx = DestroyClubCtx(self._clubDbID)
                waitingID = WAITING.CLUBS_DESTROYCLUB
                successSysMsg = club_fmts.getDestroyClubSysMsg(self.clubsCtrl.getClub(self._clubDbID))
            elif self.__viewerDbID == memberDbID:
                ctx = LeaveClubCtx(self._clubDbID)
                waitingID = WAITING.CLUBS_LEAVECLUB
                successSysMsg = club_fmts.getLeaveClubSysMsg(self.clubsCtrl.getClub(self._clubDbID))
            else:
                ctx = KickMemberCtx(self._clubDbID, memberDbID)
                waitingID = WAITING.CLUBS_CLUBKICKMEMBER
                successSysMsg = club_fmts.getKickMemberSysMsg(self.getUserFullName(memberDbID))
            self.showWaiting(waitingID)
            result = yield self.clubsCtrl.sendRequest(ctx)
            if result.isSuccess():
                SystemMessages.pushMessage(successSysMsg)
            self.hideWaiting()

    @process
    def setRecruitmentOpened(self, opened):
        club = self.clubsCtrl.getClub(self._clubDbID)
        stateIsOpened = club.getState().isOpened()
        if stateIsOpened != opened:
            sendRequest = True
            if not opened and (len(club.getInvites(onlyActive=True)) or len(club.getApplicants(onlyActive=True))):
                sendRequest = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('staticFormation/staffView/closeClub'))
            if sendRequest:
                waitingID = WAITING.CLUBS_OPENCLUB if opened else WAITING.CLUBS_CLOSECLUB
                self.showWaiting(waitingID)
                result = yield self.clubsCtrl.sendRequest(OpenCloseClubCtx(opened, self._clubDbID))
                if result.isSuccess():
                    SystemMessages.pushMessage(club_fmts.getOpenClubSysMsg(opened))
                self.hideWaiting()
        club = self.clubsCtrl.getClub(self._clubDbID)
        self.as_updateHeaderDataS(self.__packHeaderSettings(club))

    def _populate(self):
        super(ClubStaffView, self)._populate()

    def _dispose(self):
        super(ClubStaffView, self)._dispose()
        self.clearClub()
        self.__viewerDbID = None
        self.removeListener(events.CoolDownEvent.CLUB, self.__handleClubCooldown, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__openCloseCallbackID:
            BigWorld.cancelCallback(self.__openCloseCallbackID)
            self.__openCloseCallbackID = None
        return

    def _initializeGui(self, club):
        self.as_setStaticHeaderDataS(self.__packStaticHeaderData(club))
        self.as_updateHeaderDataS(self.__packHeaderSettings(club))
        self.as_updateStaffDataS(self.__packStaffData(club, syncUserInfo=True))

    def __packTableHeaders(self):
        return [self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERCOUNT, 'orderNumberSortValue', label=CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERCOUNT_TEXT),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAPPOINTMENT, 'appointmentSortValue', label=CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERAPPOINTMENT_TEXT, sortOrder=1),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERNAME, 'userDataSortValue', label=CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERNAME_TEXT, sortOrder=2),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERRATING, 'ratingSortValue', icon=RES_ICONS.MAPS_ICONS_STATISTIC_RATING24),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERBATTLESCOUNT, 'battlesCountSortValue', icon=RES_ICONS.MAPS_ICONS_STATISTIC_BATTLES24),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERDAMAGECOEF, 'damageCoefSortValue', icon=RES_ICONS.MAPS_ICONS_STATISTIC_DMGRATIO24),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVRDAMAGE, 'avrDamageSortValue', icon=RES_ICONS.MAPS_ICONS_STATISTIC_AVGDAMAGE24),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVREXPIRIENCE, 'avrExperienceSortValue', icon=RES_ICONS.MAPS_ICONS_STATISTIC_AVGEXP24),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERAVRASSISTDAMAGE, 'avrAssistDamageSortValue', icon=RES_ICONS.MAPS_ICONS_STATISTIC_ASSIST24),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERTAUNT, 'tauntSortValue', icon=RES_ICONS.MAPS_ICONS_STATISTIC_ARMORUSING24),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERJOINDATE, 'joinDateSortValue', label=CYBERSPORT.STATICFORMATION_STAFFVIEW_STAFFTABLE_HEADERJOINDATE_TEXT, sortOrder=3),
         self.__packTableHeaderItem(TOOLTIPS.STATICFORMATIONSTAFFVIEW_TABLE_HEADERREMOVEMEMBER, 'canDelete')]

    def __packTableHeaderItem(self, tooltip, iconId, label = '', icon = None, sortOrder = 0):
        return {'label': text_styles.standard(label) if label else '',
         'toolTip': tooltip,
         'sortOrder': sortOrder,
         'iconId': iconId,
         'iconSource': icon}

    def __packHeaderSettings(self, club):
        memberInfo = club.getMember(self.__viewerDbID)
        profile = self.clubsCtrl.getProfile()
        limits = self.clubsState.getLimits()
        canInvite = limits.canSendInvite(profile, club).success
        notEnoughPlayers = not club.canParticipateBattles()
        return {'canInvite': canInvite,
         'inviteBtnText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_INVITEBTN_TEXT),
         'inviteBtnTooltip': TOOLTIPS.STATICFORMATIONSTAFFVIEW_INVITEBTN,
         'canOpenClose': limits.canOpenClub(profile, club).success,
         'isRecruitmentOpened': club.getState().isOpened(),
         'isClubMember': memberInfo is not None,
         'showInviteBtnAnimation': notEnoughPlayers and canInvite}

    def __packStaticHeaderData(self, club):
        memberInfo = club.getMember(self.__viewerDbID)
        if memberInfo:
            if memberInfo.isOwner():
                description = CYBERSPORT.STATICFORMATION_STAFFVIEW_DESCRIPTION_OWNER_TEXT
            else:
                description = CYBERSPORT.STATICFORMATION_STAFFVIEW_DESCRIPTION_MEMBER_TEXT
        else:
            description = _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_DESCRIPTION_OTHER_TEXT, clubName=club.getUserName())
        return {'title': text_styles.highTitle(CYBERSPORT.STATICFORMATION_STAFFVIEW_TITLE_TEXT),
         'description': text_styles.standard(description),
         'recruitmentBtnText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_RECRUITMENTBTN_TEXT),
         'recruitmentOpenedText': _ms(CYBERSPORT.STATICFORMATION_STAFFVIEW_RECRUITMENTOPENEDCHKBX_TEXT),
         'recruitmentBtnTooltip': TOOLTIPS.STATICFORMATIONSTAFFVIEW_RECRUITMENTBTN,
         'tableHeaders': self.__packTableHeaders()}

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
        formatDate = BigWorld.wg_getShortDateFormat
        members = []
        membersDict = club.getMembers()
        membersCount = len(membersDict)
        for dbID, member in membersDict.iteritems():
            memberType = self.__getFlashMemberType(member)
            isSelf = dbID == self.__viewerDbID
            limits = self.clubsState.getLimits()
            profile = self.clubsCtrl.getProfile()
            memberStats = member.getTotalDossier().getRated7x7Stats()
            battlesCount = memberStats.getBattlesCount()
            rating = self.getUserRating(dbID)
            damageCoef = memberStats.getDamageEfficiency() or 0
            avgDamage = memberStats.getAvgDamage() or 0
            avgAssistDamage = memberStats.getDamageAssistedEfficiency() or 0
            avgExperience = memberStats.getAvgXP() or 0
            armorUsingEfficiency = memberStats.getArmorUsingEfficiency() or 0
            joinDate = member.getJoiningTime()
            removeBtnTooltip = TOOLTIPS.STATICFORMATIONSTAFFVIEW_REMOVEMEMBERBTN
            if isSelf:
                removeBtnTooltip = TOOLTIPS.STATICFORMATIONSTAFFVIEW_REMOVEHIMSELFBTN
            members.append({'memberId': dbID,
             'canRemoved': self.__canBeRemoved(profile, club, member, membersCount, limits),
             'canPassOwnership': limits.canTransferOwnership(profile, club).success,
             'canShowContextMenu': not isSelf,
             'removeMemberBtnIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CROSS,
             'removeMemberBtnTooltip': removeBtnTooltip,
             'appointmentSortValue': memberType,
             'appointment': self.__packAppointment(profile, club, member, memberType, limits),
             'ratingSortValue': rating,
             'rating': text_styles.main(shared_fmts.getGlobalRatingFmt(rating)),
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
             'joinDate': text_styles.standard(formatDate(joinDate)),
             'userDataSortValue': self.getUserFullName(dbID).lower(),
             'userData': self.getGuiUserData(dbID),
             'clubDbID': self._clubDbID})

        members = sorted(members, key=lambda k: k['userDataSortValue'].lower())
        for idx, member in enumerate(members):
            staffIdx = idx + 1
            member['orderNumberSortValue'] = staffIdx
            member['orderNumber'] = text_styles.standard(str(staffIdx) + '.')

        if syncUserInfo:
            self.syncUsersInfo()
        return {'members': members}

    def __canBeRemoved(self, profile, club, member, membersCount, limits):
        isSelf = member.getDbID() == self.__viewerDbID
        if isSelf:
            if member.isOwner():
                return membersCount == 1
            else:
                return True
        else:
            return limits.canKickMember(profile, club).success

    def __getFlashMemberType(self, member):
        if member.isOwner():
            return FORMATION_MEMBER_TYPE.OWNER
        elif member.isOfficer():
            return FORMATION_MEMBER_TYPE.OFFICER
        else:
            return FORMATION_MEMBER_TYPE.SOLDIER

    def __packAppointment(self, profile, club, member, memberType, limits):
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

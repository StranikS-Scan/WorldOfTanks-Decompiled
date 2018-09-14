# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/ClubUserCMHandler.py
from adisp import process
from debug_utils import LOG_DEBUG
from gui import SystemMessages, DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler
from gui.shared.view_helpers import UsersInfoHelper
from gui.clubs import formatters as club_fmts
from gui.clubs.club_helpers import ClubListener
from gui.clubs.contexts import TransferOwnershipCtx, AssignOfficerCtx, AssignPrivateCtx
ASSIGN_OFFICER = 'assignOfficer'
ASSIGN_PRIVATE = 'assignPrivate'
GIVE_LEADERSHIP = 'giveLeadership'

class ClubUserCMHandler(BaseUserCMHandler, ClubListener, UsersInfoHelper):

    def __init__(self, cmProxy, ctx = None):
        super(ClubUserCMHandler, self).__init__(cmProxy, ctx)

    def onClubMembersChanged(self, members):
        self.onContextMenuHide()

    @process
    def giveLeadership(self):
        clubDbID = self.__clubDbID
        databaseID = self.databaseID
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('staticFormation/staffView/transferOwnership'))
        if isOk:
            result = yield self.clubsCtrl.sendRequest(TransferOwnershipCtx(clubDbID, databaseID, waitingID='clubs/transferOwnership'))
            if result.isSuccess():
                SystemMessages.pushMessage(club_fmts.getTransferOwnershipSysMsg(self.getUserFullName(databaseID)))

    @process
    def assignOfficer(self):
        databaseID = self.databaseID
        result = yield self.clubsCtrl.sendRequest(AssignOfficerCtx(self.__clubDbID, databaseID, waitingID='clubs/assignOfficer'))
        if result.isSuccess():
            SystemMessages.pushMessage(club_fmts.getAssignOfficerSysMsg(self.getUserFullName(databaseID)))

    @process
    def assignPrivate(self):
        databaseID = self.databaseID
        result = yield self.clubsCtrl.sendRequest(AssignPrivateCtx(self.__clubDbID, databaseID, waitingID='clubs/assignPrivate'))
        if result.isSuccess():
            SystemMessages.pushMessage(club_fmts.getAssignPrivateSysMsg(self.getUserFullName(databaseID)))

    def _addClubInfo(self, options, userCMInfo):
        club = self.clubsCtrl.getClub(self.__clubDbID)
        if club is not None:
            profile = self.clubsCtrl.getProfile()
            limits = self.clubsState.getLimits()
            member = club.getMember(self.databaseID)
            if limits.canTransferOwnership(profile, club).success:
                options.append(self._makeItem(GIVE_LEADERSHIP, MENU.contextmenu(GIVE_LEADERSHIP)))
            if member.isPrivate():
                if limits.canAssignOfficer(profile, club).success:
                    options.append(self._makeItem(ASSIGN_OFFICER, MENU.contextmenu(ASSIGN_OFFICER)))
            if member.isOfficer():
                if limits.canAssignPrivate(profile, club).success:
                    options.append(self._makeItem(ASSIGN_PRIVATE, MENU.contextmenu(ASSIGN_PRIVATE)))
        return options

    def _initFlashValues(self, ctx):
        super(ClubUserCMHandler, self)._initFlashValues(ctx)
        self.__clubDbID = long(ctx.clubDbID)

    def _clearFlashValues(self):
        super(ClubUserCMHandler, self)._clearFlashValues()
        self.__clubDbID = None
        return

    def _getHandlers(self):
        handlers = super(ClubUserCMHandler, self)._getHandlers()
        handlers.update({ASSIGN_OFFICER: 'assignOfficer',
         ASSIGN_PRIVATE: 'assignPrivate',
         GIVE_LEADERSHIP: 'giveLeadership'})
        return handlers

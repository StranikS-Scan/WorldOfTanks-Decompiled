# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scalefrom/InvitesInterface.py
# Compiled at: 2018-11-29 14:33:44
from account_helpers.AccountPrebattle import AccountPrebattle
import BigWorld
from constants import IS_DEVELOPMENT
from debug_utils import LOG_WARNING
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from messenger.gui.interfaces import DispatcherProxyHolder
from messenger.gui.Scalefrom import INV_COMMANDS
from PlayerEvents import g_playerEvents

class InvitesInterface(DispatcherProxyHolder):

    def __init__(self):
        self.__movieViewHandler = None
        self.__joinArgs = tuple()
        return

    @property
    def invitesManager(self):
        return self._dispatcherProxy.invites

    def populateUI(self, movieViewHandler):
        self.__movieViewHandler = movieViewHandler
        self.invitesManager.onReceivedInviteListInited += self.__pim_onReceivedInviteListInited
        self.invitesManager.onReceivedInviteListModified += self.__pim_onReceivedInviteListModified
        self.__movieViewHandler.addExternalCallbacks({INV_COMMANDS.GetReceivedInvite(): self.onGetReceivedInvite,
         INV_COMMANDS.RequestList(): self.onRequestReceivedInviteList,
         INV_COMMANDS.AcceptInvite(): self.onAcceptInvite,
         INV_COMMANDS.RejectInvite(): self.onRejectInvite,
         INV_COMMANDS.LeftPrbAndAcceptInvite(): self.onLeftPrebattleAndAcceptInvite,
         INV_COMMANDS.RequestUnreadCount(): self.onRequestUnreadCount,
         INV_COMMANDS.ClearUnreadCount(): self.onClearUnreadCount})

    def dispossessUI(self):
        self.clear()
        self.invitesManager.onReceivedInviteListInited -= self.__pim_onReceivedInviteListInited
        self.invitesManager.onReceivedInviteListModified -= self.__pim_onReceivedInviteListModified
        self.__movieViewHandler.removeExternalCallbacks(INV_COMMANDS.GetReceivedInvite(), INV_COMMANDS.RequestList(), INV_COMMANDS.AcceptInvite(), INV_COMMANDS.RejectInvite(), INV_COMMANDS.LeftPrbAndAcceptInvite(), INV_COMMANDS.RequestUnreadCount(), INV_COMMANDS.ClearUnreadCount())
        self.__movieViewHandler = None
        return

    def clear(self):
        if self.__movieViewHandler:
            self.__movieViewHandler.call(INV_COMMANDS.ClearData())

    def __comparator(self, data, other):
        return cmp(data[0].createTime, other[0].createTime)

    def __pim_onReceivedInviteListInited(self):
        self.__movieViewHandler.call(INV_COMMANDS.RefreshList(), [self.invitesManager.getUnreadCount()])

    def __pim_onReceivedInviteListModified(self, added, changed, deleted):
        if len(added) and not len(changed) and not len(deleted):
            invites = self.invitesManager.getReceivedInvites(added)
            invites = sorted(invites, cmp=self.__comparator)
            links = map(lambda item: item[1], invites)
            self.__movieViewHandler.call(INV_COMMANDS.ReceiveInvites(), ['\n'.join(links)])
        else:
            self.__movieViewHandler.call(INV_COMMANDS.RefreshList(), [self.invitesManager.getUnreadCount()])
            if len(deleted):
                self.__movieViewHandler.call(INV_COMMANDS.DeletedInvites(), deleted)
            if len(changed):
                self.__movieViewHandler.call(INV_COMMANDS.ChangedInvites(), changed)

    def onGetReceivedInvite(self, *args):
        parser = CommandArgsParser(self.onGetReceivedInvite.__name__, 1, [int])
        inviteID = parser.parse(*args)
        invite, _ = self.invitesManager.getReceivedInvite(inviteID)
        if invite:
            formatter = self.invitesManager.formatter
            parser.addArgs([int(invite.id),
             formatter.title(invite),
             formatter.format(invite),
             invite.comment,
             invite.opFlags()])
            self.__movieViewHandler.respond(parser.args())
        elif IS_DEVELOPMENT:
            LOG_WARNING('Not found invite with id = %d' % inviteID)

    def onRequestReceivedInviteList(self, *args):
        parser = CommandArgsParser(self.onRequestReceivedInviteList.__name__)
        parser.parse(*args)
        invites = self.invitesManager.getReceivedInvites()
        invites = sorted(invites, cmp=self.__comparator)
        links = map(lambda item: item[1], invites)
        parser.addArg('\n'.join(links))
        self.__movieViewHandler.respond(parser.args())

    def onAcceptInvite(self, *args):
        parser = CommandArgsParser(self.onAcceptInvite.__name__, 1, [int])
        inviteID = parser.parse(*args)
        if inviteID:
            if AccountPrebattle.get():
                dialog = 'leftPrebattleAndAcceptInvite'
                if AccountPrebattle.isTraining():
                    dialog = 'leftTrainingAndAcceptInvite'
                elif AccountPrebattle.isSquad():
                    dialog = 'leftSquadAndAcceptInvite'
                elif AccountPrebattle.isCompany():
                    dialog = 'leftTeamAndAcceptInvite'
                self.__movieViewHandler.call(INV_COMMANDS.CloseReceivedInviteWindow(), [int(inviteID)])
                self.__movieViewHandler.call('common.showMessageDialog', [dialog,
                 True,
                 True,
                 None,
                 INV_COMMANDS.LeftPrbAndAcceptInvite(),
                 inviteID])
                return
            if BigWorld.player().isInQueue:
                self.__movieViewHandler.call('common.showMessageDialog', ['cancelInvite', True, False])
                return
            isCaptchaRequired = True
            captcha = self.__movieViewHandler.captcha
            if isCaptchaRequired and captcha.isCaptchaRequired():
                captcha.showCaptcha(lambda : self.__doAcceptInvite(inviteID))
            else:
                self.__doAcceptInvite(inviteID)
        return

    def __doAcceptInvite(self, inviteID):
        self.invitesManager.acceptInvite(inviteID)

    def onRejectInvite(self, *args):
        parser = CommandArgsParser(self.onRejectInvite.__name__, 1, [int])
        inviteID = parser.parse(*args)
        if inviteID:
            self.invitesManager.declineInvite(inviteID)

    def onRequestUnreadCount(self, *args):
        parser = CommandArgsParser(self.onRequestUnreadCount.__name__)
        parser.parse(*args)
        parser.addArg(self.invitesManager.getUnreadCount())
        self.__movieViewHandler.respond(parser.args())

    def onClearUnreadCount(self, *args):
        self.invitesManager.resetUnreadCount()

    def onLeftPrebattleAndAcceptInvite(self, *args):
        self.__joinArgs = args
        g_playerEvents.onPrebattleLeft += self.__pe_onPrebattleLeft
        BigWorld.player().prb_leave(self.__cb_onPrbLeft)

    def __cb_onPrbLeft(self, code):
        if code < 0:
            LOG_WARNING('Error to leave prebattle code: %s' % code)
            g_playerEvents.onPrebattleLeft -= self.__pe_onPrebattleLeft
            self.__joinArgs = tuple()

    def __pe_onPrebattleLeft(self):
        g_playerEvents.onPrebattleLeft -= self.__pe_onPrebattleLeft
        if self.__joinArgs:
            self.onAcceptInvite(*self.__joinArgs)
            self.__joinArgs = tuple()

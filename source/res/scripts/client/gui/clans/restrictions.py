# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/restrictions.py
import weakref
from constants import CLAN_MEMBER_FLAGS
from debug_utils import LOG_DEBUG, LOG_WARNING
from account_helpers import isOutOfWallet, isClanEnabled
from gui.shared import g_itemsCache
from gui.clans.settings import error, success, CLIENT_CLAN_RESTRICTIONS as _CCR
from gui.clans.settings import isValidPattern

class ClanMemberPermissions(object):

    def __init__(self, bwRoleMask):
        self.__roleMask = bwRoleMask

    def canChangeSettings(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_CHANGE_SETTINGS)

    def canChangeRole(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_CHANGE_ROLE)

    def canEditRecruiterProfile(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_EDIT_RECRUIT_PROFILE)

    def canChangeCommander(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_CHANGE_COMMANDER)

    def canHandleClanInvites(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_HANDLE_INVITES)

    def canRemoveMembers(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_REMOVE_MEMBERS)

    def canRemoveClan(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_REMOVE_CLAN)

    def canTrade(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_TRADE)

    def canExchangeMoney(self):
        return self.__checkFlags(CLAN_MEMBER_FLAGS.MAY_EXCHANGE_MONEY)

    def canSendApplication(self):
        return self.isValidAccountType()

    def canRevokeApplication(self):
        LOG_DEBUG('Application revoking is not supported')
        return False

    def canAcceptInvite(self):
        return self.isValidAccountType()

    def canDeclineInvite(self):
        return self.isValidAccountType()

    def canSeeClans(self):
        return True

    def isValidAccountType(self):
        attrs = g_itemsCache.items.stats.attributes
        return not (isOutOfWallet(attrs) and not isClanEnabled(attrs))

    def __checkFlags(self, flags):
        return self.__roleMask & flags != 0


class DefaultClanMemberPermissions(ClanMemberPermissions):

    def __init__(self):
        super(DefaultClanMemberPermissions, self).__init__(0)


class BaseAccountClanLimits(object):

    def canHandleClanInvites(self, clan):
        return error(_CCR.DEFAULT)

    def canSendApplication(self, clan):
        return error(_CCR.DEFAULT)

    def canRevokeApplication(self, clan):
        return error(_CCR.DEFAULT)

    def canAcceptApplication(self, clan):
        return error(_CCR.DEFAULT)

    def canDeclineApplication(self, clan):
        return error(_CCR.DEFAULT)

    def canSendInvite(self, clan):
        return error(_CCR.DEFAULT)

    def canRevokeInvite(self, clan):
        return error(_CCR.DEFAULT)

    def canAcceptInvite(self, clan):
        return error(_CCR.DEFAULT)

    def canDeclineInvite(self, clan):
        return error(_CCR.DEFAULT)

    def canSearchClans(self, pattern):
        return error(_CCR.DEFAULT)

    def canSeeTreasury(self, clan):
        return error(_CCR.DEFAULT)


class DefaultAccountClanLimits(BaseAccountClanLimits):

    def __init__(self):
        super(DefaultAccountClanLimits, self).__init__()


class AccountClanLimits(BaseAccountClanLimits):

    def __init__(self, profile):
        super(AccountClanLimits, self).__init__()
        self.__profile = weakref.proxy(profile)

    def canSeeTreasury(self, clan):
        return self.__checkPermissions('canExchangeMoney', clan)

    def canSendApplication(self, clan):
        if self.__profile.isInClan():
            if self.__profile.getClanDbID() == clan.getDbID():
                return error(_CCR.OWN_CLAN)
            else:
                return error(_CCR.ALREADY_IN_CLAN)
        if self.__profile.hasClanInvite(clan.getDbID()):
            return error(_CCR.CLAN_INVITE_ALREADY_RECEIVED)
        if self.__profile.isClanApplicationSent(clan.getDbID()):
            return error(_CCR.CLAN_APPLICATION_ALREADY_SENT)
        if self.__profile.isInClanEnterCooldown():
            return error(_CCR.CLAN_LEAVE_COOLDOWN)
        if self.__profile.isInvitesLimitReached():
            return error(_CCR.SENT_INVITES_LIMIT_REACHED)
        if not clan.canAcceptsJoinRequests():
            return error(_CCR.CLAN_CONSCRIPTION_CLOSED)
        if not self.__profile.getPermissions(clan).isValidAccountType():
            return error(_CCR.FORBIDDEN_ACCOUNT_TYPE)
        if not clan.hasFreePlaces():
            return error(_CCR.CLAN_IS_FULL)
        return self.__checkPermissions('canSendApplication', clan)

    def canRevokeApplication(self, clan):
        return self.__checkPermissions('canRevokeApplication', clan)

    def canHandleClanInvites(self, clan):
        return self.__checkPermissions('canHandleClanInvites', clan)

    def canAcceptApplication(self, clan):
        return self.__checkPermissions('canHandleClanInvites', clan)

    def canDeclineApplication(self, clan):
        return self.__checkPermissions('canHandleClanInvites', clan)

    def canSendInvite(self, clan):
        return self.__checkPermissions('canHandleClanInvites', clan)

    def canRevokeInvite(self, clan):
        return self.__checkPermissions('canHandleClanInvites', clan)

    def canAcceptInvite(self, clan):
        return self.__checkPermissions('canAcceptInvite', clan)

    def canDeclineInvite(self, clan):
        return self.__checkPermissions('canDeclineInvite', clan)

    def canSearchClans(self, pattern):
        if not isValidPattern(pattern):
            return error(_CCR.SEARCH_PATTERN_INVALID)
        return self.__checkPermissions('canSeeClans')

    def __checkPermissions(self, permName, clan = None):
        perms = self.__profile.getPermissions(clan)
        if not hasattr(perms, permName):
            LOG_WARNING('There is error while checking account clan permissions', clan, permName)
            return error(_CCR.DEFAULT)
        if not getattr(perms, permName)():
            return error(_CCR.DEFAULT)
        return success()

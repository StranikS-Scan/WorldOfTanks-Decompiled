# Embedded file name: scripts/client/gui/wgnc/proxy_data.py
from gui.wgnc.events import g_wgncEvents
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from account_helpers import getAccountDatabaseID

class _ProxyDataItem(object):

    def getType(self):
        raise NotImplementedError

    def show(self, notID):
        g_wgncEvents.onProxyDataItemShowByDefault(notID, self)


class _ClanBaseAooItem(_ProxyDataItem):

    def getID(self):
        pass


class ClanApplicationItem(_ClanBaseAooItem):

    def __init__(self, account_id, application_id, active_applications_count):
        super(ClanApplicationItem, self).__init__()
        self.__accountId = account_id
        self.__appId = application_id
        self.__applicationsCount = active_applications_count

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_APP

    def getAccountID(self):
        return self.__accountId

    def getApplicationID(self):
        return self.__appId

    def getActiveApplicationsCount(self):
        return self.__applicationsCount

    def getID(self):
        return self.getApplicationID()


class ClanInviteItem(_ClanBaseAooItem):

    def __init__(self, invite_id, clan_id, clan_name, clan_tag, active_invites_count):
        super(ClanInviteItem, self).__init__()
        self.__inviteId = invite_id
        self.__clanId = clan_id
        self.__clanName = clan_name
        self.__clanTag = clan_tag
        self.__activeInvitesCount = active_invites_count

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_INVITE

    def getInviteId(self):
        return self.__inviteId

    def getClanId(self):
        return self.__clanId

    def getClanName(self):
        return self.__clanName

    def getClanTag(self):
        return self.__clanTag

    def getActiveInvitesCount(self):
        return self.__activeInvitesCount

    def getID(self):
        return self.getInviteId()

    def getAccountDbID(self):
        return getAccountDatabaseID()


class _ClanPersonalAppItem(_ProxyDataItem):

    def __init__(self, clan_id, clan_name, clan_tag, application_id):
        super(_ClanPersonalAppItem, self).__init__()
        self.__clanId = clan_id
        self.__clanName = clan_name
        self.__clanTag = clan_tag
        self.__applicationId = application_id

    def getClanId(self):
        return self.__clanId

    def getClanName(self):
        return self.__clanName

    def getClanTag(self):
        return self.__clanTag

    def getApplicationId(self):
        return self.__applicationId


class ClanAppDeclinedItem(_ClanPersonalAppItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED


class ClanAppAcceptedItem(_ClanPersonalAppItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED


class _ClanInviteActionResultItem(_ProxyDataItem):

    def __init__(self, account_id, invite_id):
        super(_ClanInviteActionResultItem, self).__init__()
        self.__accountId = account_id
        self.__inviteId = invite_id

    def getAccountID(self):
        return self.__accountId

    def getInviteId(self):
        return self.__inviteId


class ClanInviteDeclinedItem(_ClanInviteActionResultItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_INVITE_DECLINED


class ClanInviteAcceptedItem(_ClanInviteActionResultItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_INVITE_ACCEPTED


class ProxyDataHolder(object):

    def __init__(self, items):
        super(ProxyDataHolder, self).__init__()
        self.__items = {item.getType():item for item in items}

    def all(self):
        return self.__items.itervalues()

    def hasItemType(self, itemType):
        return itemType in self.__items

    def getItemByType(self, itemType):
        item = None
        if self.hasItemType(itemType):
            item = self.__items[itemType]
        return item

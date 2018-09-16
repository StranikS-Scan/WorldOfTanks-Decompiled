# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/clan/contexts.py
from gui.clans import items
from gui.clans.settings import SEND_INVITES_COOLDOWN, DECLINE_INVITES_COOLDOWN, ACCEPT_INVITES_COOLDOWN
from gui.shared.utils.decorators import ReprInjector
from gui.wgcg.base.contexts import CommonWebRequestCtx, AccountsInfoBaseCtx, PaginatorCtx, TotalInfoCtx
from gui.wgcg.settings import WebRequestDataType
from shared_utils import makeTupleByDict

class ClanFavouriteAttributesCtx(CommonWebRequestCtx):

    def __init__(self, clanID, waitingID=''):
        super(ClanFavouriteAttributesCtx, self).__init__(waitingID)
        self._clanID = clanID

    def getClanID(self):
        return self._clanID

    def getRequestType(self):
        return WebRequestDataType.CLAN_FAVOURITE_ATTRS

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanFavouriteAttrs, incomeData)

    def getDefDataObj(self):
        return items.ClanFavouriteAttrs()


@ReprInjector.withParent(('getClanID', 'clanID'))
class WebRequestBaseCtx(CommonWebRequestCtx):

    def __init__(self, clanID, waitingID=''):
        super(WebRequestBaseCtx, self).__init__(waitingID)
        self._clanID = clanID

    def getClanID(self):
        return self._clanID

    def getRequestType(self):
        raise NotImplementedError

    def getDataObj(self, incomeData):
        raise NotImplementedError

    def getDefDataObj(self):
        raise NotImplementedError


@ReprInjector.withParent()
class ClanInfoCtx(WebRequestBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.CLAN_INFO

    def getDataObj(self, incomeData):
        return makeTupleByDict(items.ClanExtInfoData, incomeData[0]) if incomeData else items.ClanExtInfoData()

    def getDefDataObj(self):
        return items.ClanExtInfoData()

    def isCaching(self):
        return True

    def isAuthorizationRequired(self):
        return self.getClanID() == self._getOwnClanDbID()

    def getFields(self):
        fields = list(items.ClanExtInfoData._fields)
        if self.getClanID() != self._getOwnClanDbID():
            fields.remove('treasury')
        return fields


@ReprInjector.withParent(('getClanIDs', 'clanIDs'))
class ClansInfoCtx(CommonWebRequestCtx):

    def __init__(self, clanIDs, waitingID=''):
        super(ClansInfoCtx, self).__init__(waitingID)
        self._clanIDs = clanIDs

    def getClanIDs(self):
        return self._clanIDs

    def getRequestType(self):
        return WebRequestDataType.CLANS_INFO

    def getDataObj(self, incomeData):
        data = incomeData or []
        return [ makeTupleByDict(items.ClanExtInfoData, item) for item in data ]

    def getDefDataObj(self):
        return []

    def isAuthorizationRequired(self):
        return False

    def getFields(self):
        fields = list(items.ClanExtInfoData._fields)
        fields.remove('treasury')
        return fields


@ReprInjector.withParent(('getClanIDs', 'clanIDs'))
class ClanRatingsCtx(CommonWebRequestCtx):

    def __init__(self, clanIDs, waitingID=''):
        super(ClanRatingsCtx, self).__init__(waitingID)
        self._clanIDs = clanIDs

    def getClanIDs(self):
        return self._clanIDs

    def getRequestType(self):
        return WebRequestDataType.CLAN_RATINGS

    def getDataObj(self, incomeData):
        data = incomeData or []
        return [ makeTupleByDict(items.ClanRatingsData, item) for item in data ]

    def getDefDataObj(self):
        return []


@ReprInjector.withParent()
class ClanGlobalMapStatsCtx(WebRequestBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.CLAN_GLOBAL_MAP_STATS

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanGlobalMapStatsData, incomeData)

    def getDefDataObj(self):
        return items.ClanGlobalMapStatsData()

    def isAuthorizationRequired(self):
        return self.getClanID() == self._getOwnClanDbID()


@ReprInjector.withParent()
class AccountsInfoCtx(AccountsInfoBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.CLAN_ACCOUNTS

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return [ makeTupleByDict(items.AccountClanData, v) for v in incomeData ]

    def getDefDataObj(self):
        return []


@ReprInjector.withParent()
class GetClanInfoCtx(AccountsInfoCtx):

    def __init__(self, accountDbID, waitingID=''):
        super(GetClanInfoCtx, self).__init__([accountDbID], waitingID)
        self.__defDataObj = items.AccountClanData(accountDbID)

    def getDataObj(self, incomeData):
        return makeTupleByDict(items.AccountClanData, incomeData.pop()) if incomeData else self.getDefDataObj()

    def getDefDataObj(self):
        return self.__defDataObj

    def isCaching(self):
        return True


@ReprInjector.withParent()
class AccountClanRatingsCtx(AccountsInfoBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.CLAN_MEMBERS_RATING

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        result = {}
        for data in incomeData:
            result[data['account_id']] = makeTupleByDict(items.AccountClanRatingsData, data)

        return result

    def getDefDataObj(self):
        return {}


@ReprInjector.withParent()
class _BaseSearchClanContext(PaginatorCtx):

    def getRequestType(self):
        raise NotImplementedError

    def getDataObj(self, incomeData):
        data = super(_BaseSearchClanContext, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanSearchData, item) for item in data ]


@ReprInjector.withParent()
class GetRecommendedClansCtx(_BaseSearchClanContext):

    def getRequestType(self):
        return WebRequestDataType.GET_RECOMMENDED_CLANS


@ReprInjector.withParent(('getSearchCriteria', 'pattern'))
class SearchClansCtx(_BaseSearchClanContext):

    def __init__(self, searchCriteria, offset, limit, getTotalCount=False, fields=None, waitingID=''):
        super(SearchClansCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__searchCriteria = searchCriteria

    def getSearchCriteria(self):
        return self.__searchCriteria

    def getRequestType(self):
        return WebRequestDataType.SEARCH_CLANS


@ReprInjector.withParent(('getClanDbID', 'clanDbID'), ('getStatuses', 'statuses'))
class ClanApplicationsCtx(PaginatorCtx):

    def __init__(self, clanDbID, offset, limit, statuses=None, getTotalCount=False, fields=None, waitingID=''):
        super(ClanApplicationsCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__clanDbID = clanDbID
        self.__statuses = statuses

    def getClanDbID(self):
        return self.__clanDbID

    def getStatuses(self):
        return self.__statuses

    def getRequestType(self):
        return WebRequestDataType.CLAN_APPLICATIONS

    def getDataObj(self, incomeData):
        data = super(ClanApplicationsCtx, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanInviteData, item) for item in data ]

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getClanDbID', 'clanDbID'), ('getStatuses', 'statuses'))
class ClanInvitesCtx(PaginatorCtx):

    def __init__(self, clanDbID, offset, limit, statuses=None, getTotalCount=False, fields=None, waitingID=''):
        super(ClanInvitesCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__clanDbID = clanDbID
        self.__statuses = statuses

    def getClanDbID(self):
        return self.__clanDbID

    def getStatuses(self):
        return self.__statuses

    def getRequestType(self):
        return WebRequestDataType.CLAN_INVITES

    def getDataObj(self, incomeData):
        data = super(ClanInvitesCtx, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanInviteData, item) for item in data ]

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getAccountDbID', 'accountDbID'), ('getStatuses', 'statuses'))
class AccountInvitesCtx(PaginatorCtx):

    def __init__(self, accountDbID, offset, limit, statuses=None, getTotalCount=False, fields=None, waitingID=''):
        super(AccountInvitesCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__accountDbID = accountDbID
        self.__statuses = statuses

    def getAccountDbID(self):
        return self.__accountDbID

    def getStatuses(self):
        return self.__statuses

    def getRequestType(self):
        return WebRequestDataType.ACCOUNT_INVITES

    def getDataObj(self, incomeData):
        data = super(AccountInvitesCtx, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanInviteData, item) for item in data ]

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getClanDbID', 'clanDbID'), ('getAccountDbIDs', 'accountDbIDs'), ('getComment', 'comment'))
class CreateInviteCtx(CommonWebRequestCtx):

    def __init__(self, clanDbID, accountDbIDs, comment='', waitingID=''):
        super(CreateInviteCtx, self).__init__(waitingID)
        self.__clanDbID = clanDbID
        self.__accountDbIDs = accountDbIDs
        self.__comment = comment

    def getClanDbID(self):
        return self.__clanDbID

    def getAccountDbIDs(self):
        return self.__accountDbIDs

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return WebRequestDataType.CREATE_INVITES

    def getDataObj(self, incomeData):
        data = incomeData or []
        return [ makeTupleByDict(items.ClanCreateInviteData, item) for item in data ]

    def getDefDataObj(self):
        return list()

    def getCooldown(self):
        return SEND_INVITES_COOLDOWN

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getApplicationDbID', 'applicationDbID'))
class DeclineApplicationCtx(CommonWebRequestCtx):

    def __init__(self, appDbID, waitingID=''):
        super(DeclineApplicationCtx, self).__init__(waitingID)
        self.__appDbID = appDbID

    def getApplicationDbID(self):
        return self.__appDbID

    def getRequestType(self):
        return WebRequestDataType.DECLINE_APPLICATION

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanADInviteData, incomeData)

    def getDefDataObj(self):
        return items.ClanADInviteData()

    def isAuthorizationRequired(self):
        return True

    def getCooldown(self):
        return DECLINE_INVITES_COOLDOWN


@ReprInjector.withParent(('getInviteDbID', 'inviteDbID'))
class DeclineInviteCtx(CommonWebRequestCtx):

    def __init__(self, inviteDbID, waitingID=''):
        super(DeclineInviteCtx, self).__init__(waitingID)
        self.__inviteDbID = inviteDbID

    def getInviteDbID(self):
        return self.__inviteDbID

    def getRequestType(self):
        return WebRequestDataType.DECLINE_INVITE

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanADInviteData, incomeData)

    def getDefDataObj(self):
        return items.ClanADInviteData()

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()
class GetClanAppsCount(ClanApplicationsCtx):

    def __init__(self, clanDbID, isCaching, statuses=None, waitingID=''):
        super(GetClanAppsCount, self).__init__(clanDbID, 0, 1, statuses, getTotalCount=True, fields=['id'], waitingID=waitingID)
        self.__isCaching = isCaching

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return incomeData.get('total', None)

    def getDefDataObj(self):
        return None

    def isCaching(self):
        return self.__isCaching

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()
class GetClanInvitesCount(ClanInvitesCtx):

    def __init__(self, clanDbID, statuses=None, waitingID=''):
        super(GetClanInvitesCount, self).__init__(clanDbID, 0, 1, statuses, getTotalCount=True, fields=['id'], waitingID=waitingID)

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return incomeData.get('total', None)

    def getDefDataObj(self):
        return None

    def isCaching(self):
        return True

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()
class ClanMembersCtx(WebRequestBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.CLAN_MEMBERS

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return [ makeTupleByDict(items.ClanMemberData, v) for v in incomeData ]

    def getDefDataObj(self):
        return []


@ReprInjector.withParent()
class GetFrontsCtx(CommonWebRequestCtx):

    def __init__(self, provincesIDs, waitingID=''):
        super(GetFrontsCtx, self).__init__(waitingID)
        self.__provincesIDs = provincesIDs

    def getRequestType(self):
        return WebRequestDataType.CLAN_GM_FRONTS

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return dict(((v['front_name'], makeTupleByDict(items.GlobalMapFrontInfoData, v)) for v in incomeData))

    def getDefDataObj(self):
        return items.GlobalMapFrontInfoData({})

    def getProvincesIDs(self):
        return self.__provincesIDs


@ReprInjector.withParent(('getInviteDbIDs', 'inviteDbIDs'))
class DeclineInvitesCtx(CommonWebRequestCtx):

    def __init__(self, inviteDbIDs, waitingID=''):
        super(DeclineInvitesCtx, self).__init__(waitingID)
        self.__inviteDbIDs = inviteDbIDs

    def getInviteDbIDs(self):
        return self.__inviteDbIDs

    def getRequestType(self):
        return WebRequestDataType.DECLINE_INVITES

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return [ makeTupleByDict(items.ClanADInviteData, item) for item in incomeData ]

    def getDefDataObj(self):
        return []

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()
class GetAccountInvitesCount(AccountInvitesCtx):

    def __init__(self, accountDbID, statuses=None, waitingID=''):
        super(GetAccountInvitesCount, self).__init__(accountDbID, 0, 1, statuses, getTotalCount=True, fields=['id'], waitingID=waitingID)

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return incomeData.get('total', None)

    def getDefDataObj(self):
        return None

    def isCaching(self):
        return True

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getAccountDbID', 'accountDbID'), ('getStatuses', 'statuses'))
class AccountApplicationsCtx(PaginatorCtx):

    def __init__(self, accountDbID, offset, limit, statuses=None, getTotalCount=False, fields=None, waitingID=''):
        super(AccountApplicationsCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__accountDbID = accountDbID
        self.__statuses = statuses

    def getAccountDbID(self):
        return self.__accountDbID

    def getStatuses(self):
        return self.__statuses

    def getRequestType(self):
        return WebRequestDataType.GET_ACCOUNT_APPLICATIONS

    def getDataObj(self, incomeData):
        data = super(AccountApplicationsCtx, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanInviteData, item) for item in data ]

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()
class GetAccountAppsCount(AccountApplicationsCtx):

    def __init__(self, accountDbID, statuses=None, waitingID=''):
        super(GetAccountAppsCount, self).__init__(accountDbID, 0, 1, statuses, getTotalCount=True, fields=['id'], waitingID=waitingID)

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return incomeData.get('total', None)

    def getDefDataObj(self):
        return None

    def isCaching(self):
        return True

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()
class GetProvincesCtx(WebRequestBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.CLAN_PROVINCES

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return [ makeTupleByDict(items.ClanProvinceData, v) for v in incomeData ]

    def getDefDataObj(self):
        return []

    def isAuthorizationRequired(self):
        return self.getClanID() == self._getOwnClanDbID()


@ReprInjector.withParent()
class AccountApplicationsCountCtx(TotalInfoCtx):

    def getRequestType(self):
        return WebRequestDataType.ACCOUNT_APPLICATIONS_COUNT

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getApplicationDbID', 'applicationDbID'))
class AcceptApplicationCtx(CommonWebRequestCtx):

    def __init__(self, appDbID, waitingID=''):
        super(AcceptApplicationCtx, self).__init__(waitingID)
        self.__appDbID = appDbID

    def getApplicationDbID(self):
        return self.__appDbID

    def getRequestType(self):
        return WebRequestDataType.ACCEPT_APPLICATION

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanADInviteData, incomeData)

    def getDefDataObj(self):
        return items.ClanADInviteData()

    def isAuthorizationRequired(self):
        return True

    def getCooldown(self):
        return ACCEPT_INVITES_COOLDOWN


@ReprInjector.withParent(('getInviteDbID', 'inviteDbID'))
class AcceptInviteCtx(CommonWebRequestCtx):

    def __init__(self, inviteDbID, waitingID=''):
        super(AcceptInviteCtx, self).__init__(waitingID)
        self.__inviteDbID = inviteDbID

    def getInviteDbID(self):
        return self.__inviteDbID

    def getRequestType(self):
        return WebRequestDataType.ACCEPT_INVITE

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanADInviteData, incomeData)

    def getDefDataObj(self):
        return items.ClanADInviteData()

    def isAuthorizationRequired(self):
        return True

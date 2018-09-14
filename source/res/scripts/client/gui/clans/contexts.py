# Embedded file name: scripts/client/gui/clans/contexts.py
from shared_utils import makeTupleByDict
from gui.clans import items
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE, SEND_INVITES_COOLDOWN
from gui.clubs.settings import DEFAULT_COOLDOWN
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx
from gui.shared import g_itemsCache

def _getOwnClanDbID():
    return g_itemsCache.items.stats.clanDBID


@ReprInjector.withParent()

class CommonClanRequestCtx(RequestCtx):

    def __init__(self, waitingID = ''):
        super(CommonClanRequestCtx, self).__init__(waitingID=waitingID)

    def getCooldown(self):
        return DEFAULT_COOLDOWN

    def isCaching(self):
        return True

    def isAuthorizationRequired(self):
        return False

    def getFields(self):
        return None


@ReprInjector.withParent(('getTokenID', 'token'), ('getUserDatabaseID', 'dbID'))

class LogInCtx(CommonClanRequestCtx):

    def __init__(self, databaseID, tokenID):
        super(LogInCtx, self).__init__()
        self.__tokenID = tokenID
        self.__databaseID = databaseID

    def getTokenID(self):
        return self.__tokenID

    def getUserDatabaseID(self):
        return self.__databaseID

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.LOGIN


@ReprInjector.withParent()

class LogOutCtx(CommonClanRequestCtx):

    def __init__(self):
        super(LogOutCtx, self).__init__()

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.LOGOUT


@ReprInjector.withParent(('getClanID', 'clanID'))

class _ClanRequestBaseCtx(CommonClanRequestCtx):

    def __init__(self, clanID, waitingID = ''):
        super(_ClanRequestBaseCtx, self).__init__(waitingID)
        self._clanID = clanID

    def getClanID(self):
        return self._clanID

    def getRequestType(self):
        raise NotImplementedError

    def getDataObj(self, incomeData):
        raise NotImplementedError

    def getDefDataObj(self):
        raise NotImplementedError


class ClanFavouriteAttributesCtx(CommonClanRequestCtx):

    def __init__(self, clanID, waitingID = ''):
        super(ClanFavouriteAttributesCtx, self).__init__(waitingID)
        self._clanID = clanID

    def getClanID(self):
        return self._clanID

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_FAVOURITE_ATTRS

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanFavouriteAttrs, incomeData)

    def getDefDataObj(self):
        return items.ClanFavouriteAttrs


@ReprInjector.withParent()

class ClanInfoCtx(_ClanRequestBaseCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_INFO

    def getDataObj(self, incomeData):
        if incomeData is not None and len(incomeData) > 0:
            return makeTupleByDict(items.ClanExtInfoData, incomeData[0])
        else:
            return items.ClanExtInfoData()

    def getDefDataObj(self):
        return items.ClanExtInfoData()

    def isCaching(self):
        return True

    def isAuthorizationRequired(self):
        return self.getClanID() == _getOwnClanDbID()

    def getFields(self):
        fields = list(items.ClanExtInfoData._fields)
        if self.getClanID() != _getOwnClanDbID():
            fields.remove('treasury')
        return fields


@ReprInjector.withParent(('getClanIDs', 'clanIDs'))

class ClansInfoCtx(CommonClanRequestCtx):

    def __init__(self, clanIDs, waitingID = ''):
        super(ClansInfoCtx, self).__init__(waitingID)
        self._clanIDs = clanIDs

    def getClanIDs(self):
        return self._clanIDs

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLANS_INFO

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

class ClanRatingsCtx(CommonClanRequestCtx):

    def __init__(self, clanIDs, waitingID = ''):
        super(ClanRatingsCtx, self).__init__(waitingID)
        self._clanIDs = clanIDs

    def getClanIDs(self):
        return self._clanIDs

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_RATINGS

    def getDataObj(self, incomeData):
        data = incomeData or []
        return [ makeTupleByDict(items.ClanRatingsData, item) for item in data ]

    def getDefDataObj(self):
        return []


@ReprInjector.withParent()

class ClanGlobalMapStatsCtx(_ClanRequestBaseCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_GLOBAL_MAP_STATS

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanGlobalMapStatsData, incomeData)

    def getDefDataObj(self):
        return items.ClanGlobalMapStatsData()

    def isAuthorizationRequired(self):
        return self.getClanID() == _getOwnClanDbID()


@ReprInjector.withParent(('getAccountsIDs', 'ids'))

class _AccountsInfoBaseCtx(CommonClanRequestCtx):

    def __init__(self, accIDs, waitingID = ''):
        super(_AccountsInfoBaseCtx, self).__init__(waitingID)
        self.__accountsIDs = accIDs

    def getAccountsIDs(self):
        return self.__accountsIDs


@ReprInjector.withParent()

class AccountsInfoCtx(_AccountsInfoBaseCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_ACCOUNTS

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return map(lambda v: makeTupleByDict(items.AccountClanData, v), incomeData)

    def getDefDataObj(self):
        return []


@ReprInjector.withParent()

class GetClanInfoCtx(AccountsInfoCtx):

    def __init__(self, accountDbID, waitingID = ''):
        super(GetClanInfoCtx, self).__init__([accountDbID], waitingID)
        self.__defDataObj = items.AccountClanData(accountDbID)

    def getDataObj(self, incomeData):
        if incomeData:
            return makeTupleByDict(items.AccountClanData, incomeData.pop())
        return self.getDefDataObj()

    def getDefDataObj(self):
        return self.__defDataObj

    def isCaching(self):
        return True


@ReprInjector.withParent()

class AccountClanRatingsCtx(_AccountsInfoBaseCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_MEMBERS_RATING

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        result = {}
        for data in incomeData:
            result[data['account_id']] = makeTupleByDict(items.AccountClanRatingsData, data)

        return result

    def getDefDataObj(self):
        return {}


@ReprInjector.withParent()

class StrongholdInfoCtx(_ClanRequestBaseCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.STRONGHOLD_INFO

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanStrongholdInfoData, incomeData)

    def getDefDataObj(self):
        return items.ClanStrongholdInfoData()


@ReprInjector.withParent()

class StrongholdStatisticsCtx(_ClanRequestBaseCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.STRONGHOLD_STATISTICS

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanStrongholdStatisticsData, incomeData)

    def getDefDataObj(self):
        return items.ClanStrongholdStatisticsData()


@ReprInjector.withParent()

class GetProvincesCtx(_ClanRequestBaseCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_PROVINCES

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return map(lambda v: makeTupleByDict(items.ClanProvinceData, v), incomeData)

    def getDefDataObj(self):
        return []

    def isAuthorizationRequired(self):
        return self.getClanID() == _getOwnClanDbID()


@ReprInjector.withParent()

class GetFrontsCtx(CommonClanRequestCtx):

    def __init__(self, provincesIDs, waitingID = ''):
        super(GetFrontsCtx, self).__init__(waitingID)
        self.__provincesIDs = provincesIDs

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_GM_FRONTS

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return dict(map(lambda v: (v['front_name'], makeTupleByDict(items.GlobalMapFrontInfoData, v)), incomeData))

    def getDefDataObj(self):
        return items.GlobalMapFrontInfoData({})

    def getProvincesIDs(self):
        return self.__provincesIDs


@ReprInjector.withParent()

class ClanMembersCtx(_ClanRequestBaseCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_MEMBERS

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return map(lambda v: makeTupleByDict(items.ClanMemberData, v), incomeData)

    def getDefDataObj(self):
        return []


@ReprInjector.withParent(('getID', 'id'))

class TotalInfoCtx(CommonClanRequestCtx):

    def __init__(self, itemID, waitingID = ''):
        super(TotalInfoCtx, self).__init__(waitingID)
        self.__itemID = itemID

    def getID(self):
        return self.__itemID

    def getDataObj(self, incomeData):
        if incomeData:
            return incomeData['total']
        return self.getDefDataObj()

    def getDefDataObj(self):
        return 0


@ReprInjector.withParent()

class AccountApplicationsCountCtx(TotalInfoCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.ACCOUNT_APPLICATIONS_COUNT

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()

class ClanInvitationsCountCtx(TotalInfoCtx):

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_INVITATIONS_COUNT

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getOffset', 'offset'), ('getLimit', 'limit'), ('isGetTotalCount', 'isGetTotalCount'), ('getFields', 'fields'))

class PaginatorCtx(CommonClanRequestCtx):

    def __init__(self, offset, limit, getTotalCount = False, fields = None, waitingID = ''):
        super(PaginatorCtx, self).__init__(waitingID)
        self.__offset = offset
        self.__limit = limit
        self.__getTotalCount = getTotalCount
        self.__fields = fields

    def getOffset(self):
        return self.__offset

    def getLimit(self):
        return self.__limit

    def isGetTotalCount(self):
        return self.__getTotalCount

    def getFields(self):
        return self.__fields

    def getTotalCount(self, incomeData):
        if incomeData:
            return incomeData.get('total', None)
        else:
            return None

    def getDataObj(self, incomeData):
        data = incomeData.get('items', self.getDefDataObj()) if incomeData else self.getDefDataObj()
        return data

    def getDefDataObj(self):
        return list()


@ReprInjector.withParent()

class _BaseSearchClanContext(PaginatorCtx):

    def __init__(self, offset, limit, getTotalCount = False, fields = None, waitingID = ''):
        super(_BaseSearchClanContext, self).__init__(offset, limit, getTotalCount, fields, waitingID)

    def getRequestType(self):
        raise NotImplementedError

    def getDataObj(self, incomeData):
        data = super(_BaseSearchClanContext, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanSearchData, item) for item in data ]


@ReprInjector.withParent()

class GetRecommendedClansCtx(_BaseSearchClanContext):

    def __init__(self, offset, limit, getTotalCount = False, fields = None, waitingID = ''):
        super(GetRecommendedClansCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.GET_RECOMMENDED_CLANS


@ReprInjector.withParent(('getSearchCriteria', 'pattern'))

class SearchClansCtx(_BaseSearchClanContext):

    def __init__(self, searchCriteria, offset, limit, getTotalCount = False, fields = None, waitingID = ''):
        super(SearchClansCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__searchCriteria = searchCriteria

    def getSearchCriteria(self):
        return self.__searchCriteria

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.SEARCH_CLANS


@ReprInjector.withParent(('getClanDbID', 'clanDbID'), ('getStatuses', 'statuses'))

class ClanApplicationsCtx(PaginatorCtx):

    def __init__(self, clanDbID, offset, limit, statuses = None, getTotalCount = False, fields = None, waitingID = ''):
        super(ClanApplicationsCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__clanDbID = clanDbID
        self.__statuses = statuses

    def getClanDbID(self):
        return self.__clanDbID

    def getStatuses(self):
        return self.__statuses

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_APPLICATIONS

    def getDataObj(self, incomeData):
        data = super(ClanApplicationsCtx, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanInviteData, item) for item in data ]

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getClanDbID', 'clanDbID'), ('getStatuses', 'statuses'))

class ClanInvitesCtx(PaginatorCtx):

    def __init__(self, clanDbID, offset, limit, statuses = None, getTotalCount = False, fields = None, waitingID = ''):
        super(ClanInvitesCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__clanDbID = clanDbID
        self.__statuses = statuses

    def getClanDbID(self):
        return self.__clanDbID

    def getStatuses(self):
        return self.__statuses

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CLAN_INVITES

    def getDataObj(self, incomeData):
        data = super(ClanInvitesCtx, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanInviteData, item) for item in data ]

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getAccountDbID', 'accountDbID'), ('getStatuses', 'statuses'))

class AccountInvitesCtx(PaginatorCtx):

    def __init__(self, accountDbID, offset, limit, statuses = None, getTotalCount = False, fields = None, waitingID = ''):
        super(AccountInvitesCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__accountDbID = accountDbID
        self.__statuses = statuses

    def getAccountDbID(self):
        return self.__accountDbID

    def getStatuses(self):
        return self.__statuses

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.ACCOUNT_INVITES

    def getDataObj(self, incomeData):
        data = super(AccountInvitesCtx, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanInviteData, item) for item in data ]

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getAccountDbID', 'accountDbID'), ('getStatuses', 'statuses'))

class AccountApplicationsCtx(PaginatorCtx):

    def __init__(self, accountDbID, offset, limit, statuses = None, getTotalCount = False, fields = None, waitingID = ''):
        super(AccountApplicationsCtx, self).__init__(offset, limit, getTotalCount, fields, waitingID)
        self.__accountDbID = accountDbID
        self.__statuses = statuses

    def getAccountDbID(self):
        return self.__accountDbID

    def getStatuses(self):
        return self.__statuses

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.GET_ACCOUNT_APPLICATIONS

    def getDataObj(self, incomeData):
        data = super(AccountApplicationsCtx, self).getDataObj(incomeData)
        return [ makeTupleByDict(items.ClanInviteData, item) for item in data ]

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getApplicationDbID', 'applicationDbID'))

class AcceptApplicationCtx(CommonClanRequestCtx):

    def __init__(self, appDbID, waitingID = ''):
        super(AcceptApplicationCtx, self).__init__(waitingID)
        self.__appDbID = appDbID

    def getApplicationDbID(self):
        return self.__appDbID

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.ACCEPT_APPLICATION

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanADInviteData, incomeData)

    def getDefDataObj(self):
        return items.ClanADInviteData()

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getInviteDbID', 'inviteDbID'))

class AcceptInviteCtx(CommonClanRequestCtx):

    def __init__(self, inviteDbID, waitingID = ''):
        super(AcceptInviteCtx, self).__init__(waitingID)
        self.__inviteDbID = inviteDbID

    def getInviteDbID(self):
        return self.__inviteDbID

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.ACCEPT_INVITE

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanADInviteData, incomeData)

    def getDefDataObj(self):
        return items.ClanADInviteData()

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getClanDbIDs', 'clanDbIDs'), ('getComment', 'comment'))

class CreateApplicationCtx(CommonClanRequestCtx):

    def __init__(self, clanDbIDs, comment = '', waitingID = ''):
        super(CreateApplicationCtx, self).__init__(waitingID)
        self.__clanDbIDs = clanDbIDs
        self.__comment = comment

    def getClanDbIDs(self):
        return self.__clanDbIDs

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.CREATE_APPLICATIONS

    def getDataObj(self, incomeData):
        data = incomeData or []
        return [ makeTupleByDict(items.ClanCreateInviteData, item) for item in data ]

    def getDefDataObj(self):
        return list()

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getClanDbID', 'clanDbID'), ('getAccountDbIDs', 'accountDbIDs'), ('getComment', 'comment'))

class CreateInviteCtx(CommonClanRequestCtx):

    def __init__(self, clanDbID, accountDbIDs, comment = '', waitingID = ''):
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
        return CLAN_REQUESTED_DATA_TYPE.CREATE_INVITES

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

class DeclineApplicationCtx(CommonClanRequestCtx):

    def __init__(self, appDbID, waitingID = ''):
        super(DeclineApplicationCtx, self).__init__(waitingID)
        self.__appDbID = appDbID

    def getApplicationDbID(self):
        return self.__appDbID

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.DECLINE_APPLICATION

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanADInviteData, incomeData)

    def getDefDataObj(self):
        return items.ClanADInviteData()

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getInviteDbID', 'inviteDbID'))

class DeclineInviteCtx(CommonClanRequestCtx):

    def __init__(self, inviteDbID, waitingID = ''):
        super(DeclineInviteCtx, self).__init__(waitingID)
        self.__inviteDbID = inviteDbID

    def getInviteDbID(self):
        return self.__inviteDbID

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITE

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanADInviteData, incomeData)

    def getDefDataObj(self):
        return items.ClanADInviteData()

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent(('getInviteDbIDs', 'inviteDbIDs'))

class DeclineInvitesCtx(CommonClanRequestCtx):

    def __init__(self, inviteDbIDs, waitingID = ''):
        super(DeclineInvitesCtx, self).__init__(waitingID)
        self.__inviteDbIDs = inviteDbIDs

    def getInviteDbIDs(self):
        return self.__inviteDbIDs

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITES

    def getDataObj(self, incomeData):
        incomeData = incomeData or []
        return [ makeTupleByDict(items.ClanADInviteData, item) for item in incomeData ]

    def getDefDataObj(self):
        return []

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()

class GetAccountInvitesCount(AccountInvitesCtx):

    def __init__(self, accountDbID, statuses = None, waitingID = ''):
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


@ReprInjector.withParent()

class GetAccountAppsCount(AccountApplicationsCtx):

    def __init__(self, accountDbID, statuses = None, waitingID = ''):
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

class GetClanInvitesCount(ClanInvitesCtx):

    def __init__(self, clanDbID, statuses = None, waitingID = ''):
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

class GetClanAppsCount(ClanApplicationsCtx):

    def __init__(self, clanDbID, isCaching, statuses = None, waitingID = ''):
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

class PingCtx(CommonClanRequestCtx):

    def __init__(self, waitingID = ''):
        super(PingCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return CLAN_REQUESTED_DATA_TYPE.PING

    def getDataObj(self, incomeData):
        return incomeData

    def getDefDataObj(self):
        return None

    def isCaching(self):
        return False

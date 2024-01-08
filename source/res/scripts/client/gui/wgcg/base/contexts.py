# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/base/contexts.py
from gui.clans import items
from gui.clans.settings import DEFAULT_COOLDOWN
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx
from gui.wgcg.settings import WebRequestDataType
from helpers import dependency
from shared_utils import makeTupleByDict
from skeletons.gui.shared import IItemsCache

@ReprInjector.withParent()
class CommonWebRequestCtx(RequestCtx):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, waitingID=''):
        super(CommonWebRequestCtx, self).__init__(waitingID=waitingID)

    def getCooldown(self):
        return DEFAULT_COOLDOWN

    def isCaching(self):
        return True

    def isAuthorizationRequired(self):
        return False

    def getFields(self):
        return None

    def isClanSyncRequired(self):
        return True

    def getDataObj(self, incomeData):
        return incomeData

    def getDefDataObj(self):
        return None

    def _getOwnClanDbID(self):
        return self.itemsCache.items.stats.clanDBID


@ReprInjector.withParent(('getTokenID', 'token'), ('getUserDatabaseID', 'dbID'), ('isJwt', 'jwt'))
class LogInCtx(CommonWebRequestCtx):

    def __init__(self, databaseID, tokenID, isJwt):
        super(LogInCtx, self).__init__()
        self.__tokenID = tokenID
        self.__databaseID = databaseID
        self.__isJwt = isJwt

    def getTokenID(self):
        return self.__tokenID

    def getUserDatabaseID(self):
        return self.__databaseID

    def isJwt(self):
        return self.__isJwt

    def getRequestType(self):
        return WebRequestDataType.LOGIN


@ReprInjector.withParent()
class LogOutCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.LOGOUT


@ReprInjector.withParent(('getClanDbIDs', 'clanDbIDs'), ('getComment', 'comment'))
class CreateApplicationCtx(CommonWebRequestCtx):

    def __init__(self, clanDbIDs, comment='', waitingID=''):
        super(CreateApplicationCtx, self).__init__(waitingID)
        self.__clanDbIDs = clanDbIDs
        self.__comment = comment

    def getClanDbIDs(self):
        return self.__clanDbIDs

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return WebRequestDataType.CREATE_APPLICATIONS

    def getDataObj(self, incomeData):
        data = incomeData or []
        return [ makeTupleByDict(items.ClanCreateInviteData, item) for item in data ]

    def getDefDataObj(self):
        return list()

    def isAuthorizationRequired(self):
        return True


@ReprInjector.withParent()
class PingCtx(CommonWebRequestCtx):

    def __init__(self, waitingID=''):
        super(PingCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.PING

    def isCaching(self):
        return False


@ReprInjector.withParent(('getAccountsIDs', 'ids'))
class AccountsInfoBaseCtx(CommonWebRequestCtx):

    def __init__(self, accIDs, waitingID=''):
        super(AccountsInfoBaseCtx, self).__init__(waitingID)
        self.__accountsIDs = accIDs

    def getAccountsIDs(self):
        return self.__accountsIDs


@ReprInjector.withParent(('getOffset', 'offset'), ('getLimit', 'limit'), ('isGetTotalCount', 'isGetTotalCount'), ('getFields', 'fields'))
class PaginatorCtx(CommonWebRequestCtx):

    def __init__(self, offset, limit, getTotalCount=False, fields=None, waitingID=''):
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
        return incomeData.get('total', None) if incomeData else None

    def getDataObj(self, incomeData):
        data = incomeData.get('items', self.getDefDataObj()) if incomeData else self.getDefDataObj()
        return data

    def getDefDataObj(self):
        return list()


@ReprInjector.withParent(('getID', 'id'))
class TotalInfoCtx(CommonWebRequestCtx):

    def __init__(self, itemID, waitingID=''):
        super(TotalInfoCtx, self).__init__(waitingID)
        self.__itemID = itemID

    def getID(self):
        return self.__itemID

    def getDataObj(self, incomeData):
        return incomeData['total'] if incomeData else self.getDefDataObj()

    def getDefDataObj(self):
        pass

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/macroses.py
import base64
from urllib import quote_plus
import BigWorld
import constants
from adisp import async, process
from helpers import getClientLanguage, dependency
from helpers.http.url_formatters import addParamsToUrlQuery
from skeletons.gui.web import IWebController
from skeletons.connection_mgr import IConnectionManager

def getLanguageCode(args=None):
    code = getClientLanguage()
    return code.replace('_', '-')


@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def getAreaID(args=None, connectionMgr=None):
    if connectionMgr is not None:
        areaID = connectionMgr.areaID
    else:
        areaID = None
    if areaID:
        result = str(areaID)
    else:
        result = 'errorArea'
    return result


@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def getEncodedLogin(args=None, connectionMgr=None):
    if connectionMgr is not None:
        login = connectionMgr.loginName
    else:
        login = None
    if login:
        result = login
    else:
        result = 'errorLogin'
    return base64.b64encode(result)


@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def getQuotedLogin(args=None, connectionMgr=None):
    if connectionMgr is not None:
        login = connectionMgr.lastLoginName
    else:
        login = None
    if login:
        result = quote_plus(login)
    else:
        result = ''
    return result


@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def getDatabaseID(args=None, connectionMgr=None):
    if connectionMgr is not None:
        dbID = connectionMgr.databaseID
    else:
        dbID = None
    if dbID:
        result = str(dbID)
    else:
        result = 'errorID'
    return result


@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def getPeripheryID(args=None, connectionMgr=None):
    return str(connectionMgr.peripheryID) if connectionMgr is not None else '0'


def getUnitServerID(args=None):
    try:
        unitID = str(BigWorld.player().unitMgr.id)
    except AttributeError:
        unitID = ''

    return unitID


def getAuthRealm(args=None):
    return constants.AUTH_REALM


def getCurrentRealm(args=None):
    return constants.CURRENT_REALM


def getClanDBID(args=None):
    clansCtrl = dependency.instance(IWebController)
    return str(clansCtrl.getClanDbID())


def getSyncMacroses():
    return {'LANGUAGE_CODE': getLanguageCode,
     'AREA_ID': getAreaID,
     'ENCODED_LOGIN': getEncodedLogin,
     'QUOTED_LOGIN': getQuotedLogin,
     'DB_ID': getDatabaseID,
     'PERIPHERY_ID': getPeripheryID,
     'AUTH_REALM': getAuthRealm,
     'UNIT_SERVER_ID': getUnitServerID,
     'CLAN_DBID': getClanDBID,
     'CURRENT_REALM': getCurrentRealm}


@async
def getWgniToken(proxy, args, params, callback):

    def _cbWrapper(response):
        if response and response.isValid():
            callback(str(response.getToken()))
        else:
            callback('')

    from gui.shared.utils.requesters import getTokenRequester
    tokenRqs = getTokenRequester(constants.TOKEN_TYPE.WGNI)
    if not tokenRqs.isInProcess():
        tokenRqs.request(timeout=10.0)(_cbWrapper)
    else:
        _cbWrapper(response=None)
    return


@async
@process
def getTargetURL(proxy, args, params, callback):
    result = args or ''
    if result:
        url = yield proxy.parse(result, params)
        result = quote_plus(url)
    callback(result)


@async
@process
def getUrlParams(proxy, args, params, callback):
    result = args or ''
    params = params or {}
    if result:
        url = yield proxy.parse(result, params)
        result = addParamsToUrlQuery(url, params)
    callback(result)


def getAsyncMacroses():
    return {'WGNI_TOKEN': getWgniToken,
     'TARGET_URL': getTargetURL,
     'PARAMS': getUrlParams}

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/macroses.py
import BigWorld
import base64
from urllib import quote_plus
import constants
from adisp import async, process
from helpers import getClientLanguage, dependency
from helpers.http.url_formatters import addParamsToUrlQuery
from skeletons.gui.clans import IClanController
from skeletons.connection_mgr import IConnectionManager

def getLanguageCode(args=None):
    """
    Gets client language code. Macros is $LANGUAGE_CODE.
    @return: string containing language code (2-5 chars). Note: replaces "_"
    to "-" if code has format xx_xx.
    """
    code = getClientLanguage()
    return code.replace('_', '-')


@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def getAreaID(args=None, connectionMgr=None):
    """
    Gets area ID. It used in china. Macros is $AREA_ID.
    @return: string containing area ID.
    """
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
    """
    Gets encoded name of login. Macros is $ENCODED_LOGIN.
    @return: string containing encoded name of login.
    """
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
    """
    Gets quoted name of login. Macros is $QUOTED_LOGIN.
    @return: string containing quoted name of login.
    """
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
    """
    Gets DB ID. It used in china. Macros is $DB_ID.
    @return: string containing DB ID.
    """
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
    """
    Gets periphery ID. Macros is $PERIPHERY_ID.
    @return: string containing periphery ID.
    """
    return str(connectionMgr.peripheryID) if connectionMgr is not None else '0'


def getUnitServerID(args=None):
    """
    Gets UnitMrg ID. Macros is UNIT_SERVER_ID.
    @return: string containing UnitMrg ID.
    """
    try:
        unitID = str(BigWorld.player().unitMgr.id)
    except AttributeError:
        unitID = ''

    return unitID


def getAuthRealm(args=None):
    return constants.AUTH_REALM


def getClanDBID(args=None):
    """
    Gets player's clan database ID. Macros is CLAN_DBID.
    @return: string containing player's clan database ID.
    """
    clansCtrl = dependency.instance(IClanController)
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
     'CLAN_DBID': getClanDBID}


@async
def getWgniToken(proxy, args, params, callback):
    """
    Gets WGNI login token. Macros is $WGNI_TOKEN.
    @return: string containing WGNI token
    """

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
    """
    Gets target URL, that sets manual. Macros is $TARGET_URL.
    trying to get target url from given args
    or take it from stored attribute
    @return: string containing quoted target URL.
    """
    result = args or ''
    if result:
        url = yield proxy.parse(result, params)
        result = quote_plus(url)
    callback(result)


@async
@process
def getUrlParams(proxy, args, params, callback):
    """
    Gets url GET parameters from external params dict.
    @return: url-encoded params.
    """
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

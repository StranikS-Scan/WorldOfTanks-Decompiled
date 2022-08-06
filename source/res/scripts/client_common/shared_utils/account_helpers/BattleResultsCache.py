# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/account_helpers/BattleResultsCache.py
import os
import cPickle
import zlib
import base64
from functools import partial
import BigWorld
import AccountCommands
from battle_results_shared import VehicleInteractionDetails
from battle_results import unpackClientBattleResults
from debug_utils import LOG_CURRENT_EXCEPTION
import constants
from external_strings_utils import unicode_from_utf8
BATTLE_RESULTS_VERSION = 1
CACHE_DIR = os.path.join(os.path.dirname(unicode_from_utf8(BigWorld.wg_getPreferencesFilePath() if not constants.IS_BOT else '.')[1]), 'battle_results')

class BattleResultsCache(object):

    def __init__(self):
        self.__account = None
        self.__ignore = True
        self.__waiting = False
        clean()
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False
        self.__waiting = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def get(self, arenaUniqueID, callback):
        errorCode, results = self.__checkErrorsAndGetFromCache(arenaUniqueID, self.__account.name)
        if errorCode is not None:
            if callback is not None:
                callback(errorCode, results)
            return
        else:
            self.__waiting = True
            proxy = partial(self.__onGetResponse, callback, None)
            self.__account._doCmdInt3(AccountCommands.CMD_REQ_BATTLE_RESULTS, arenaUniqueID, 0, 0, proxy)
            return

    def getOther(self, arenaUniqueID, resultsSubUrl, callback):
        errorCode, results = self.__checkErrorsAndGetFromCache(arenaUniqueID, resultsSubUrl)
        if errorCode is not None:
            if callback is not None:
                callback(errorCode, results)
            return
        else:
            raise NotImplementedError
            return

    def __checkErrorsAndGetFromCache(self, arenaUniqueID, uniqueFolderName):
        if self.__ignore:
            return (AccountCommands.RES_NON_PLAYER, None)
        elif self.__waiting:
            return (AccountCommands.RES_COOLDOWN, None)
        else:
            battleResults = load(uniqueFolderName, arenaUniqueID)
            return (AccountCommands.RES_CACHE, convertToFullForm(battleResults)) if battleResults is not None else (None, None)

    def __onGetResponse(self, callback, resultsSubUrl, requestID, resultID, errorStr, ext=None):
        if resultID != AccountCommands.RES_STREAM:
            self.__waiting = False
            if callback is not None:
                callback(resultID, None)
            return
        else:
            self.__account._subscribeForStream(requestID, partial(self.__onStreamComplete, callback, resultsSubUrl))
            return

    def __onStreamComplete(self, callback, resultsSubUrl, isSuccess, data):
        self.__waiting = False
        try:
            isSelfResults = resultsSubUrl is None
            battleResults = cPickle.loads(zlib.decompress(data))
            folderName = self.__account.name if isSelfResults else resultsSubUrl
            save(folderName, battleResults)
            if callback is not None:
                callback(AccountCommands.RES_STREAM, convertToFullForm(battleResults))
            if isSelfResults:
                self.__account.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_BATTLE_RESULTS_RECEIVED, battleResults[0], 0, 0)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            if callback is not None:
                callback(AccountCommands.RES_FAILURE, None)

        return


def save(accountName, battleResults):
    fileHandler = None
    try:
        arenaUniqueID = battleResults[0]
        folderName = getFolderName(accountName, arenaUniqueID)
        if not os.path.isdir(folderName):
            os.makedirs(folderName)
        fileName = os.path.join(folderName, '%s.dat' % arenaUniqueID)
        fileHandler = open(fileName, 'wb')
        cPickle.dump((BATTLE_RESULTS_VERSION, battleResults), fileHandler, -1)
    except Exception:
        LOG_CURRENT_EXCEPTION()

    if fileHandler is not None:
        fileHandler.close()
    return


def load(uniqueFolderName, arenaUniqueID):
    fileHandler = None
    try:
        fileName = os.path.join(getFolderName(uniqueFolderName, arenaUniqueID), '%s.dat' % arenaUniqueID)
        if not os.path.isfile(fileName):
            return
        fileHandler = open(fileName, 'rb')
        version, battleResults = cPickle.load(fileHandler)
    except Exception:
        LOG_CURRENT_EXCEPTION()

    if fileHandler is not None:
        fileHandler.close()
    return battleResults if version == BATTLE_RESULTS_VERSION else None


def getFolderName(uniqueFolderName, arenaUniqueID):
    battleStartTime = arenaUniqueID & 4294967295L
    battleStartDay = battleStartTime / 86400
    return os.path.join(CACHE_DIR, base64.b32encode('%s;%s' % (uniqueFolderName, battleStartDay)))


def clean():
    try:
        for root, dirs, files in os.walk(CACHE_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                os.rmdir(os.path.join(root, name))

    except Exception:
        LOG_CURRENT_EXCEPTION()


def convertToFullForm(compactForm):
    arenaUniqueID, avatarResults, vehicleResults, otherResults = compactForm
    vehicleResults = cPickle.loads(zlib.decompress(vehicleResults))
    avatarResults = cPickle.loads(zlib.decompress(avatarResults))
    personal = {}
    fullForm = {'arenaUniqueID': arenaUniqueID,
     'personal': personal,
     'common': {},
     'players': {},
     'vehicles': {},
     'avatars': {}}
    personal['avatar'] = unpackClientBattleResults(avatarResults)
    for vehTypeCompDescr, ownResults in vehicleResults.iteritems():
        vehPersonal = personal[vehTypeCompDescr] = unpackClientBattleResults(ownResults)
        if vehPersonal is None:
            continue
        vehPersonal['details'] = VehicleInteractionDetails.fromPacked(vehPersonal['details']).toDict()

    commonAsList, playersAsList, vehiclesAsList, avatarsAsList = cPickle.loads(zlib.decompress(otherResults))
    fullForm['common'] = unpackClientBattleResults(commonAsList)
    for accountDBID, playerAsList in playersAsList.iteritems():
        fullForm['players'][accountDBID] = unpackClientBattleResults(playerAsList)

    for accountDBID, avatarAsList in avatarsAsList.iteritems():
        fullForm['avatars'][accountDBID] = unpackClientBattleResults(avatarAsList)

    for vehicleID, vehiclesInfo in vehiclesAsList.iteritems():
        fullForm['vehicles'][vehicleID] = []
        for vehTypeCompDescr, vehicleInfo in vehiclesInfo.iteritems():
            fullForm['vehicles'][vehicleID].append(unpackClientBattleResults(vehicleInfo))

    return fullForm

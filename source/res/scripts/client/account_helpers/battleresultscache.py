# Embedded file name: scripts/client/account_helpers/BattleResultsCache.py
import os
import BigWorld
import cPickle
import AccountCommands
import zlib
import base64
from functools import partial
from battle_results_shared import *
from debug_utils import *
BATTLE_RESULTS_VERSION = 1
CACHE_DIR = os.path.join(os.path.dirname(unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')), 'battle_results')

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
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        elif self.__waiting:
            if callback is not None:
                callback(AccountCommands.RES_COOLDOWN, None)
            return
        else:
            battleResults = load(self.__account.name, arenaUniqueID)
            if battleResults is not None:
                if callback is not None:
                    callback(AccountCommands.RES_CACHE, convertToFullForm(battleResults))
                return
            self.__waiting = True
            proxy = partial(self.__onGetResponse, callback)
            self.__account._doCmdInt3(AccountCommands.CMD_REQ_BATTLE_RESULTS, arenaUniqueID, 0, 0, proxy)
            return

    def __onGetResponse(self, callback, requestID, resultID, errorStr, ext = {}):
        if resultID != AccountCommands.RES_STREAM:
            self.__waiting = False
            if callback is not None:
                callback(resultID, None)
            return
        else:
            self.__account._subscribeForStream(requestID, partial(self.__onStreamComplete, callback))
            return

    def __onStreamComplete(self, callback, isSuccess, data):
        self.__waiting = False
        try:
            battleResults = cPickle.loads(zlib.decompress(data))
            save(self.__account.name, battleResults)
            if callback is not None:
                callback(AccountCommands.RES_STREAM, convertToFullForm(battleResults))
            self.__account.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_BATTLE_RESULTS_RECEIVED, battleResults[0], 0, 0)
        except:
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
    except:
        LOG_CURRENT_EXCEPTION()

    if fileHandler is not None:
        fileHandler.close()
    return


def load(accountName, arenaUniqueID):
    fileHandler = None
    try:
        fileName = os.path.join(getFolderName(accountName, arenaUniqueID), '%s.dat' % arenaUniqueID)
        if not os.path.isfile(fileName):
            return
        fileHandler = open(fileName, 'rb')
        version, battleResults = cPickle.load(fileHandler)
    except:
        LOG_CURRENT_EXCEPTION()

    if fileHandler is not None:
        fileHandler.close()
    if version == BATTLE_RESULTS_VERSION:
        return battleResults
    else:
        return


def getFolderName(accountName, arenaUniqueID):
    battleStartTime = arenaUniqueID & 4294967295L
    battleStartDay = battleStartTime / 86400
    return os.path.join(CACHE_DIR, base64.b32encode('%s;%s' % (accountName, battleStartDay)))


def clean():
    try:
        for root, dirs, files in os.walk(CACHE_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                os.rmdir(os.path.join(root, name))

    except:
        LOG_CURRENT_EXCEPTION()


def convertToFullForm(compactForm):
    fullForm = {'arenaUniqueID': compactForm[0],
     'personal': listToDict(VEH_FULL_RESULTS, compactForm[1]),
     'common': {},
     'players': {},
     'vehicles': {}}
    fullForm['personal']['details'] = VehicleInteractionDetails.fromPacked(fullForm['personal']['details']).toDict()
    commonAsList, playersAsList, vehiclesAsList = cPickle.loads(compactForm[2])
    fullForm['common'] = listToDict(COMMON_RESULTS, commonAsList)
    for accountDBID, playerAsList in playersAsList.iteritems():
        fullForm['players'][accountDBID] = listToDict(PLAYER_INFO, playerAsList)

    for vehicleID, vehicleAsList in vehiclesAsList.iteritems():
        fullForm['vehicles'][vehicleID] = listToDict(VEH_PUBLIC_RESULTS, vehicleAsList)

    return fullForm

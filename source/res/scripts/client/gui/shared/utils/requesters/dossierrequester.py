# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/DossierRequester.py
import time
from functools import partial
import BigWorld
import constants
import dossiers2
import AccountCommands
from adisp import adisp_async
from debug_utils import LOG_ERROR
from gui.shared.utils import code2str
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from gui.shared.utils.requesters.common import RequestProcessor
from skeletons.gui.shared.utils.requesters import IDossierRequester

class UserDossier(object):
    __queue = []
    __lastResponseTime = 0
    __request = None

    def __init__(self, databaseID):
        self.__cache = {'databaseID': int(databaseID),
         'account': None,
         'vehicles': {},
         'clan': None,
         'hidden': False,
         'available': True,
         'rating': None,
         'rated7x7Seasons': {},
         'ranked': None}
        return

    def __setLastResponseTime(self):
        self.__lastResponseTime = time.time()

    def __nextRequestTime(self):
        t = constants.REQUEST_COOLDOWN.PLAYER_DOSSIER - (time.time() - self.__lastResponseTime)
        return t if t > 0 else 0

    def __processQueue(self):
        if self.__request is not None:
            return
        elif self.__queue:
            self.__request = RequestProcessor(self.__nextRequestTime(), self.__queue.pop())
            return
        else:
            return

    def __requestPlayerInfo(self, callback):

        def proxyCallback(value):
            if value is not None and len(value) > 1:
                self.__cache['databaseID'] = value[0]
                self.__cache['account'] = dossiers2.getAccountDossierDescr(value[1])
                self.__cache['clan'] = value[2]
                self.__cache['rating'] = value[3]
                self.__cache['rated7x7Seasons'] = seasons = {}
                self.__cache['ranked'] = value[5]
                self.__cache['dogTag'] = value[6]
                self.__cache['battleRoyaleStats'] = value[7]
                self.__cache['wtr'] = value[8]
                self.__cache['layout'] = value[9]
                self.__cache['layoutState'] = value[10]
                for sID, d in (value[4] or {}).iteritems():
                    seasons[sID] = dossiers2.getRated7x7DossierDescr(d)

            callback(self.__cache['account'])
            return

        def callBackMethod(c, code, databaseID, dossier, clanID, clanInfo, gRating, eSportSeasons, ranked, dogTag, br, wtr, layout, layoutState):
            value = (databaseID,
             dossier,
             (clanID, clanInfo),
             gRating,
             eSportSeasons,
             ranked,
             dogTag,
             br,
             wtr,
             layout,
             layoutState)
            self.__processValueResponse(c, code, value)

        self.__queue.append(lambda : BigWorld.player().requestPlayerInfo(self.__cache['databaseID'], partial(callBackMethod, proxyCallback)))
        self.__processQueue()

    def __requestAccountDossier(self, callback):

        def proxyCallback(dossier):
            self.__cache['account'] = dossiers2.getAccountDossierDescr(dossier)
            callback(self.__cache['account'])

        self.__queue.append(lambda : BigWorld.player().requestAccountDossier(self.__cache['databaseID'], partial(self.__processValueResponse, proxyCallback)))
        self.__processQueue()

    def __requestVehicleDossier(self, vehCompDescr, callback):

        def proxyCallback(dossier):
            self.__cache['vehicles'][vehCompDescr] = dossiers2.getVehicleDossierDescr(dossier)
            callback(self.__cache['vehicles'][vehCompDescr])

        self.__queue.append(lambda : BigWorld.player().requestVehicleDossier(self.__cache['databaseID'], vehCompDescr, partial(self.__processValueResponse, proxyCallback)))
        self.__processQueue()

    def __requestClanInfo(self, callback):
        self.__queue.append(lambda : BigWorld.player().requestPlayerClanInfo(self.__cache['databaseID'], partial(lambda c, code, str, clanDBID, clanInfo: self.__processValueResponse(c, code, (clanDBID, clanInfo)), callback)))
        self.__processQueue()

    def __processValueResponse(self, callback, code, value):
        self.__setLastResponseTime()
        self.__request = None
        if code < 0:
            LOG_ERROR('Error while server request (code=%s): %s' % (code, code2str(code)))
            if code == AccountCommands.RES_HIDDEN_DOSSIER:
                self.__cache['hidden'] = True
            elif code == AccountCommands.RES_CENTER_DISCONNECTED:
                self.__cache['available'] = False
            callback('')
        else:
            callback(value)
        self.__processQueue()
        return

    @adisp_async
    def getAccountDossier(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('account') is None:
            self.__requestPlayerInfo(callback)
            return
        else:
            callback(self.__cache['account'])
            return

    @adisp_async
    def getClanInfo(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('clan') is None:
            self.__requestClanInfo(callback)
            return
        else:
            callback(self.__cache['clan'])
            return

    @adisp_async
    def getRated7x7Seasons(self, callback):
        if not self.isValid:
            callback({})
        if self.__cache.get('rated7x7Seasons') is None:
            self.__requestPlayerInfo(lambda accDossier: callback(self.__cache['rated7x7Seasons']))
            return
        else:
            callback(self.__cache['rated7x7Seasons'])
            return

    @adisp_async
    def getRankedInfo(self, callback):
        if not self.isValid:
            callback({})
        if self.__cache.get('ranked') is None:
            self.__requestPlayerInfo(lambda accDossier: callback(self.__cache['ranked']))
            return
        else:
            callback(self.__cache['ranked'])
            return

    @adisp_async
    def getGlobalRating(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('rating') is None:
            self.__requestPlayerInfo(lambda accDossier: callback(self.__cache['rating']))
            return
        else:
            callback(self.__cache['rating'])
            return

    @adisp_async
    def getVehicleDossier(self, vehCompDescr, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('vehicles', {}).get(vehCompDescr, None) is None:
            self.__requestVehicleDossier(vehCompDescr, callback)
            return
        else:
            callback(self.__cache['vehicles'][vehCompDescr])
            return

    @adisp_async
    def getDogTag(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('dogTag') is None:
            self.__requestPlayerInfo(callback)
            return
        else:
            callback(self.__cache['dogTag'])
            return

    @adisp_async
    def getBattleRoyaleStats(self, callback):
        if not self.isValid:
            callback({})
        if self.__cache.get('battleRoyaleStats') is None:
            self.__requestPlayerInfo(lambda accDossier: callback(self.__cache['battleRoyaleStats']))
            return
        else:
            callback(self.__cache['battleRoyaleStats'])
            return

    @adisp_async
    def getWTR(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('wtr') is None:
            self.__requestPlayerInfo(callback)
            return
        else:
            callback(self.__cache['wtr'])
            return

    @adisp_async
    def getLayout(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('layout') is None:
            self.__requestPlayerInfo(callback)
            return
        else:
            callback(self.__cache['layout'])
            return

    @adisp_async
    def getLayoutState(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('layoutState') is None:
            self.__requestPlayerInfo(callback)
            return
        else:
            callback(self.__cache['layoutState'])
            return

    @property
    def isHidden(self):
        return self.__cache.get('hidden', False)

    @property
    def isAvailable(self):
        return self.__cache.get('available', False)

    @property
    def isValid(self):
        return not self.isHidden and self.isAvailable


class DossierRequester(AbstractSyncDataRequester, IDossierRequester):

    def __init__(self):
        super(DossierRequester, self).__init__()
        self.__users = {}

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().dossierCache.getCache(lambda resID, value: self._response(resID, value, callback))

    def getVehicleDossier(self, vehTypeCompDescr):
        return self.getCacheValue((constants.DOSSIER_TYPE.VEHICLE, vehTypeCompDescr), (0, ''))[1]

    def getVehDossiersIterator(self):
        for (dossierType, vehIntCD), records in self._data.iteritems():
            if dossierType == constants.DOSSIER_TYPE.VEHICLE:
                yield (vehIntCD, records[1])

    def getUserDossierRequester(self, databaseID):
        databaseID = int(databaseID)
        return self.__users.setdefault(databaseID, UserDossier(databaseID))

    def closeUserDossier(self, databaseID):
        if databaseID in self.__users:
            del self.__users[databaseID]

    def onCenterIsLongDisconnected(self, isLongDisconnected):
        if isLongDisconnected:
            return
        self.__users = dict((item for item in self.__users.iteritems() if item[1].isAvailable))

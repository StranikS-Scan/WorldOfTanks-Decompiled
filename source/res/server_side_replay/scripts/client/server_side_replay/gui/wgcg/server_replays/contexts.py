# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/wgcg/server_replays/contexts.py
from typing import Dict, List
import base64
from gui.wgcg.base.contexts import CommonWebRequestCtx
from server_side_replay.gui.wgcg.data_wrappers import server_replays
from server_side_replay.gui.wgcg.requests import SERVER_SIDE_REPLAY_REQUEST_TYPE

def makeTupleByDict(ntClass, data):
    unsupportedFields = set(data) - set(ntClass._fields)
    supported = {}
    fieldTypes = getattr(ntClass, '_field_types', None)
    for k, v in data.iteritems():
        if k not in unsupportedFields:
            if fieldTypes and v is None:
                try:
                    supported[k] = fieldTypes[k]()
                    continue
                except:
                    pass

            supported[k] = v

    return ntClass(**supported)


class JwtWebRequestCtx(CommonWebRequestCtx):

    def __init__(self):
        super(JwtWebRequestCtx, self).__init__()
        self.jwtToken = None
        return


class BestReplaysCtx(JwtWebRequestCtx):

    def __init__(self, account_id=None, vehicleCDs=None, sortBy=None, nation=None, vehicleLevel=None, vehicleType=None, fromDate=None, isPrimeTime=None):
        super(BestReplaysCtx, self).__init__()
        self.__accountId = account_id
        self.__vehicleCDs = vehicleCDs
        self.__nation = nation
        self.__vehicleLevel = vehicleLevel
        self.__vehicleType = vehicleType
        self.__fromDate = fromDate
        self.__isPrimeTime = isPrimeTime
        self.__sortBy = sortBy

    def getRequestType(self):
        return SERVER_SIDE_REPLAY_REQUEST_TYPE.GET_BEST_REPLAYS

    def getRequestKwargs(self):
        result = {}
        if self.__vehicleCDs:
            result['vehicle_cd'] = self.__vehicleCDs
        if self.__nation:
            result['nation'] = self.__nation
        if self.__vehicleLevel:
            result['vehicle_level'] = self.__vehicleLevel
        if self.__vehicleType:
            result['vehicle_type'] = self.__vehicleType
        if self.__sortBy:
            result['sort_by'] = self.__sortBy
        if self.__accountId:
            result['account_id'] = self.__accountId
        if self.__fromDate is not None:
            result['from_date'] = self.__fromDate
        if self.__isPrimeTime is not None:
            result['is_prime_time'] = self.__isPrimeTime
        return result

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        rankings = []
        incomeRankings = incomeData.get('rankings', [])
        for rawReplay in sorted(incomeRankings, key=lambda r: r.get('rank')):
            rankings.append(makeTupleByDict(server_replays.ShortReplay, rawReplay))

        incomeData['rankings'] = rankings
        return makeTupleByDict(server_replays.PageReplays, incomeData)


class TopReplaysCtx(JwtWebRequestCtx):

    def getRequestType(self):
        return SERVER_SIDE_REPLAY_REQUEST_TYPE.GET_TOP_REPLAYS

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        incomeData = {k:makeTupleByDict(server_replays.ShortReplay, v) for k, v in incomeData.items()}
        return makeTupleByDict(server_replays.TopReplays, incomeData)


class ReplayLinkCtx(JwtWebRequestCtx):

    def __init__(self, replayID=None):
        super(ReplayLinkCtx, self).__init__()
        self.__replayID = replayID

    def getReplayID(self):
        return self.__replayID

    def getRequestType(self):
        return SERVER_SIDE_REPLAY_REQUEST_TYPE.GET_REPLAY_LINK

    def getDataObj(self, incomeData):
        return makeTupleByDict(server_replays.ReplayLink, incomeData or {})


class FindReplayCtx(JwtWebRequestCtx):

    def __init__(self, replayName):
        super(FindReplayCtx, self).__init__()
        self.__replayName = replayName

    def getReplayName(self):
        return base64.b64encode(str(self.__replayName))

    def getRequestType(self):
        return SERVER_SIDE_REPLAY_REQUEST_TYPE.POST_FIND_REPLAY

    def getDataObj(self, incomeData):
        return makeTupleByDict(server_replays.ReplayLink, incomeData or {})

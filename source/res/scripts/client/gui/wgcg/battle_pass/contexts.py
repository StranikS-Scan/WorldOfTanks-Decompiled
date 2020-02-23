# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/battle_pass/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class BattlePassGetVideoDataCtx(CommonWebRequestCtx):

    def __init__(self, seasonID, level, hasBP, voteID, **kwargs):
        super(BattlePassGetVideoDataCtx, self).__init__(**kwargs)
        self.__seasonID = seasonID
        self.__level = level
        self.__hasBP = hasBP
        self.__voteID = voteID

    def getSeasonID(self):
        return self.__seasonID

    def getLevel(self):
        return self.__level

    def getHasBP(self):
        return self.__hasBP

    def getVoteID(self):
        return self.__voteID

    def getRequestType(self):
        return WebRequestDataType.BATTLE_PASS_GET_VIDEO_DATA

    @staticmethod
    def getDataObj(incomeData):
        data = incomeData or []
        result = {}
        for videoIdx, videoObj in enumerate(data.get('extras_video')):
            video = videoObj.get('video')
            videoID = video.get('id')
            video['idx'] = videoIdx
            result[videoID] = video

        return result

    def isClanSyncRequired(self):
        return False


class BattlePassGetVotingDataCtx(CommonWebRequestCtx):

    def __init__(self, season, **kwargs):
        super(BattlePassGetVotingDataCtx, self).__init__(**kwargs)
        self.__featureID = 'battle_pass'
        self.__season = season

    def getSeason(self):
        return self.__season

    def getFeatureID(self):
        return self.__featureID

    def getRequestType(self):
        return WebRequestDataType.BATTLE_PASS_GET_VOTING_DATA

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getDataObj(self, incomeData):
        data = incomeData or []
        result = {}
        for option in data.get('data', []):
            if option.get('major_key') != self.__featureID:
                return {}
            if option.get('season_id') != self.__season:
                continue
            result[option.get('option_id')] = option.get('count')

        return result

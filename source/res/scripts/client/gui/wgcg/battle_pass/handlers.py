# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/battle_pass/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class BattlePassRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.BATTLE_PASS_GET_VIDEO_DATA: self.__getVideoData,
         WebRequestDataType.BATTLE_PASS_GET_VOTING_DATA: self.__getVotingData}
        return handlers

    def __getVideoData(self, ctx, callback):
        reqCtx = self._requester.doRequestEx(ctx, callback, ('battle_pass', 'get_video_data'), season_id=ctx.getSeasonID(), level=ctx.getLevel(), has_bp=ctx.getHasBP(), vote_id=ctx.getVoteID())
        return reqCtx

    def __getVotingData(self, ctx, callback):
        reqCtx = self._requester.doRequestEx(ctx, callback, ('battle_pass', 'get_voting_data'), feature_id=ctx.getFeatureID(), seasons=ctx.getSeasons())
        return reqCtx

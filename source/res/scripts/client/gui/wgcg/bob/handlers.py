# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/bob/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class BobRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.BOB_GET_TEAMS: self.__getTeams,
         WebRequestDataType.BOB_GET_TEAM_SKILLS: self.__getTeamSkills}
        return handlers

    def __getTeams(self, ctx, callback):
        reqCtx = self._requester.doRequestEx(ctx, callback, ('wgbob', 'get_teams'))
        return reqCtx

    def __getTeamSkills(self, ctx, callback):
        reqCtx = self._requester.doRequestEx(ctx, callback, ('wgbob', 'get_team_skills'), timestamp=ctx.getTimestamp())
        return reqCtx

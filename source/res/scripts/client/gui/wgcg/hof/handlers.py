# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/hof/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class HofRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.HOF_USER_INFO: self.__hofUserInfo,
         WebRequestDataType.HOF_USER_EXCLUDE: self.__hofUserExclude,
         WebRequestDataType.HOF_USER_RESTORE: self.__hofUserRestore}
        return handlers

    def __hofUserInfo(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('wgrms', 'hof_user_info'))

    def __hofUserExclude(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('wgrms', 'hof_user_exclude'))

    def __hofUserRestore(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('wgrms', 'hof_user_restore'))

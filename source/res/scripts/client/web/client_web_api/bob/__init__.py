# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/bob/__init__.py
from skeletons.gui.game_control import IBobController
from web.client_web_api.api import C2WHandler, c2w
from helpers import dependency

class BobTokensUpdateHandler(C2WHandler):
    __bobController = dependency.descriptor(IBobController)

    def init(self):
        super(BobTokensUpdateHandler, self).init()
        self.__bobController.onTokensUpdated += self.__sendUpdate
        self.__trigger = False

    def fini(self):
        self.__bobController.onTokensUpdated -= self.__sendUpdate
        super(BobTokensUpdateHandler, self).fini()

    @c2w(name='token_list_update')
    def __sendUpdate(self):
        self.__trigger = not self.__trigger
        return self.__trigger


class BobTeamsUpdateHandler(C2WHandler):
    __bobController = dependency.descriptor(IBobController)

    def init(self):
        super(BobTeamsUpdateHandler, self).init()
        self.__bobController.teamsRequester.onRecalculationUpdated += self.__sendUpdate

    def fini(self):
        self.__bobController.teamsRequester.onRecalculationUpdated -= self.__sendUpdate
        super(BobTeamsUpdateHandler, self).fini()

    @c2w(name='wgbob_coefficients_update')
    def __sendUpdate(self):
        return self.__bobController.teamsRequester.getTeamsAsJson()

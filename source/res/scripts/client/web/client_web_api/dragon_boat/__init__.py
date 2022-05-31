# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/dragon_boat/__init__.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_control.dragon_boat_controller import DBOAT_QUEST_SELECTED
from helpers import dependency
from skeletons.gui.game_control import IDragonBoatController
from web.client_web_api.api import C2WHandler, c2w

class DragonBoatEventHandler(C2WHandler):
    __slots__ = ('__allowedTokens',)
    dragonBoatCtrl = dependency.descriptor(IDragonBoatController)

    def init(self):
        super(DragonBoatEventHandler, self).init()
        self.__updateAllowedTokens()
        self.dragonBoatCtrl.onSettingsChanged += self.__updateAllowedTokens
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        self.dragonBoatCtrl.onSettingsChanged -= self.__updateAllowedTokens
        super(DragonBoatEventHandler, self).fini()

    def __updateAllowedTokens(self):
        self.__allowedTokens = {DBOAT_QUEST_SELECTED}
        self.__allowedTokens.update(self.dragonBoatCtrl.getConfig().dragonBoatTokens.get('dailyBattleMissions', []))

    def __onTokensUpdate(self, diff):
        tokens = list(self.__allowedTokens.intersection(diff.keys()))
        if tokens:
            self.__sendTokens(tokens)

    @c2w(name='dboat_tokens_update')
    def __sendTokens(self, tokens):
        return tokens

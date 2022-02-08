# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/battle_pass/__init__.py
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.game_control import IBattlePassController
from web.client_web_api.api import C2WHandler, c2w
from web.common import formatBattlePassInfo

class BattlePassEventHandler(C2WHandler, EventsHandler):
    __battlePass = dependency.descriptor(IBattlePassController)

    def init(self):
        super(BattlePassEventHandler, self).init()
        self._subscribe()

    def fini(self):
        self._unsubscribe()
        super(BattlePassEventHandler, self).fini()

    def _getEvents(self):
        return ((self.__battlePass.onBattlePassIsBought, self.__sendInfo),
         (self.__battlePass.onSeasonStateChange, self.__sendInfo),
         (self.__battlePass.onBattlePassSettingsChange, self.__sendInfo),
         (self.__battlePass.onChapterChanged, self.__sendInfo))

    @c2w(name='battle_pass_info_changed')
    def __sendInfo(self, *args, **kwargs):
        return formatBattlePassInfo()

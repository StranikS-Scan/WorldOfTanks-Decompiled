# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/comp7/__init__.py
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.game_control import IComp7Controller
from web.client_web_api.api import C2WHandler, c2w

class Comp7BattleResultEventHandler(C2WHandler, EventsHandler):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def init(self):
        super(Comp7BattleResultEventHandler, self).init()
        self._subscribe()

    def fini(self):
        self._unsubscribe()
        super(Comp7BattleResultEventHandler, self).fini()

    def _getEvents(self):
        return ((self.__comp7Ctrl.onComp7BattleFinished, self.__sendInfo),)

    @c2w(name='comp7_battle_result')
    def __sendInfo(self, *args, **kwargs):
        pass

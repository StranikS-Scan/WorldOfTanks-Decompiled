# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/squad/actions_handler.py
import BigWorld
from adisp import adisp_process
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.random.squad.actions_handler import BalancedSquadActionsHandler
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController, IPlatoonController

class EpicSquadActionsHandler(BalancedSquadActionsHandler):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    @prbDispatcherProperty
    def _prbDispatcher(self):
        return None

    def _onKickedFromQueue(self, *args):
        super(EpicSquadActionsHandler, self)._onKickedFromQueue(*args)
        if not self.__epicController.isEnabled():
            BigWorld.callback(0.0, self._doLeave)

    @adisp_process
    def _doLeave(self):
        yield self._prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

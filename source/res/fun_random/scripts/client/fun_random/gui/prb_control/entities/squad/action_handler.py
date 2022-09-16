# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/squad/action_handler.py
from PlayerEvents import g_playerEvents
from gui.prb_control.entities.random.squad.actions_handler import BalancedSquadActionsHandler
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController, IPlatoonController

class FunRandomSquadActionsHandler(BalancedSquadActionsHandler):
    __funRandomController = dependency.descriptor(IFunRandomController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, entity):
        super(FunRandomSquadActionsHandler, self).__init__(entity)
        g_playerEvents.onDequeued += self.__onDequeued

    def clear(self):
        g_playerEvents.onDequeued -= self.__onDequeued
        super(FunRandomSquadActionsHandler, self).clear()

    def _onKickedFromQueue(self, event):
        super(FunRandomSquadActionsHandler, self)._onKickedFromQueue(event)
        if not self.__funRandomController.isInPrimeTime():
            self.__platoonCtrl.leavePlatoon(ignoreConfirmation=True)

    def __onDequeued(self, _):
        if not self.__funRandomController.isInPrimeTime():
            self.__platoonCtrl.leavePlatoon(ignoreConfirmation=True)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/squad/scheduler.py
from fun_random.gui.feature.util.fun_wrappers import hasSpecifiedSubMode
from fun_random.gui.prb_control.entities.pre_queue.scheduler import FunRandomScheduler
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.game_control import IPlatoonController

class FunRandomSquadScheduler(FunRandomScheduler):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    _FUN_RES_ROOT = R.strings.fun_random.scheduler

    @hasSpecifiedSubMode()
    def notifySubModeSwitching(self, subModeID):
        SystemMessages.pushMessage(backport.text(self._FUN_RES_ROOT.notification.squadModeSwitch(), **self._getMessageParams(subModeID)), messageData={'header': backport.text(self._FUN_RES_ROOT.notification.squadModeSwitch.title())}, type=SystemMessages.SM_TYPE.InformationHeader)

    def _checkControllerLeave(self, controller):
        return not controller.isSquadAvailable()

    def _doLeave(self):
        if not self._entity.getFlags().isInQueue():
            self.__platoonCtrl.leavePlatoon(ignoreConfirmation=True)
        elif self._entity.getPlayerInfo().isCommander():
            self._entity.exitFromQueue()

    def _startListening(self):
        super(FunRandomSquadScheduler, self)._startListening()
        g_playerEvents.onKickedFromQueue += self.__checkLeave
        g_playerEvents.onDequeued += self.__checkLeave

    def _stopListening(self):
        g_playerEvents.onDequeued -= self.__checkLeave
        g_playerEvents.onKickedFromQueue -= self.__checkLeave
        super(FunRandomSquadScheduler, self)._stopListening()

    def __checkLeave(self, *_, **__):
        self._checkLeave()

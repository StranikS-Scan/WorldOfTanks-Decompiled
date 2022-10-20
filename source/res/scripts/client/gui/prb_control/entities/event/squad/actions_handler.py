# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_handler.py
from gui.prb_control.entities.random.squad.actions_handler import BalancedSquadActionsHandler, RandomSquadActionsHandler
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from constants import QUEUE_TYPE_NAMES
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
_R_HW_QUEUE_MESSENGER = R.strings.hw_messenger.queue

class EventBattleSquadActionsHandler(RandomSquadActionsHandler):

    def _checkVehicleAmmo(self):
        return False

    def _onKickedFromQueue(self, _):
        SystemMessages.pushMessage(backport.text(_R_HW_QUEUE_MESSENGER.disabled.dyn(QUEUE_TYPE_NAMES[self._entity.getCurrentQueueType])()), type=SystemMessages.SM_TYPE.Error)


class EventBattleBalancedSquadActionsHandler(BalancedSquadActionsHandler):
    __eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def _checkVehicleAmmo(self):
        return False

    def _onKickedFromQueue(self, queueType):
        if not self.__eventBattlesCtrl.isQueueEnabled(queueType):
            SystemMessages.pushMessage(backport.text(_R_HW_QUEUE_MESSENGER.disabled.dyn(QUEUE_TYPE_NAMES[queueType])()), type=SystemMessages.SM_TYPE.Error)
        else:
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.arena_start_errors.prb.kick.timeout()), type=SystemMessages.SM_TYPE.Error)

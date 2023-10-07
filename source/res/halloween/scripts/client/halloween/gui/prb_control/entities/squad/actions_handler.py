# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/squad/actions_handler.py
from gui.prb_control.entities.random.squad.actions_handler import BalancedSquadActionsHandler, RandomSquadActionsHandler
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from constants import QUEUE_TYPE_NAMES
from helpers import dependency
from skeletons.gui.game_control import IHalloweenController
_R_HW_QUEUE_MESSENGER = R.strings.hw_messenger.queue

class HalloweenBattleSquadActionsHandler(RandomSquadActionsHandler):

    def _checkVehicleAmmo(self):
        return False

    def _onKickedFromQueue(self, _):
        SystemMessages.pushMessage(backport.text(_R_HW_QUEUE_MESSENGER.disabled.dyn(QUEUE_TYPE_NAMES[self._entity.getCurrentQueueType])()), type=SystemMessages.SM_TYPE.Error)


class HalloweenBattleBalancedSquadActionsHandler(BalancedSquadActionsHandler):
    __controller = dependency.descriptor(IHalloweenController)

    def _checkVehicleAmmo(self):
        return False

    def _onKickedFromQueue(self, queueType):
        if not self.__controller.isQueueEnabled(queueType):
            SystemMessages.pushMessage(backport.text(_R_HW_QUEUE_MESSENGER.disabled.dyn(QUEUE_TYPE_NAMES[queueType])()), type=SystemMessages.SM_TYPE.Error)
        else:
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.arena_start_errors.prb.kick.timeout()), type=SystemMessages.SM_TYPE.Error)

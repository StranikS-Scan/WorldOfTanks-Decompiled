# Embedded file name: scripts/client/gui/prb_control/functional/no_prebattle.py
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from CurrentVehicle import g_currentVehicle
from gui.game_control import getFalloutCtrl
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.functional.interfaces import IPrbFunctional, IPreQueueFunctional
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
_PAN = PREBATTLE_ACTION_NAME

class NoPrbFunctional(IPrbFunctional):

    def leave(self, ctx, callback = None):
        LOG_ERROR('NoPrbFunctional.leave was invoke', ctx)
        if callback:
            callback(False)

    def request(self, ctx, callback = None):
        LOG_ERROR('NoPrbFunctional.request was invoke', ctx)
        if callback:
            callback(False)


class NoPreQueueFunctional(IPreQueueFunctional):
    CREATE_QUEUE_BY_ACTION = {_PAN.UNDEFINED: (QUEUE_TYPE.RANDOMS, True),
     _PAN.JOIN_RANDOM_QUEUE: (QUEUE_TYPE.RANDOMS, True),
     _PAN.JOIN_EVENT_BATTLES_QUEUE: (QUEUE_TYPE.EVENT_BATTLES, True)}

    def canPlayerDoAction(self):
        return (True, '')

    def doAction(self, action = None, dispatcher = None):
        result = False
        if action is not None:
            actionName = action.actionName or _PAN.UNDEFINED
            if actionName in (_PAN.JOIN_RANDOM_QUEUE, _PAN.UNDEFINED) and getFalloutCtrl().isSelected():
                actionName = _PAN.JOIN_EVENT_BATTLES_QUEUE
            if actionName in self.CREATE_QUEUE_BY_ACTION:
                queueType, doAction = self.CREATE_QUEUE_BY_ACTION[actionName]
                g_prbCtrlEvents.onPreQueueFunctionalCreated(queueType, doAction, action)
                result = True
        return result

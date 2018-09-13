# Embedded file name: scripts/client/gui/prb_control/functional/not_supported.py
import BigWorld
from constants import PREBATTLE_TYPE_NAMES, QUEUE_TYPE_NAMES
from debug_utils import LOG_ERROR
from gui.prb_control.functional import interfaces
from gui.prb_control.settings import FUNCTIONAL_EXIT, CTRL_ENTITY_TYPE

class NotSupportedEntry(interfaces.IPrbEntry):

    def create(self, ctx, callback = None):
        LOG_ERROR('NotSupportedEntry.create')

    def join(self, ctx, callback = None):
        LOG_ERROR('NotSupportedEntry.join')


class PrbNotSupportedFunctional(interfaces.IPrbFunctional):

    def __init__(self, settings):
        try:
            self._prbTypeName = PREBATTLE_TYPE_NAMES[settings['type']]
        except KeyError:
            self._prbTypeName = 'N/A'

    def init(self, clientPrb = None, ctx = None):
        LOG_ERROR('PrbNotSupportedFunctional.init. Prebattle is not supported', self._prbTypeName)
        return CTRL_ENTITY_TYPE.UNKNOWN

    def fini(self, clientPrb = None, woEvents = False):
        pass

    def canPlayerDoAction(self):
        LOG_ERROR('Actions are disabled. Prebattle is not supported', self._prbTypeName)
        return (True, '')

    def doAction(self, action = None, dispatcher = None):
        LOG_ERROR('Leaves prebattle. Prebattle is not supported', self._prbTypeName)
        BigWorld.player().prb_leave(lambda result: result)
        return True

    def hasGUIPage(self):
        LOG_ERROR('PrbNotSupportedFunctional.showGUI. Prebattle is not supported', self._prbTypeName)
        return False


class QueueNotSupportedFunctional(interfaces.IPreQueueFunctional):

    def __init__(self, queueType):
        super(QueueNotSupportedFunctional, self).__init__()
        try:
            self._queueTypeName = QUEUE_TYPE_NAMES[queueType]
        except KeyError:
            self._queueTypeName = 'N/A'

    def init(self, clientPrb = None, ctx = None):
        LOG_ERROR('QueueNotSupportedFunctional.init. Queue is not supported', self._queueTypeName)
        return CTRL_ENTITY_TYPE.UNKNOWN

    def fini(self, clientPrb = None, woEvents = False):
        pass

    def canPlayerDoAction(self):
        LOG_ERROR('Actions are disabled. Queue is not supported', self._queueTypeName)
        return (True, '')

    def doAction(self, action = None, dispatcher = None):
        LOG_ERROR('Actions are disabled.Queue is not supported', self._queueTypeName)
        return True

    def hasGUIPage(self):
        LOG_ERROR('QueueNotSupportedFunctional.showGUI. Queue is not supported', self._queueTypeName)
        return False

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/scheduler.py
import weakref
from gui.shared.utils.scheduled_notifications import Notifiable

class BaseScheduler(Notifiable):
    """
    Class that process schedules for prebattle functionality
    """

    def __init__(self, entity):
        super(BaseScheduler, self).__init__()
        self._entity = weakref.proxy(entity)

    def init(self):
        """
        Initialization method
        """
        pass

    def fini(self):
        """
        Finalization method
        """
        pass

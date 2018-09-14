# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/lobby/aspects.py
import weakref
from helpers import aop

class BuySlotAspect(aop.Aspect):

    def __init__(self, trigger, *args, **kwargs):
        super(BuySlotAspect, self).__init__()
        self.__triggerRef = weakref.ref(trigger)

    def atCall(self, cd):
        trigger = self.__triggerRef()
        if trigger is None:
            return
        else:
            trigger.toggle(isOn=trigger.isOn(success=True))
            return

    def clear(self):
        self.__triggerRef = None
        return


class BuySlotPointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.shared.gui_items.processors.vehicle', 'VehicleSlotBuyer', '_successHandler')

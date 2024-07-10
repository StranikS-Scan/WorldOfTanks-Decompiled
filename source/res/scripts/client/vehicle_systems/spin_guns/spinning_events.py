# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/spin_guns/spinning_events.py
import typing
import weakref
from Event import EventManager, Event, LateEvent
from vehicle_systems.spin_guns.system_interfaces import IGunSpinningEvents
if typing.TYPE_CHECKING:
    from SpinGunController import SpinGunController
    from vehicle_systems.spin_guns.system_interfaces import IGunSpinningListener

class SpinGunSpinningEvents(IGunSpinningEvents):

    def __init__(self, controller):
        super(SpinGunSpinningEvents, self).__init__()
        self.__controller = weakref.proxy(controller)
        self.__isActive = False
        self.__eventsManager = EventManager()
        self.onDestroy = Event(self.__eventsManager)
        self.onSpinFactorUpdate = LateEvent(self.__lateSpinFactorUpdate, self.__eventsManager)
        self.onSpinningActivation = LateEvent(self.__lateSpinningActivation, self.__eventsManager)
        self.onSpinningDeactivation = Event(self.__eventsManager)
        self.onTick = Event(self.__eventsManager)

    def destroy(self):
        self.onDestroy(self)
        self.__controller = None
        self.__eventsManager.clear()
        super(SpinGunSpinningEvents, self).destroy()
        return

    def lateSubscribe(self, listener):
        self.__lateSpinFactorUpdate(listener.onSpinFactorUpdate)
        self.__lateSpinningActivation(listener.onSpinningActivation)
        listener.subscribe(self)

    def processTick(self):
        if self.__isActive and self.__controller is not None:
            self.onSpinFactorUpdate(self.__controller.getSpinningValue())
        return

    def updateSpinningActiveStatus(self, isActive):
        if self.__isActive and not isActive:
            self.__deactivateSpinning()
        elif not self.__isActive and isActive:
            self.__activateSpinning()

    def __activateSpinning(self):
        self.__isActive = True
        self.onSpinFactorUpdate(self.__controller.getSpinningValue())
        self.onSpinningActivation()

    def __deactivateSpinning(self):
        self.__isActive = False
        self.onSpinFactorUpdate(self.__controller.getSpinningValue())
        self.onSpinningDeactivation()

    def __lateSpinFactorUpdate(self, handler):
        if self.__controller is not None:
            handler(self.__controller.getSpinningValue())
        return

    def __lateSpinningActivation(self, handler):
        if self.__isActive:
            handler()

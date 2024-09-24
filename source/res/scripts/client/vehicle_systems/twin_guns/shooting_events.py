# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/twin_guns/shooting_events.py
import typing
import weakref
import BigWorld
from constants import DUPLET_GUN_INDEXES_TUPLE
from Event import EventManager, Event, LateEvent
from vehicle_systems.twin_guns.system_interfaces import ITwinGunShootingEvents
if typing.TYPE_CHECKING:
    from TwinGunController import TwinGunController
    from vehicle_systems.twin_guns.system_interfaces import ITwinShootingListener

class TwinGunShootingEvents(ITwinGunShootingEvents):

    def __init__(self, controller):
        super(TwinGunShootingEvents, self).__init__()
        self.__controller = weakref.proxy(controller)
        self.__isAppearanceReady = False
        self.__lastShotTime = 0.0
        self.__eventsManager = EventManager()
        self.onDestroy = Event(self.__eventsManager)
        self.onAppearanceReady = LateEvent(self.__lateAppearanceReady, self.__eventsManager)
        self.onActiveGunsUpdate = LateEvent(self.__lateActiveGunsUpdate, self.__eventsManager)
        self.onAnimatedGunsUpdate = LateEvent(self.__lateAnimatedGunsUpdate, self.__eventsManager)
        self.onDiscreteShot = Event(self.__eventsManager)
        self.onDoubleShot = Event(self.__eventsManager)

    def destroy(self):
        self.onDestroy(self)
        self.__controller = None
        self.__lastShotTime = 0.0
        self.__eventsManager.clear()
        super(TwinGunShootingEvents, self).destroy()
        return

    def lateSubscribe(self, listener):
        self.__lateAppearanceReady(listener.onAppearanceReady)
        self.__lateActiveGunsUpdate(listener.onActiveGunsUpdate)
        listener.subscribe(self)

    def processAppearanceReady(self):
        self.__isAppearanceReady = True
        self.onAppearanceReady()

    def processNextGunsUpdate(self, nextGunIndexes):
        self.onAnimatedGunsUpdate(self.__getAnimatedGunIndexes(nextGunIndexes=nextGunIndexes))

    def processDiscreteShot(self, gunIndex):
        self.__lastShotTime = BigWorld.time()
        self.onDiscreteShot(gunIndex)

    def processDoubleShot(self):
        self.__lastShotTime = BigWorld.time()
        self.onDoubleShot(DUPLET_GUN_INDEXES_TUPLE)

    def __needDelayGunsAnimation(self):
        return self.__lastShotTime + self.__controller.getAfterShotDelay() > BigWorld.time()

    def __getAnimatedGunIndexes(self, gunIndexes=None, nextGunIndexes=None):
        gunIndexes = gunIndexes or self.__controller.getActiveGunIndexes()
        nextGunIndexes = nextGunIndexes or self.__controller.getNextGunIndexes()
        return gunIndexes if self.__needDelayGunsAnimation() else nextGunIndexes

    def __lateAppearanceReady(self, handler):
        if self.__isAppearanceReady:
            handler()

    def __lateActiveGunsUpdate(self, handler):
        if self.__isAppearanceReady and self.__controller is not None:
            handler(self.__controller.getActiveGunIndexes())
        return

    def __lateAnimatedGunsUpdate(self, handler):
        if self.__isAppearanceReady and self.__controller is not None:
            handler(self.__getAnimatedGunIndexes())
        return

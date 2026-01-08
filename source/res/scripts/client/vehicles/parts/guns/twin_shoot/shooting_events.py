# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/twin_shoot/shooting_events.py
from __future__ import absolute_import
import typing
import BigWorld
from vehicles.parts.guns.twin_shoot.guns_interfaces import ITwinShootingEventsLogic, ITwinShootingListenerLogic
from vehicles.parts.guns.common import GunShootingEvents, GunShootingCGFIntegration, GunShootingEventsDebugger
if typing.TYPE_CHECKING:
    from vehicles.parts.guns.twin_shoot.guns_interfaces import ITwinShootGunComponent

class TwinShootingEvents(GunShootingEvents, ITwinShootingEventsLogic):

    def __init__(self, component):
        super(TwinShootingEvents, self).__init__(component)
        self.__lastShotTime = 0.0
        self.onActiveGunsUpdate = self._createLateEvent(self.__lateActiveGunsUpdate)
        self.onAnimatedGunsUpdate = self._createLateEvent(self.__lateAnimatedGunsUpdate)

    def destroy(self):
        self.__lastShotTime = 0.0
        super(TwinShootingEvents, self).destroy()

    def processNextGunsUpdate(self, nextGunIndexes):
        self.onAnimatedGunsUpdate(self.__getAnimatedGunIndexes(nextGunIndexes=nextGunIndexes))

    def processDiscreteShot(self, gunIndex):
        self.__lastShotTime = BigWorld.time()
        super(TwinShootingEvents, self).processDiscreteShot(gunIndex)

    def processMultiShot(self, gunIndexes):
        self.__lastShotTime = BigWorld.time()
        super(TwinShootingEvents, self).processMultiShot(gunIndexes)

    def _createCGFIntegration(self):
        return TwinShootingCGFIntegration(self, self._getComponent())

    def _createEventsDebugger(self):
        return TwinShootingEventsDebugger(self, self._getComponent())

    def _lateSubscribe(self, listener):
        super(TwinShootingEvents, self)._lateSubscribe(listener)
        self.__lateActiveGunsUpdate(listener.onActiveGunsUpdate)
        self.__lateAnimatedGunsUpdate(listener.onAnimatedGunsUpdate)

    def __needDelayGunsAnimation(self):
        return self.__lastShotTime + self._getComponent().getAfterShotDelay() > BigWorld.time()

    def __getAnimatedGunIndexes(self, gunIndexes=None, nextGunIndexes=None):
        gunIndexes = gunIndexes or self._getComponent().getActiveGunIndexes()
        nextGunIndexes = nextGunIndexes or self._getComponent().getNextGunIndexes()
        return gunIndexes if self.__needDelayGunsAnimation() else nextGunIndexes

    def __lateActiveGunsUpdate(self, handler):
        if self._isAppearanceReady and self._getComponent() is not None:
            handler(self._getComponent().getActiveGunIndexes())
        return

    def __lateAnimatedGunsUpdate(self, handler):
        if self._isAppearanceReady and self._getComponent() is not None:
            handler(self.__getAnimatedGunIndexes())
        return


class TwinShootingCGFIntegration(GunShootingCGFIntegration, ITwinShootingListenerLogic):
    pass


class TwinShootingEventsDebugger(GunShootingEventsDebugger):
    _EVENTS_DEBUG_PREFIX = 'TWIN_GUN'

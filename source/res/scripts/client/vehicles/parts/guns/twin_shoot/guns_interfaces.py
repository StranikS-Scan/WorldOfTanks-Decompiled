# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/twin_shoot/guns_interfaces.py
from __future__ import absolute_import
import typing
from vehicles.parts.guns.common import IGunComponent, IGunShootingEvents, IGunShootingListener

class ITwinShootGunComponent(IGunComponent):

    def isDoubleBarrelMode(self):
        raise NotImplementedError

    def getActiveGunIndexes(self):
        raise NotImplementedError

    def getAfterShotDelay(self):
        raise NotImplementedError

    def getNextGunIndexes(self):
        raise NotImplementedError


class ITwinShootingEventsLogic(object):
    onActiveGunsUpdate = None
    onAnimatedGunsUpdate = None

    def processNextGunsUpdate(self, nextGunIndexes):
        raise NotImplementedError


class ITwinShootingEvents(IGunShootingEvents, ITwinShootingEventsLogic):
    pass


class ITwinShootingListenerLogic(object):

    def onActiveGunsUpdate(self, gunIndexes):
        pass

    def onAnimatedGunsUpdate(self, gunIndexes):
        pass


class ITwinShootingListener(IGunShootingListener, ITwinShootingListenerLogic):
    pass

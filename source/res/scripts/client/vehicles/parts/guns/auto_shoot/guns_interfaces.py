# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/auto_shoot/guns_interfaces.py
from __future__ import absolute_import
from vehicles.parts.guns.common import IGunComponent, IGunShootingEvents, IGunShootingListener

class IAutoShootDispersionState(object):

    def getCurrentDispersionFactor(self):
        raise NotImplementedError


class IAutoShootGunComponentState(object):

    def isShooting(self):
        raise NotImplementedError

    def isContinuousShooting(self):
        raise NotImplementedError

    def getDefaultShotRatePerSecond(self):
        raise NotImplementedError

    def getGroupShotInterval(self):
        raise NotImplementedError

    def getShotRatePerSecond(self):
        raise NotImplementedError


class IAutoShootGunComponent(IGunComponent):

    def getComponentState(self):
        raise NotImplementedError

    def getDispersionState(self):
        raise NotImplementedError


class IAutoShootingEventsLogic(object):
    onBurstActivation = None
    onBurstDeactivation = None
    onContinuousBurstActivation = None
    onContinuousBurstDeactivation = None
    onContinuousBurstUpdate = None
    onShotRateUpdate = None

    def updateAutoShootingState(self, componentState):
        raise NotImplementedError


class IAutoShootingEvents(IGunShootingEvents, IAutoShootingEventsLogic):
    pass


class IAutoShootingListenerLogic(object):

    def onBurstActivation(self):
        pass

    def onBurstDeactivation(self):
        pass

    def onContinuousBurstActivation(self):
        pass

    def onContinuousBurstDeactivation(self):
        pass

    def onContinuousBurstUpdate(self):
        pass

    def onShotRateUpdate(self, rate):
        pass


class IAutoShootingListener(IGunShootingListener, IAutoShootingListenerLogic):
    pass

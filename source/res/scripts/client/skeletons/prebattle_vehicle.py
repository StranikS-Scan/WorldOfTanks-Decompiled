# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/prebattle_vehicle.py
from Event import Event

class IPrebattleVehicle(object):
    onChanged = None

    def switchCamera(self, vehicle):
        raise NotImplementedError

    def select(self, vehicle):
        raise NotImplementedError

    def selectVehicle(self, idx):
        raise NotImplementedError

    def selectPreviousVehicle(self):
        raise NotImplementedError

    def selectAny(self):
        raise NotImplementedError

    def selectNone(self):
        raise NotImplementedError

    def getViewState(self):
        raise NotImplementedError

    def isPresent(self):
        raise NotImplementedError

    def isPremiumIGR(self):
        raise NotImplementedError

    def isInHangar(self):
        raise NotImplementedError

    def isDisabled(self):
        raise NotImplementedError

    def isBroken(self):
        raise NotImplementedError

    def isDisabledInRent(self):
        raise NotImplementedError

    def isOnlyForEventBattles(self):
        raise NotImplementedError

    def isOutfitLocked(self):
        raise NotImplementedError

    def isCustomizationEnabled(self):
        raise NotImplementedError

    @property
    def item(self):
        raise NotImplementedError

    @property
    def invID(self):
        raise NotImplementedError

    @property
    def lastInvID(self):
        raise NotImplementedError

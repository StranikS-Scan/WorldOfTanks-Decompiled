# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/techtree_events.py
from Event import Event

class ITechTreeEventsListener(object):
    onEventsUpdated = None
    onSettingsChanged = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def actions(self):
        raise NotImplementedError

    def getUserName(self):
        raise NotImplementedError

    def getVehicles(self, nationID=None):
        raise NotImplementedError

    def setNationViewed(self, nationID):
        raise NotImplementedError

    def getNations(self, unviewed=False):
        raise NotImplementedError

    def getTimeTillEnd(self):
        raise NotImplementedError

    def getFinishTime(self):
        raise NotImplementedError

    def hasActiveAction(self, vehicleCD, nationID=None):
        raise NotImplementedError

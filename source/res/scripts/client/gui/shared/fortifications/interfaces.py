# Embedded file name: scripts/client/gui/shared/fortifications/interfaces.py
from debug_utils import LOG_DEBUG
from gui.shared.fortifications.settings import FORT_RESTRICTION

class IFortController(object):

    def __del__(self):
        LOG_DEBUG('Fort controller deleted:', self)

    def init(self, clan, listeners):
        pass

    def fini(self):
        pass

    @classmethod
    def isNext(cls, stateID, isLeader):
        return False

    def getPermissions(self):
        return IFortPermissions()

    def getLimits(self):
        return IFortLimits()

    def getSortiesCache(self):
        return None

    def removeSortiesCache(self):
        return None

    def getFort(self):
        return None

    def request(self, ctx, callback = None):
        pass

    def subscribe(self, callback = None):
        pass

    def unsubscribe(self, callback = None):
        pass


class IFortListener(object):

    def onClientStateChanged(self, state):
        pass

    def onClanMembersListChanged(self):
        pass

    def onSortieChanged(self, cache, item):
        pass

    def onSortieRemoved(self, cache, sortieID):
        pass

    def onSortieUnitReceived(self, clientIdx):
        pass

    def onUpgradeVisitedBuildingChanged(self, buildingID):
        pass

    def onUpdated(self):
        pass

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        pass

    def onBuildingsUpdated(self, buildingsTypeIDs, cooldownPassed = False):
        pass

    def onBuildingRemoved(self, buildingTypeID):
        pass

    def onTransport(self):
        pass

    def onDirectionOpened(self, dir):
        pass

    def onDirectionClosed(self, dir):
        pass

    def onStateChanged(self, state):
        pass

    def onOrderReady(self, orderTypeID, count):
        pass

    def onDossierChanged(self, compDossierDescr):
        pass

    def onPlayerAttached(self, buildingTypeID):
        pass


class IFortPermissions(object):

    def canCreate(self):
        return False

    def canDelete(self):
        return False

    def canOpenDirection(self):
        return False

    def canCloseDirection(self):
        return False

    def canAddBuilding(self):
        return False

    def canDeleteBuilding(self):
        return False

    def canTransport(self):
        return False

    def canAddOrder(self):
        return False

    def canActivateOrder(self):
        return False

    def canUpgradeBuilding(self):
        return False

    def canAttach(self):
        return False


class IFortLimits(object):

    def getDirectionsMembersRequirements(self):
        return {}

    def isCreationValid(self):
        return (False, FORT_RESTRICTION.UNKNOWN)

    def isDirectionValid(self, direction, open = True):
        return (False, FORT_RESTRICTION.UNKNOWN)

    def isOrderValid(self, orderTypeID, count = 1, add = True):
        return (False, FORT_RESTRICTION.UNKNOWN)

    def canBuild(self, buildingID):
        return (False, FORT_RESTRICTION.UNKNOWN)

    def canUpgrade(self, buildingTypeID):
        return (False, FORT_RESTRICTION.UNKNOWN)

    def isSortieCreationValid(self, level = None):
        return (False, FORT_RESTRICTION.UNKNOWN)

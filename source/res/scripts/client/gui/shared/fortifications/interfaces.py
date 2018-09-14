# Embedded file name: scripts/client/gui/shared/fortifications/interfaces.py
from debug_utils import LOG_DEBUG
from gui.shared.fortifications.settings import FORT_RESTRICTION

class IFortController(object):

    def __del__(self):
        LOG_DEBUG('Fort controller deleted:', self)

    def init(self, clan, listeners, prevController = None):
        pass

    def fini(self, clearCache = True):
        pass

    @classmethod
    def isNext(cls, stateID, isLeader):
        return False

    def getPermissions(self):
        return IFortPermissions()

    def getLimits(self):
        return IFortLimits()

    def getValidators(self):
        return None

    def getSortiesCache(self):
        return None

    def getSortiesCurfewCtrl(self):
        return None

    def getPublicInfoCache(self):
        return None

    def removeSortiesCache(self):
        return None

    def removeFortBattlesCache(self):
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

    def onFortBattleChanged(self, cache, item, battleItem):
        pass

    def onFortBattleRemoved(self, cache, battleID):
        pass

    def onFortBattleUnitReceived(self, clientIdx):
        pass

    def onUpgradeVisitedBuildingChanged(self, buildingID):
        pass

    def onUpdated(self, isFullUpdate):
        pass

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        pass

    def onBuildingsUpdated(self, buildingsTypeIDs, cooldownPassed = False):
        pass

    def onTransport(self):
        pass

    def onDirectionOpened(self, dir):
        pass

    def onDirectionClosed(self, dir):
        pass

    def onDirectionLockChanged(self):
        pass

    def onStateChanged(self, state):
        pass

    def onOrderChanged(self, orderTypeID, reason):
        pass

    def onDossierChanged(self, compDossierDescr):
        pass

    def onPlayerAttached(self, buildingTypeID):
        pass

    def onSettingCooldown(self, eventTypeID):
        pass

    def onPeripheryChanged(self, peripheryID):
        pass

    def onDefenceHourChanged(self, hour):
        pass

    def onDefenceHourActivated(self, hour, initiatorDBID):
        pass

    def onDefenceHourStateChanged(self):
        pass

    def onOffDayChanged(self, offDay):
        pass

    def onVacationChanged(self, vacationStart, vacationEnd):
        pass

    def onFavoritesChanged(self, clanDBID):
        pass

    def onFortPublicInfoReceived(self, hasResults):
        pass

    def onFortPublicInfoValidationError(self, reason):
        pass

    def onEnemyClanCardReceived(self, card):
        pass

    def onEnemyClanCardRemoved(self):
        pass

    def onShutdownDowngrade(self):
        pass

    def onDefenceHourShutdown(self):
        pass

    def onEnemyStateChanged(self, battleID, isReady):
        pass

    def onConsumablesChanged(self, unitMgrID):
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

    def canCreateSortie(self):
        return False

    def canCreateFortBattle(self):
        return False

    def canChangeDefHour(self):
        return False

    def canChangeOffDay(self):
        return False

    def canChangePeriphery(self):
        return False

    def canChangeVacation(self):
        return False

    def canChangeSettings(self):
        return False

    def canShutDownDefHour(self):
        return False

    def canCancelShutDownDefHour(self):
        return False

    def canRequestPublicInfo(self):
        return False

    def canRequestClanCard(self):
        return False

    def canAddToFavorite(self):
        return False

    def canRemoveFavorite(self):
        return False

    def canPlanAttack(self):
        return False

    def canViewContext(self):
        return False

    def canViewNotCommanderHelp(self):
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


class IFortValidators(object):

    def __init__(self, validators):
        self._validators = validators

    def fini(self):
        self._validators.clear()

    def validate(self, requestType, *args):
        if requestType in self._validators:
            return self._validators[requestType](*args)
        return (True, '')

# Embedded file name: scripts/client/gui/shared/fortifications/restrictions.py
from FortifiedRegionBase import _FORT_CLIENT_METHOD_ROLES, FORT_CLIENT_METHOD
import constants
from UnitBase import SORTIE_DIVISION
from constants import CLAN_MEMBER_FLAGS, FORT_BUILDING_TYPE, MAX_FORTIFICATION_LEVEL, PREBATTLE_TYPE, FORT_SCOUTING_DATA_FILTER
from external_strings_utils import isClanAbbrevValid
import fortified_regions
from gui.shared.fortifications import interfaces, getClientFort
from gui.shared.fortifications.interfaces import IFortValidators
from gui.shared.fortifications.settings import FORT_RESTRICTION, FORT_REQUEST_TYPE, FORT_REQUEST_VALIDATION
from gui.shared.utils.decorators import ReprInjector
from messenger.storage import storage_getter

@ReprInjector.simple('_roles', 'roles')

class FortPermissions(interfaces.IFortPermissions):

    def __init__(self, roles = 0):
        super(FortPermissions, self).__init__()
        self._roles = roles

    def canCreate(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CREATE)

    def canDelete(self):
        return self._checkPermission(FORT_CLIENT_METHOD.DELETE)

    def canOpenDirection(self):
        return self._checkPermission(FORT_CLIENT_METHOD.OPEN_DIR)

    def canCloseDirection(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CLOSE_DIR)

    def canAddBuilding(self):
        return self._checkPermission(FORT_CLIENT_METHOD.ADD_BUILDING)

    def canDeleteBuilding(self):
        return self._checkPermission(FORT_CLIENT_METHOD.DEL_BUILDING)

    def canTransport(self):
        return self._checkPermission(FORT_CLIENT_METHOD.TRANSPORT)

    def canAddOrder(self):
        return self._checkPermission(FORT_CLIENT_METHOD.ADD_ORDER)

    def canActivateOrder(self):
        return self._checkPermission(FORT_CLIENT_METHOD.ACTIVATE_ORDER)

    def canUpgradeBuilding(self):
        return self._checkPermission(FORT_CLIENT_METHOD.UPGRADE)

    def canAttach(self):
        return self._checkPermission(FORT_CLIENT_METHOD.ATTACH)

    def canCreateSortie(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CREATE_SORTIE)

    def canCreateFortBattle(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CREATE_JOIN_FORT_BATTLE)

    def canChangeDefHour(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CHANGE_DEF_HOUR)

    def canChangeOffDay(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CHANGE_OFF_DAY)

    def canChangePeriphery(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CHANGE_PERIPHERY)

    def canChangeVacation(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CHANGE_VACATION)

    def canChangeSettings(self):
        return self.canChangeDefHour() and self.canChangeOffDay() and self.canChangePeriphery() and self.canChangeVacation()

    def canShutDownDefHour(self):
        return self._checkPermission(FORT_CLIENT_METHOD.SHUTDOWN_DEF_HOUR)

    def canCancelShutDownDefHour(self):
        return self._checkPermission(FORT_CLIENT_METHOD.CANCEL_SHUTDOWN)

    def canRequestPublicInfo(self):
        return self.canRequestClanCard()

    def canRequestClanCard(self):
        return self._checkPermission(FORT_CLIENT_METHOD.GET_ENEMY_CLAN_CARD)

    def canAddToFavorite(self):
        return self._checkPermission(FORT_CLIENT_METHOD.ADD_FAVORITE)

    def canRemoveFavorite(self):
        return self._checkPermission(FORT_CLIENT_METHOD.REMOVE_FAVORITE)

    def canPlanAttack(self):
        return self._checkPermission(FORT_CLIENT_METHOD.PLAN_ATTACK)

    def canActivateConsumable(self):
        return self._checkPermission(FORT_CLIENT_METHOD.ACTIVATE_CONSUMABLE)

    def canReturnConsumable(self):
        return self._checkPermission(FORT_CLIENT_METHOD.DEACTIVATE_CONSUMABLE)

    def canViewContext(self):
        return self._roles & (CLAN_MEMBER_FLAGS.LEADER | CLAN_MEMBER_FLAGS.VICE_LEADER) > 0

    def canViewNotCommanderHelp(self):
        return self._roles & CLAN_MEMBER_FLAGS.LEADER == 0

    def _checkPermission(self, cmd):
        cmdRoles = _FORT_CLIENT_METHOD_ROLES.get(cmd, 0)
        if cmdRoles > 0 and self._roles & cmdRoles == 0:
            return False
        return True


class NoFortLimits(interfaces.IFortLimits):

    def isCreationValid(self):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)

    def isDirectionValid(self, direction, open = True):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)

    def isOrderValid(self, orderTypeID, count = 1, add = True):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)

    def canBuild(self, buildingID):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)

    def canUpgrade(self, buildingTypeID):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)

    def isSortieCreationValid(self, level = None):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)


class IntroFortLimits(interfaces.IFortLimits):

    @storage_getter('users')
    def userStorage(self):
        return None

    def getClanMembersCount(self):
        result = 0
        if self.userStorage:
            result = len(set(self.userStorage.getClanMembersIterator(False)))
        return result

    def getDirectionsMembersRequirements(self):
        result = {}
        for dir in range(1, fortified_regions.g_cache.maxDirections + 1):
            if dir == 1 and fortified_regions.g_cache.isFirstDirectionFree:
                result[dir] = 0
            else:
                result[dir] = dir * fortified_regions.g_cache.clanMembersPerDirection

        return result

    def isCreationValid(self):
        if self.getClanMembersCount() < fortified_regions.g_cache.clanMembersForStart:
            return (False, FORT_RESTRICTION.CREATION_MIN_COUNT)
        return (True, '')

    def isDirectionValid(self, direction, open = True):
        if direction < 1:
            return (False, FORT_RESTRICTION.DIRECTION_MIN_COUNT)
        elif direction > fortified_regions.g_cache.maxDirections:
            return (False, FORT_RESTRICTION.DIRECTION_MAX_COUNT)
        fort = getClientFort()
        if fort is None:
            return (False, FORT_RESTRICTION.UNKNOWN)
        openedDirections = len(fort.getOpenedDirections())
        if open and self.getDirectionsMembersRequirements().get(openedDirections + 1, 0) > self.getClanMembersCount():
            return (False, FORT_RESTRICTION.DIRECTION_NOT_ENOUGH_MEMBERS)
        else:
            return (True, '')

    def canBuild(self, buildingID):
        fort = getClientFort()
        if fort is None:
            return (False, FORT_RESTRICTION.UNKNOWN)
        else:
            return (True, '')

    def isOrderValid(self, orderTypeID, count = 1, add = True):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)

    def isSortieCreationValid(self, level = None):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)


class FortLimits(IntroFortLimits):

    def isCreationValid(self):
        return (False, FORT_RESTRICTION.NOT_AVAILABLE)

    def isOrderValid(self, orderTypeID, count = 1, add = True):
        fort = getClientFort()
        if fort is None:
            return (False, FORT_RESTRICTION.UNKNOWN)
        order = fort.getOrder(orderTypeID)
        if order is None:
            return (False, FORT_RESTRICTION.UNKNOWN)
        elif add and order.count + count > order.maxCount:
            return (False, FORT_RESTRICTION.ORDER_MAX_COUNT)
        else:
            return (True, '')

    def canActivateOrder(self, orderID):
        fort = getClientFort()
        if fort is None:
            return (False, FORT_RESTRICTION.UNKNOWN)
        else:
            order = fort.getOrder(orderID)
            canActivate = False
            if order.hasBuilding and order.count > 0 and not order.inCooldown:
                if order.isPermanent:
                    canActivate = fort.isDefenceHourEnabled()
                else:
                    canActivate = order.isCompatible or not fort.hasActivatedContinualOrders()
            return (canActivate, '')

    def canUpgrade(self, buildingTypeID):
        fort = getClientFort()
        restrict, restricType = True, ''
        if fort is None:
            return (False, FORT_RESTRICTION.UNKNOWN)
        else:
            building = fort.getBuilding(buildingTypeID)
            if building is None:
                return (False, FORT_RESTRICTION.UNKNOWN)
            upgradeCost = building.levelRef.upgradeCost
            if not upgradeCost:
                restrict, restricType = False, FORT_RESTRICTION.BUILDING_CANT_UPGRADE
            level = building.level
            baseDescr = fort.getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
            if buildingTypeID != FORT_BUILDING_TYPE.MILITARY_BASE and level >= baseDescr.level:
                restrict, restricType = False, FORT_RESTRICTION.BUILDING_FORT_LEVEL_TOO_LOW
            if buildingTypeID == FORT_BUILDING_TYPE.MILITARY_BASE and baseDescr.level >= MAX_FORTIFICATION_LEVEL:
                restrict, restricType = False, FORT_RESTRICTION.BUILDING_CANT_UPGRADE
            if building.storage < upgradeCost:
                if buildingTypeID != FORT_BUILDING_TYPE.MILITARY_BASE and level >= baseDescr.level:
                    return (False, FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE_AND_LOW_LEVEL)
                restrict, restricType = False, FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE
            return (restrict, restricType)

    def isSortieCreationValid(self, level = None):
        from gui.prb_control.dispatcher import g_prbLoader
        fort = getClientFort()
        if fort is None:
            return (False, FORT_RESTRICTION.UNKNOWN)
        elif level is not None and level not in SORTIE_DIVISION._ORDER:
            return (False, FORT_RESTRICTION.SORTIE_LEVEL_INVALID)
        elif not fort.isStartingScriptDone():
            return (False, FORT_RESTRICTION.STARTING_SCRIPT_NOT_DONE)
        elif len(fort.sorties) >= fortified_regions.g_cache.maxSorties:
            return (False, FORT_RESTRICTION.SORTIE_MAX_COUNT)
        state = g_prbLoader.getDispatcher().getFunctionalState()
        if not state.isInUnit(PREBATTLE_TYPE.SORTIE) and state.hasModalEntity:
            return (False, FORT_RESTRICTION.SORTIE_HAS_MODAL_ENTITY)
        else:
            return (True, '')


class NoFortValidators(IFortValidators):

    def __init__(self):
        super(NoFortValidators, self).__init__({})


class FortValidators(IFortValidators):

    def __init__(self):
        super(FortValidators, self).__init__({FORT_REQUEST_TYPE.REQUEST_PUBLIC_INFO: self.__validateFortPublicInfo})

    def __validateFortPublicInfo(self, filterType, abbrevPattern):
        if filterType == FORT_SCOUTING_DATA_FILTER.FILTER:
            if not isClanAbbrevValid(abbrevPattern):
                if constants.IS_KOREA:
                    return (False, FORT_REQUEST_VALIDATION.REQUEST_PUBLIC_INFO.ABBREV_IS_INVALID_KR)
                elif constants.IS_CHINA:
                    return (False, FORT_REQUEST_VALIDATION.REQUEST_PUBLIC_INFO.ABBREV_IS_INVALID_CN)
                else:
                    return (False, FORT_REQUEST_VALIDATION.REQUEST_PUBLIC_INFO.ABBREV_IS_INVALID)
        return (True, '')

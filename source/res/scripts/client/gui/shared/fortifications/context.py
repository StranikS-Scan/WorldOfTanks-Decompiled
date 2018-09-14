# Embedded file name: scripts/client/gui/shared/fortifications/context.py
from constants import REQUEST_COOLDOWN, PREBATTLE_TYPE
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.prb_control import settings as prb_settings
from gui.prb_control.prb_getters import getUnitIdx
from gui.shared.fortifications.settings import FORT_REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx

@ReprInjector.withParent(('__isUpdateExpected', 'isUpdateExpected'))

class FortRequestCtx(RequestCtx):

    def __init__(self, waitingID = '', isUpdateExpected = False):
        super(FortRequestCtx, self).__init__(waitingID)
        self.__isUpdateExpected = isUpdateExpected

    def isUpdateExpected(self):
        return self.__isUpdateExpected

    def getCooldown(self):
        return REQUEST_COOLDOWN.CALL_FORT_METHOD

    def _setUpdateExpected(self, value):
        self.__isUpdateExpected = value


class CreateFortCtx(FortRequestCtx):

    def __init__(self, waitingID = ''):
        super(CreateFortCtx, self).__init__(waitingID, True)

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CREATE_FORT


class DeleteFortCtx(FortRequestCtx):

    def __init__(self, waitingID = ''):
        super(DeleteFortCtx, self).__init__(waitingID, True)

    def getRequestType(self):
        return FORT_REQUEST_TYPE.DELETE_FORT


@ReprInjector.withParent(('__direction', 'direction'), ('__isOpen', 'isOpen'))

class DirectionCtx(FortRequestCtx):

    def __init__(self, direction, isOpen = True, waitingID = ''):
        super(DirectionCtx, self).__init__(waitingID, True)
        self.__direction = direction
        self.__isOpen = isOpen

    def getRequestType(self):
        if self.__isOpen:
            return FORT_REQUEST_TYPE.OPEN_DIRECTION
        return FORT_REQUEST_TYPE.CLOSE_DIRECTION

    def getDirection(self):
        return self.__direction


@ReprInjector.withParent(('__buildingTypeID', 'buildingTypeID'), ('__direction', 'direction'), ('__position', 'position'), ('__isAdd', 'isAdd'))

class BuildingCtx(FortRequestCtx):

    def __init__(self, buildingTypeID, direction = None, position = None, isAdd = True, waitingID = ''):
        super(BuildingCtx, self).__init__(waitingID, True)
        self.__buildingTypeID = buildingTypeID
        self.__direction = direction
        self.__position = position
        self.__isAdd = isAdd

    def getRequestType(self):
        if self.__isAdd:
            return FORT_REQUEST_TYPE.ADD_BUILDING
        return FORT_REQUEST_TYPE.DELETE_BUILDING

    def getDirection(self):
        return self.__direction

    def getPosition(self):
        return self.__position

    def getBuildingTypeID(self):
        return self.__buildingTypeID


@ReprInjector.withParent(('__fromBuildingTypeID', 'fromBuildingTypeID'), ('__toBuildingTypeID', 'toBuildingTypeID'), ('__resCount', 'resCount'))

class TransportationCtx(FortRequestCtx):

    def __init__(self, fromBuildingTypeID, toBuildingTypeID, resCount, waitingID = ''):
        super(TransportationCtx, self).__init__(waitingID, True)
        self.__fromBuildingTypeID = fromBuildingTypeID
        self.__toBuildingTypeID = toBuildingTypeID
        self.__resCount = resCount

    def getRequestType(self):
        return FORT_REQUEST_TYPE.TRANSPORTATION

    def getFromBuildingTypeID(self):
        return self.__fromBuildingTypeID

    def getToBuildingTypeID(self):
        return self.__toBuildingTypeID

    def getResCount(self):
        return self.__resCount


@ReprInjector.withParent(('__orderTypeID', 'orderTypeID'), ('__count', 'count'), ('__isAdd', 'isAdd'))

class OrderCtx(FortRequestCtx):

    def __init__(self, orderTypeID, count = 1, isAdd = True, waitingID = ''):
        super(OrderCtx, self).__init__(waitingID, True)
        self.__orderTypeID = orderTypeID
        self.__count = count
        self.__isAdd = isAdd

    def getRequestType(self):
        if self.__isAdd:
            return FORT_REQUEST_TYPE.ADD_ORDER
        return FORT_REQUEST_TYPE.ACTIVATE_ORDER

    def getOrderTypeID(self):
        return self.__orderTypeID

    def getCount(self):
        return self.__count


@ReprInjector.withParent(('__buildingTypeID', 'buildingTypeID'))

class AttachCtx(FortRequestCtx):

    def __init__(self, buildingTypeID, waitingID = ''):
        super(AttachCtx, self).__init__(waitingID, True)
        self.__buildingTypeID = buildingTypeID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.ATTACH

    def getBuildingTypeID(self):
        return self.__buildingTypeID


@ReprInjector.withParent(('__buildingTypeID', 'buildingTypeID'))

class UpgradeCtx(FortRequestCtx):

    def __init__(self, buildingTypeID, waitingID = ''):
        super(UpgradeCtx, self).__init__(waitingID, True)
        self.__buildingTypeID = buildingTypeID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.UPGRADE

    def getBuildingTypeID(self):
        return self.__buildingTypeID


@ReprInjector.withParent(('__divisionLevel', 'divisionLevel'))

class CreateSortieCtx(FortRequestCtx):

    def __init__(self, divisionLevel = 10, waitingID = ''):
        super(CreateSortieCtx, self).__init__(waitingID)
        self.__divisionLevel = divisionLevel

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CREATE_SORTIE

    def getDivisionLevel(self):
        return self.__divisionLevel

    def __repr__(self):
        return 'CreateSortieCtx(buildingTypeID={0:n}, waitingID={1:>s})'.format(self.__divisionLevel, self.getWaitingID())


@ReprInjector.withParent(('__unitMgrID', 'unitMgrID'), ('__peripheryID', 'peripheryID'))

class RequestSortieUnitCtx(FortRequestCtx):

    def __init__(self, unitMgrID, peripheryID, waitingID = ''):
        super(RequestSortieUnitCtx, self).__init__(waitingID)
        self.__unitMgrID = unitMgrID
        self.__peripheryID = peripheryID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.REQUEST_SORTIE_UNIT

    def getCooldown(self):
        return REQUEST_COOLDOWN.GET_FORT_SORTIE_DATA

    def getUnitMgrID(self):
        return self.__unitMgrID

    def getPeripheryID(self):
        return self.__peripheryID

    def __repr__(self):
        return 'RequestSortieUnitCtx(unitMgrID={0:n}, peripheryID={1:n}, waitingID={2:>s})'.format(self.__unitMgrID, self.__peripheryID, self.getWaitingID())


@ReprInjector.withParent(('_defenceHour', 'defenceHour'))

class DefenceHourCtx(FortRequestCtx):

    def __init__(self, defenceHour, waitingID = ''):
        super(DefenceHourCtx, self).__init__(waitingID)
        self._defenceHour = defenceHour

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_DEF_HOUR

    def getDefenceHour(self):
        return self._defenceHour


@ReprInjector.withParent(('_offDay', 'offDay'))

class OffDayCtx(FortRequestCtx):

    def __init__(self, offDay, waitingID = ''):
        super(OffDayCtx, self).__init__(waitingID)
        self._offDay = offDay

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_OFF_DAY

    def getOffDay(self):
        return self._offDay


@ReprInjector.withParent(('_peripheryID', 'peripheryID'))

class PeripheryCtx(FortRequestCtx):

    def __init__(self, peripheryID, waitingID = ''):
        super(PeripheryCtx, self).__init__(waitingID)
        self._peripheryID = peripheryID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_PERIPHERY

    def getPeripheryID(self):
        return self._peripheryID


@ReprInjector.withParent(('_timeVacationStart', 'timeVacationStart'), ('_vacationDuration', 'vacationDuration'))

class VacationCtx(FortRequestCtx):

    def __init__(self, timeVacationStart, vacationDuration, waitingID = ''):
        super(VacationCtx, self).__init__(waitingID)
        self._timeVacationStart = timeVacationStart
        self._vacationDuration = vacationDuration

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_VACATION

    def getTimeVacationStart(self):
        return self._timeVacationStart

    def getTimeVacationEnd(self):
        return self.getTimeVacationStart() + self.getTimeVacationDuration()

    def getTimeVacationDuration(self):
        return self._vacationDuration


class SettingsCtx(DefenceHourCtx, OffDayCtx, PeripheryCtx):

    def __init__(self, defenceHour, offDay, peripheryID, waitingID = ''):
        DefenceHourCtx.__init__(self, defenceHour, waitingID)
        OffDayCtx.__init__(self, offDay, waitingID)
        PeripheryCtx.__init__(self, peripheryID, waitingID)

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_SETTINGS


@ReprInjector.withParent(('_shutDown', 'shutDown'))

class DefencePeriodCtx(FortRequestCtx):

    def __init__(self, shutDown = True, waitingID = ''):
        super(DefencePeriodCtx, self).__init__(waitingID)
        self._shutDown = shutDown

    def getRequestType(self):
        if self._shutDown:
            return FORT_REQUEST_TYPE.SHUTDOWN_DEF_HOUR
        else:
            return FORT_REQUEST_TYPE.CANCEL_SHUTDOWN_DEF_HOUR


@ReprInjector.withParent(('_filterType', 'filterType'), ('_abbrevPattern', 'abbrevPattern'), ('_limit', 'limit'), ('_lvlFrom', 'lvlFrom'), ('_lvlTo', 'lvlTo'), ('_extStartDefHourFrom', 'extStartDefHourFrom'), ('_extStartDefHourTo', 'extStartDefHourTo'), ('_attackDay', 'attackDay'), ('_firstDefaultQuery', 'firstDefaultQuery'), ('getWaitingID', 'waitingID'))

class FortPublicInfoCtx(FortRequestCtx):

    def __init__(self, filterType, abbrevPattern, limit, lvlFrom, lvlTo, extStartDefHourFrom, extStartDefHourTo, attackDay, firstDefaultQuery = False, waitingID = ''):
        super(FortPublicInfoCtx, self).__init__(waitingID)
        self._filterType = filterType
        self._abbrevPattern = abbrevPattern
        self._limit = limit
        self._lvlFrom = lvlFrom
        self._lvlTo = lvlTo
        self._extStartDefHourFrom = extStartDefHourFrom
        self._extStartDefHourTo = extStartDefHourTo
        self._attackDay = attackDay
        self._firstDefaultQuery = firstDefaultQuery

    def getRequestType(self):
        return FORT_REQUEST_TYPE.REQUEST_PUBLIC_INFO

    def getCooldown(self):
        return REQUEST_COOLDOWN.REQUEST_FORT_PUBLIC_INFO

    def getFilterType(self):
        return self._filterType

    def getAbbrevPattern(self):
        return self._abbrevPattern

    def getLimit(self):
        return self._limit

    def getLvlFrom(self):
        return self._lvlFrom

    def getLvlTo(self):
        return self._lvlTo

    def getStartDefHourFrom(self):
        return self._extStartDefHourFrom

    def getStartDefHourTo(self):
        return self._extStartDefHourTo

    def getAttackDay(self):
        return self._attackDay

    def isFirstDefaultQuery(self):
        return self._firstDefaultQuery


@ReprInjector.withParent(('__clanDBID', 'clanDBID'))

class RequestClanCardCtx(FortRequestCtx):

    def __init__(self, clanDBID, waitingID = ''):
        super(RequestClanCardCtx, self).__init__(waitingID)
        self.__clanDBID = clanDBID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.REQUEST_CLAN_CARD

    def getClanDBID(self):
        return self.__clanDBID

    def __repr__(self):
        return 'RequestClanCardCtx(clanDBID={0:n},  waitingID={1:>s})'.format(self.__clanDBID, self.getWaitingID())


@ReprInjector.withParent(('__clanDBID', 'clanDBID'), ('__isAdd', 'isAdd'))

class FavoriteCtx(FortRequestCtx):

    def __init__(self, clanDBID, isAdd = True, waitingID = ''):
        super(FavoriteCtx, self).__init__(waitingID)
        self.__clanDBID = clanDBID
        self.__isAdd = isAdd

    def getClanDBID(self):
        return self.__clanDBID

    def getRequestType(self):
        if self.__isAdd:
            return FORT_REQUEST_TYPE.ADD_FAVORITE
        else:
            return FORT_REQUEST_TYPE.REMOVE_FAVORITE


@ReprInjector.withParent(('__clanDBID', 'clanDBID'), ('__timeAttack', 'timeAttack'), ('__dirFrom', 'dirFrom'), ('__dirTo', 'dirTo'))

class AttackCtx(FortRequestCtx):

    def __init__(self, clanDBID, timeAttack, dirFrom, dirTo, waitingID = ''):
        super(AttackCtx, self).__init__(waitingID)
        self.__clanDBID = clanDBID
        self.__timeAttack = timeAttack
        self.__dirFrom = dirFrom
        self.__dirTo = dirTo

    def getClanDBID(self):
        return self.__clanDBID

    def getTimeAttack(self):
        return self.__timeAttack

    def getDirFrom(self):
        return self.__dirFrom

    def getDirTo(self):
        return self.__dirTo

    def getRequestType(self):
        return FORT_REQUEST_TYPE.PLAN_ATTACK


@ReprInjector.withParent(('__battleID', 'battleID'), ('__slotIdx', 'slotIdx'))

class CreateOrJoinFortBattleCtx(PrbCtrlRequestCtx):
    __slots__ = ('__battleID', '__slotIdx', '__isUpdateExpected')

    def __init__(self, battleID, slotIdx = -1, waitingID = '', isUpdateExpected = False, flags = prb_settings.FUNCTIONAL_FLAG.UNDEFINED):
        super(CreateOrJoinFortBattleCtx, self).__init__(ctrlType=prb_settings.CTRL_ENTITY_TYPE.UNIT, entityType=PREBATTLE_TYPE.FORT_BATTLE, waitingID=waitingID, flags=flags, isForced=True)
        self.__battleID = battleID
        self.__slotIdx = slotIdx
        self.__isUpdateExpected = isUpdateExpected

    def isUpdateExpected(self):
        return self.__isUpdateExpected

    def getCooldown(self):
        return REQUEST_COOLDOWN.CALL_FORT_METHOD

    def getUnitIdx(self):
        return getUnitIdx()

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CREATE_OR_JOIN_FORT_BATTLE

    def getID(self):
        return self.__battleID

    def getSlotIdx(self):
        return self.__slotIdx

    def _setUpdateExpected(self, value):
        self.__isUpdateExpected = value


@ReprInjector.withParent(('__consumableOrderTypeID', 'consumableOrderTypeID'), ('__slotIdx', 'slotIdx'))

class ActivateConsumableCtx(FortRequestCtx):

    def __init__(self, consumableOrderTypeID, slotIdx, waitingID = ''):
        super(ActivateConsumableCtx, self).__init__(waitingID)
        self.__consumableOrderTypeID = consumableOrderTypeID
        self.__slotIdx = slotIdx

    def getConsumableOrderTypeID(self):
        return self.__consumableOrderTypeID

    def getSlotIdx(self):
        return self.__slotIdx

    def getRequestType(self):
        return FORT_REQUEST_TYPE.ACTIVATE_CONSUMABLE


@ReprInjector.withParent(('__consumableOrderTypeID', 'consumableOrderTypeID'))

class ReturnConsumableCtx(FortRequestCtx):

    def __init__(self, consumableOrderTypeID, waitingID = ''):
        super(ReturnConsumableCtx, self).__init__(waitingID)
        self.__consumableOrderTypeID = consumableOrderTypeID

    def getConsumableOrderTypeID(self):
        return self.__consumableOrderTypeID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.RETURN_CONSUMABLE


__all__ = ('FortRequestCtx', 'CreateFortCtx', 'DeleteFortCtx', 'DirectionCtx', 'BuildingCtx', 'TransportationCtx', 'OrderCtx', 'AttachCtx', 'OrderCtx', 'UpgradeCtx', 'CreateSortieCtx', 'RequestSortieUnitCtx', 'DefenceHourCtx', 'OffDayCtx', 'PeripheryCtx', 'VacationCtx', 'SettingsCtx', 'FortPublicInfoCtx', 'RequestClanCardCtx', 'FavoriteCtx', 'CreateOrJoinFortBattleCtx', 'ActivateConsumableCtx', 'ReturnConsumableCtx')

# Embedded file name: scripts/client/gui/shared/fortifications/context.py
import calendar
import datetime
import time
from constants import REQUEST_COOLDOWN
from gui.shared.fortifications.settings import FORT_REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters.rqs_by_id import RequestCtx

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

    def __repr__(self):
        return 'FortRequestCtx(waitingID={0:>s}, update={1!r:s})'.format(self.getWaitingID(), self.__isUpdateExpected)


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

    def __repr__(self):
        return 'DirectionCtx(op={0:>s}, direction={1:n}, waitingID={2:>s})'.format('open' if self.__isOpen else 'close', self.__direction, self.getWaitingID())


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

    def __repr__(self):
        if self.__isAdd:
            return 'BuildingCtx(op={0:>s}, buildingTypeID={1:n}, ' + ' direction={2:n}, position={3:n},'
        return ' waitingID={4:>s})'.format('add' if self.__isAdd else 'delete', self.__buildingTypeID, self.__direction, self.__position, self.getWaitingID())


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

    def __repr__(self):
        return 'TransportationCtx(op={0:>s}, fromBuildingTypeID={1:n}, toBuildingTypeID={2:n}, resCount={3:n}, waitingID={4:>s})'.format('transport', self.__fromBuildingTypeID, self.__toBuildingTypeID, self.__resCount, self.getWaitingID())


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

    def __repr__(self):
        if self.__isAdd:
            formatter = 'OrderCtx(op=add, orderTypeID={0:n}, count={1:n}, waitingID={2:>s})'
        else:
            formatter = 'OrderCtx(op=activate, orderTypeID={0:n} waitingID={2:>s})'
        return formatter.format(self.__orderTypeID, self.__count, self.getWaitingID())


class AttachCtx(FortRequestCtx):

    def __init__(self, buildingTypeID, waitingID = ''):
        super(AttachCtx, self).__init__(waitingID, True)
        self.__buildingTypeID = buildingTypeID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.ATTACH

    def getBuildingTypeID(self):
        return self.__buildingTypeID

    def __repr__(self):
        return 'AttachCtx(op={0:>s}, buildingTypeID={1:n} waitingID={2:>s})'.format('attach', self.__buildingTypeID, self.getWaitingID())


class UpgradeCtx(FortRequestCtx):

    def __init__(self, buildingTypeID, waitingID = ''):
        super(UpgradeCtx, self).__init__(waitingID, True)
        self.__buildingTypeID = buildingTypeID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.UPGRADE

    def getBuildingTypeID(self):
        return self.__buildingTypeID

    def __repr__(self):
        return 'UpgradeCtx(op={0:>s}, buildingTypeID={1:n} waitingID={2:>s})'.format('upgrade', self.__buildingTypeID, self.getWaitingID())


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


class DefenceHourCtx(FortRequestCtx):

    def __init__(self, defenceHour, waitingID = ''):
        super(DefenceHourCtx, self).__init__(waitingID)
        self._defenceHour = defenceHour

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_DEF_HOUR

    def getDefenceHour(self):
        date = datetime.datetime.now()
        currentDefenceHourStart = datetime.datetime(date.year, date.month, date.day, self._defenceHour)
        localTime = time.mktime(currentDefenceHourStart.timetuple())
        return time.gmtime(localTime).tm_hour

    def __repr__(self):
        return 'DefenceHourCtx(defenceHour={0:n}, waitingID={1:>s})'.format(self._defenceHour, self.getWaitingID())


class OffDayCtx(FortRequestCtx):

    def __init__(self, offDay, waitingID = ''):
        super(OffDayCtx, self).__init__(waitingID)
        self._offDay = offDay

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_OFF_DAY

    def getOffDay(self):
        return self._offDay

    def __repr__(self):
        return 'OffDayCtx(offDay={0:n}, waitingID={1:>s})'.format(self._offDay, self.getWaitingID())


class PeripheryCtx(FortRequestCtx):

    def __init__(self, peripheryID, waitingID = ''):
        super(PeripheryCtx, self).__init__(waitingID)
        self._peripheryID = peripheryID

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_PERIPHERY

    def getPeripheryID(self):
        return self._peripheryID

    def __repr__(self):
        return 'PeripheryCtx(peripheryID={0:n}, waitingID={1:>s})'.format(self._peripheryID, self.getWaitingID())


class VacationCtx(FortRequestCtx):

    def __init__(self, timeVacationStart, timeVacationEnd, waitingID = ''):
        super(VacationCtx, self).__init__(waitingID)
        self._timeVacationStart = timeVacationStart
        self._timeVacationEnd = timeVacationEnd

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_VACATION

    def getTimeVacationStart(self):
        return calendar.timegm(time.gmtime(self._timeVacationStart))

    def getTimeVacationEnd(self):
        return self._timeVacationEnd

    def getTimeVacationDuration(self):
        return self._timeVacationEnd - self._timeVacationStart

    def __repr__(self):
        return 'VacationCtx(timeVacationStart={0:n}, timeVacationEnd={1:n}, waitingID={2:>s})'.format(self._timeVacationStart, self._timeVacationEnd, self.getWaitingID())


class SettingsCtx(DefenceHourCtx, OffDayCtx, PeripheryCtx):

    def __init__(self, defenceHour, offDay, peripheryID, waitingID = ''):
        DefenceHourCtx.__init__(self, defenceHour, waitingID)
        OffDayCtx.__init__(self, offDay, waitingID)
        PeripheryCtx.__init__(self, peripheryID, waitingID)

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CHANGE_SETTINGS

    def __repr__(self):
        return 'SettingsCtx(defenceHour={0:n}, offDay={1:n}, peripheryID={2:n}, waitingID={3:>s})'.format(self._defenceHour, self._offDay, self._peripheryID, self.getWaitingID())


class DefencePeriodCtx(FortRequestCtx):

    def __init__(self, shutDown = True, waitingID = ''):
        super(DefencePeriodCtx, self).__init__(waitingID)
        self._shutDown = shutDown

    def getRequestType(self):
        if self._shutDown:
            return FORT_REQUEST_TYPE.SHUTDOWN_DEF_HOUR
        else:
            return FORT_REQUEST_TYPE.CANCEL_SHUTDOWN_DEF_HOUR

    def __repr__(self):
        return 'DefencePeriodCtx(shutDown={0:n}, waitingID={1:>s})'.format(self._shutDown, self.getWaitingID())


@ReprInjector.simple(('_filterType', 'filterType'), ('_abbrevPattern', 'abbrevPattern'), ('_limit', 'limit'), ('_lvlFrom', 'lvlFrom'), ('_lvlTo', 'lvlTo'), ('_extStartDefHourFrom', 'extStartDefHourFrom'), ('_extStartDefHourTo', 'extStartDefHourTo'), ('_attackDay', 'attackDay'), ('getWaitingID', 'waitingID'))

class FortPublicInfoCtx(FortRequestCtx):

    def __init__(self, filterType, abbrevPattern, limit, lvlFrom, lvlTo, extStartDefHourFrom, extStartDefHourTo, attackDay, waitingID = ''):
        super(FortPublicInfoCtx, self).__init__(waitingID)
        self._filterType = filterType
        self._abbrevPattern = abbrevPattern
        self._limit = limit
        self._lvlFrom = lvlFrom
        self._lvlTo = lvlTo
        self._extStartDefHourFrom = extStartDefHourFrom
        self._extStartDefHourTo = extStartDefHourTo
        self._attackDay = attackDay

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


@ReprInjector.simple(('__clanDBID', 'clanDBID'), ('__isAdd', 'isAdd'), ('getWaitingID', 'waitingID'))

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


@ReprInjector.simple(('__clanDBID', 'clanDBID'), ('__timeAttack', 'timeAttack'), ('__dirFrom', 'dirFrom'), ('__dirTo', 'dirTo'), ('getWaitingID', 'waitingID'))

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


@ReprInjector.simple(('__battleID', 'battleID'), ('__slotIdx', 'slotIdx'), ('getWaitingID', 'waitingID'))

class CreateOrJoinFortBattleCtx(FortRequestCtx):

    def __init__(self, battleID, slotIdx = -1, waitingID = ''):
        super(CreateOrJoinFortBattleCtx, self).__init__(waitingID)
        self.__battleID = battleID
        self.__slotIdx = slotIdx

    def getRequestType(self):
        return FORT_REQUEST_TYPE.CREATE_OR_JOIN_FORT_BATTLE

    def getBattleID(self):
        return self.__battleID

    def getSlotIdx(self):
        return self.__slotIdx


__all__ = ('FortRequestCtx', 'CreateFortCtx', 'DeleteFortCtx', 'DirectionCtx', 'BuildingCtx', 'TransportationCtx', 'OrderCtx', 'AttachCtx', 'OrderCtx', 'UpgradeCtx', 'CreateSortieCtx', 'RequestSortieUnitCtx', 'DefenceHourCtx', 'OffDayCtx', 'PeripheryCtx', 'VacationCtx', 'SettingsCtx', 'FortPublicInfoCtx', 'RequestClanCardCtx', 'FavoriteCtx', 'CreateOrJoinFortBattleCtx')

# Embedded file name: scripts/client/gui/shared/fortifications/context.py
from gui.shared.fortifications.settings import FORT_REQUEST_TYPE
from gui.shared.utils.requesters.rqs_by_id import RequestCtx

class FortRequestCtx(RequestCtx):

    def __init__(self, waitingID = '', isUpdateExpected = False):
        super(FortRequestCtx, self).__init__(waitingID)
        self.__isUpdateExpected = isUpdateExpected

    def isUpdateExpected(self):
        return self.__isUpdateExpected

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

    def getUnitMgrID(self):
        return self.__unitMgrID

    def getPeripheryID(self):
        return self.__peripheryID

    def __repr__(self):
        return 'RequestSortieUnitCtx(unitMgrID={0:n}, peripheryID={1:n}, waitingID={2:>s})'.format(self.__unitMgrID, self.__peripheryID, self.getWaitingID())


__all__ = ('FortRequestCtx', 'CreateFortCtx', 'DeleteFortCtx', 'DirectionCtx', 'BuildingCtx', 'TransportationCtx', 'OrderCtx', 'AttachCtx', 'OrderCtx', 'UpgradeCtx', 'CreateSortieCtx', 'RequestSortieUnitCtx')

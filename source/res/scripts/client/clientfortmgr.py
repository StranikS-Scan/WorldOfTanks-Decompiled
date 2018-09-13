# Embedded file name: scripts/client/ClientFortMgr.py
from FortifiedRegionBase import FORT_CLIENT_METHOD
from ClientFortifiedRegion import ClientFortifiedRegion
import Event
from debug_utils import *
from gui.shared.utils import CONST_CONTAINER

class ClientFortMgr(object):

    class WIZARD_PROGRESS(CONST_CONTAINER):
        NO_PROGRESS = 0
        FIRST_DIRECTION = 1
        FIRST_BUILDING = 2
        FIRST_TRANSPORTATION = 3
        COMPLETED = FIRST_TRANSPORTATION

    def __init__(self, account = None):
        self.__eManager = Event.EventManager()
        self.onFortResponseReceived = Event.Event(self.__eManager)
        self.onFortUpdateReceived = Event.Event(self.__eManager)
        self.onFortStateChanged = Event.Event(self.__eManager)
        self.__account = account
        self._fort = ClientFortifiedRegion()
        self.__requestID = 0
        self.state = None
        return

    def __callFortMethod(self, *args):
        LOG_DAN('base.callFortMethod', args)
        self.__account.base.callFortMethod(*args)

    def _setAccount(self, account = None):
        self.__account = account

    def clear(self):
        self.__account = None
        self.__eManager.clear()
        self._fort.clear()
        return

    def __getNextRequestID(self):
        self.__requestID += 1
        return self.__requestID

    def onFortReply(self, reqID, resultCode, resultString):
        LOG_DAN('onFortReply: reqID=%s, resultCode=%s, resultString=%r' % (reqID, resultCode, resultString))
        self.onFortResponseReceived(reqID, resultCode, resultString)

    def onFortUpdate(self, packedOps, packedUpdate):
        LOG_DAN('onFortUpdate: packedOps len=%s, packedUpdate len=%s' % (len(packedOps), len(packedUpdate)))
        if packedUpdate:
            self._fort.unpack(packedUpdate)
        elif packedOps:
            self._fort.unpackOps(packedOps)
        self.onFortUpdateReceived()
        LOG_DAN('after onFortUpdate:', self._fort)

    def onFortStateDiff(self, newState):
        LOG_DAN('onFortStateDiff: state %s (was %s)' % (newState, self.state))
        self.state = newState
        self.onFortStateChanged()

    def create(self):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.CREATE, 0, 0, 0)
        return requestID

    def delete(self):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.DELETE, 0, 0, 0)
        return requestID

    def subscribe(self):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.SUBSCRIBE, 0, 0, 0)
        return requestID

    def unsubscribe(self):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.UNSUBSCRIBE, 0, 0, 0)
        return requestID

    def addBuilding(self, buildingTypeID, dir, pos):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.ADD_BUILDING, buildingTypeID, dir, pos)
        return requestID

    def delBuilding(self, buildingTypeID):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.DEL_BUILDING, buildingTypeID, 0, 0)
        return requestID

    def contribute(self, resCount):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.CONTRIBUTE, resCount, 0, 0)
        return requestID

    def upgrade(self, buildingTypeID):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.UPGRADE, buildingTypeID, 0, 0)
        return requestID

    def transport(self, fromBuildingTypeID, toBuildingTypeID, resCount):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.TRANSPORT, fromBuildingTypeID, toBuildingTypeID, resCount)
        return requestID

    def attach(self, buildingTypeID):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.ATTACH, 0, buildingTypeID, 0)
        return requestID

    def addOrder(self, buildingTypeID, count):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.ADD_ORDER, buildingTypeID, count, 0)
        return requestID

    def activateOrder(self, orderTypeID):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.ACTIVATE_ORDER, orderTypeID, 0, 0)
        return requestID

    def openDir(self, direction):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.OPEN_DIR, direction, 0, 0)
        return requestID

    def closeDir(self, direction):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.CLOSE_DIR, direction, 0, 0)
        return requestID

    def createSortie(self, divisionLevel = 10):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.CREATE_SORTIE, divisionLevel, 0, 0)
        return requestID

    def getSortieData(self, unitMgrID, peripheryID):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.GET_SORTIE_DATA, unitMgrID, peripheryID, 0)
        return requestID

    def changeDefHour(self, defHour):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.CHANGE_DEF_HOUR, defHour, 0, 0)
        return requestID

    def changeOffDay(self, offDay):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.CHANGE_OFF_DAY, offDay, 0, 0)
        return requestID

    def changePeriphery(self, peripheryID):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.CHANGE_PERIPHERY, peripheryID, 0, 0)
        return requestID

    def changeVacation(self, timeVacationStart, timeVacationDuration):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.CHANGE_VACATION, timeVacationStart, timeVacationDuration, 0)
        return requestID

    def setDevMode(self, isOn = True):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.SET_DEV_MODE, int(isOn), 0, 0)
        return requestID

    def addTimeShift(self, timeShiftSeconds = 3600):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.ADD_TIME_SHIFT, timeShiftSeconds, 0, 0)
        return requestID

    def keepalive(self):
        requestID = self.__getNextRequestID()
        self.__callFortMethod(requestID, FORT_CLIENT_METHOD.KEEPALIVE, 0, 0, 0)
        return requestID

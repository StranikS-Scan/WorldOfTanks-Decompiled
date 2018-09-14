# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/ClientFortMgr.py
from FortifiedRegionBase import FORT_CLIENT_METHOD, makeDirPosByte, SECONDS_PER_DAY, SECONDS_PER_HOUR, ALL_DIRS
from ClientFortifiedRegion import ClientFortifiedRegion
import Event
from debug_utils import LOG_DEBUG, LOG_DEBUG, LOG_ERROR
import time
import fortified_regions

class ClientFortMgr(object):

    def __init__(self, account=None):
        self.__eManager = Event.EventManager()
        self.onFortResponseReceived = Event.Event(self.__eManager)
        self.onFortUpdateReceived = Event.Event(self.__eManager)
        self.onFortStateChanged = Event.Event(self.__eManager)
        self.onFortPublicInfoReceived = Event.Event(self.__eManager)
        self.__account = account
        self._fort = ClientFortifiedRegion()
        self.__requestID = 0
        self.state = None
        self.__lockedForSubscribe = {}
        return

    def __callFortMethod(self, *args):
        requestID = self.__getNextRequestID()
        LOG_DEBUG('base.callFortMethod', requestID, args)
        self.__account.base.accountFortConnector_callFortMethod(requestID, *args)
        return requestID

    def callCustomFortMethod(self, *args):
        return self.__callFortMethod(*args)

    def _setAccount(self, account=None):
        self._fort.setAccount(account)
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
        LOG_DEBUG('onFortReply: reqID=%s, resultCode=%s, resultString=%r' % (reqID, resultCode, resultString))
        if reqID in self.__lockedForSubscribe:
            del self.__lockedForSubscribe[reqID]
        self.onFortResponseReceived(reqID, resultCode, resultString)

    def onFortUpdate(self, packedOps, packedUpdate):
        LOG_DEBUG('onFortUpdate: packedOps len=%s, packedUpdate len=%s' % (len(packedOps), len(packedUpdate)))
        isFullUpdate = False
        if packedUpdate:
            self._fort.unpack(packedUpdate)
            isFullUpdate = True
        elif packedOps:
            self._fort.unpackOps(packedOps)
        self._fort.refresh()
        self.onFortUpdateReceived(isFullUpdate)
        LOG_DEBUG('after onFortUpdate:', self._fort)

    def onFortStateDiff(self, newState):
        LOG_DEBUG('onFortStateDiff: state %s (was %s)' % (newState, self.state))
        self.state = newState
        self.onFortStateChanged()

    def create(self):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CREATE, 0, 0, 0)

    def delete(self):
        return self.__callFortMethod(FORT_CLIENT_METHOD.DELETE, 0, 0, 0)

    def subscribe(self):
        if self.__lockedForSubscribe:
            assert len(self.__lockedForSubscribe) > 1, 'multiple createOrJoinFortBattle call'
            return self.__lockedForSubscribe.keys()[0]
        return self.__callFortMethod(FORT_CLIENT_METHOD.SUBSCRIBE, 0, 0, 0)

    def unsubscribe(self):
        return self.__callFortMethod(FORT_CLIENT_METHOD.UNSUBSCRIBE, 0, 0, 0)

    def addBuilding(self, buildingTypeID, dir, pos):
        return self.__callFortMethod(FORT_CLIENT_METHOD.ADD_BUILDING, buildingTypeID, dir, pos)

    def delBuilding(self, buildingTypeID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.DEL_BUILDING, buildingTypeID, 0, 0)

    def contribute(self, resCount):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CONTRIBUTE, resCount, 0, 0)

    def dmgBuilding(self, buildingTypeID, damage):
        return self.__callFortMethod(FORT_CLIENT_METHOD.DMG_BUILDING, buildingTypeID, damage, 0)

    def deletePlannedBattles(self, timeStart=1, timeFinish=2000000000, dir=ALL_DIRS):
        return self.__callFortMethod(FORT_CLIENT_METHOD.DELETE_PLANNED_BATTLES, timeStart, timeFinish, dir)

    def changeAttackResult(self, attackResult, attackResource, attackTime):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CHANGE_ATTACK_RESULT, attackResult, attackResource, attackTime)

    def upgrade(self, buildingTypeID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.UPGRADE, buildingTypeID, 0, 0)

    def transport(self, fromBuildingTypeID, toBuildingTypeID, resCount):
        return self.__callFortMethod(FORT_CLIENT_METHOD.TRANSPORT, fromBuildingTypeID, toBuildingTypeID, resCount)

    def attach(self, buildingTypeID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.ATTACH, 0, buildingTypeID, 0)

    def addOrder(self, buildingTypeID, count):
        return self.__callFortMethod(FORT_CLIENT_METHOD.ADD_ORDER, buildingTypeID, count, 0)

    def activateOrder(self, orderTypeID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.ACTIVATE_ORDER, orderTypeID, 0, 0)

    def openDir(self, direction):
        return self.__callFortMethod(FORT_CLIENT_METHOD.OPEN_DIR, direction, 0, 0)

    def closeDir(self, direction):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CLOSE_DIR, direction, 0, 0)

    def createSortie(self, divisionLevel=10):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CREATE_SORTIE, divisionLevel, 0, 0)

    def createOrJoinFortBattle(self, battleID, slotIdx=-1):
        requestID = self.__callFortMethod(FORT_CLIENT_METHOD.CREATE_JOIN_FORT_BATTLE, battleID, slotIdx, 0)
        self.__lockedForSubscribe[requestID] = FORT_CLIENT_METHOD.CREATE_JOIN_FORT_BATTLE
        return requestID

    def _scheduleBattle(self, battleID, direction, isDefence, attackTime):
        if direction <= 0:
            LOG_ERROR('_scheduleBattle: Bad direction (should be >0)')
            return
        if isDefence:
            direction = -direction
        return self.__callFortMethod(FORT_CLIENT_METHOD.SCHEDULE_FORT_BATTLE, battleID, direction, attackTime)

    def getSortieData(self, unitMgrID, peripheryID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.GET_SORTIE_DATA, unitMgrID, peripheryID, 0)

    def getFortBattleData(self, battleID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.GET_FORT_BATTLE_DATA, battleID, 0, 0)

    def changeDefHour(self, defHour):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CHANGE_DEF_HOUR, defHour, 0, 0)

    def shutdownDefHour(self):
        return self.__callFortMethod(FORT_CLIENT_METHOD.SHUTDOWN_DEF_HOUR, 0, 0, 0)

    def cancelDefHourShutdown(self):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CANCEL_SHUTDOWN, 0, 0, 0)

    def changeOffDay(self, offDay):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CHANGE_OFF_DAY, offDay, 0, 0)

    def changePeriphery(self, peripheryID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CHANGE_PERIPHERY, peripheryID, 0, 0)

    def changeVacation(self, timeVacationStart, timeVacationDuration):
        return self.__callFortMethod(FORT_CLIENT_METHOD.CHANGE_VACATION, timeVacationStart, timeVacationDuration, 0)

    def setDevMode(self, isOn=True, fortBattleMgrDevMode=False):
        return self.__callFortMethod(FORT_CLIENT_METHOD.SET_DEV_MODE, int(isOn), int(fortBattleMgrDevMode), 0)

    def addTimeShift(self, timeShiftSeconds=3600):
        return self.__callFortMethod(FORT_CLIENT_METHOD.ADD_TIME_SHIFT, timeShiftSeconds, 0, 0)

    def keepalive(self):
        return self.__callFortMethod(FORT_CLIENT_METHOD.KEEPALIVE, 0, 0, 0)

    def onResponseFortPublicInfo(self, requestID, errorID, resultSet):
        self.onFortPublicInfoReceived(requestID, errorID, resultSet)

    def getEnemyClanCard(self, enemyClanDBID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.GET_ENEMY_CLAN_CARD, enemyClanDBID, 0, 0)

    def addFavorite(self, clanDBID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.ADD_FAVORITE, clanDBID, 0, 0)

    def removeFavorite(self, clanDBID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.REMOVE_FAVORITE, clanDBID, 0, 0)

    def planAttack(self, enemyClanDBID, timeAttack, dirFrom, dirTo):
        dirFromToByte = makeDirPosByte(dirFrom, dirTo)
        if isinstance(timeAttack, basestring):
            try:
                fmt = '%d.%m.%Y %H:%M'
                timeAttack = int(time.mktime(time.strptime(timeAttack, fmt)))
            except:
                LOG_DEBUG('timeAttack should be either int(unixtime) or "%d.%m.%Y %H:%M" format.')
                return

        elif timeAttack < 0:
            defHour = -timeAttack
            timeAttack = self.__getClosestAttackHour(defHour)
            LOG_DEBUG('timeAttack<0: plan attack for earliest possible defHour(%s), timeAttack=%s' % (defHour, timeAttack))
        return self.__callFortMethod(FORT_CLIENT_METHOD.PLAN_ATTACK, enemyClanDBID, timeAttack, dirFromToByte)

    def activateConsumable(self, consumableTypeID, slotIndex=-1):
        return self.__callFortMethod(FORT_CLIENT_METHOD.ACTIVATE_CONSUMABLE, 0, consumableTypeID, slotIndex)

    def returnConsumable(self, consumableTypeID):
        return self.__callFortMethod(FORT_CLIENT_METHOD.DEACTIVATE_CONSUMABLE, 0, consumableTypeID, 0)

    def __getClosestAttackHour(self, defHour):
        t = self._fort._getTime() + fortified_regions.g_cache.attackPreorderTime
        nextDayDefHour = t - t % SECONDS_PER_DAY + defHour * SECONDS_PER_HOUR
        if nextDayDefHour < t:
            nextDayDefHour += SECONDS_PER_DAY
        return nextDayDefHour

    def unlockDir(self, dir):
        return self.__callFortMethod(FORT_CLIENT_METHOD.DEBUG_UNLOCK_DIR, dir, 0, 0)

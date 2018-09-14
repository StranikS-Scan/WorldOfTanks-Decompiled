# Embedded file name: scripts/client/gui/shared/fortifications/fort_seqs.py
import random
import time
import weakref
import calendar
import BigWorld
from collections import namedtuple
import dossiers2
from helpers import html
from FortifiedRegionBase import NOT_ACTIVATED, FORT_ATTACK_RESULT
from messenger.ext import passCensor
from constants import FORT_SCOUTING_DATA_FILTER, FORT_MAX_ELECTED_CLANS, FORT_SCOUTING_DATA_ERROR
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
import fortified_regions
from shared_utils import CONST_CONTAINER, isEmpty
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control.items.sortie_items import getDivisionNameByType
from gui.shared.fortifications.context import RequestSortieUnitCtx, FortPublicInfoCtx, RequestClanCardCtx
from gui.shared.fortifications.settings import FORT_REQUEST_TYPE
from gui.shared.gui_items.dossier import FortDossier
from gui.shared.utils.decorators import ReprInjector
from helpers import time_utils
from helpers.time_utils import DaysAvailabilityIterator
from ids_generators import SequenceIDGenerator

class BATTLE_ITEM_TYPE(CONST_CONTAINER):
    UNKNOWN = 0
    ATTACK = 1
    DEFENCE = 2


def getDivisionSettings(name):
    import fortified_regions
    division = None
    divisions = fortified_regions.g_cache.divisions
    if name in divisions:
        division = fortified_regions.g_cache.divisions[name]
    else:
        LOG_ERROR('Name of division is not valid', name)
    return division


_SortieItemData = namedtuple('_SortieItemData', ('cmdrDBID',
 'rosterTypeID',
 'unitState',
 'count',
 'maxCount',
 'timestamp',
 'igrType',
 'cmdrName',
 'strComment'))

class SortieItem(object):

    def __init__(self, sortieID, itemData):
        super(SortieItem, self).__init__()
        self._sortieID = sortieID
        self._isDirty = True
        self.itemData = self._makeItemData(itemData)

    def __repr__(self):
        return 'SortieItem(sortieID = {0!r:s}, dirty = {1!r:s}, data = {2!r:s})'.format(self._sortieID, self._isDirty, self.itemData)

    def clear(self):
        self.unitMgrID = 0
        self.itemData = None
        return

    def filter(self, rosterTypeID):
        return rosterTypeID == 0 or self.itemData.rosterTypeID == rosterTypeID

    def getIgrType(self):
        return self.itemData.igrType

    def getID(self):
        return self._sortieID

    def getDivision(self):
        return self.itemData.rosterTypeID

    def getDivisionName(self):
        return getDivisionNameByType(self.itemData.rosterTypeID)

    def getCommanderFullName(self):
        return self.itemData.cmdrName

    def getCommanderDatabaseID(self):
        return self.itemData.cmdrDBID

    def getFlags(self):
        return self.itemData.unitState

    def getDescription(self):
        return passCensor(self.itemData.strComment)

    def _makeItemData(self, itemData):
        supportedLen = len(_SortieItemData._fields)
        unsupportedData = itemData[supportedLen:]
        itemData = itemData[:supportedLen]
        if unsupportedData:
            LOG_ERROR('Client got unsupported data from server: ', unsupportedData)
        return _SortieItemData(*itemData)

    def _updateItemData(self, itemData):
        newData = self._makeItemData(itemData)
        if self.itemData.timestamp != newData.timestamp:
            self._isDirty = True
        self.itemData = newData


class SortiesCache(object):
    __selectedID = (0, 0)
    __rosterTypeID = 0

    def __init__(self, controller):
        self.__controller = weakref.proxy(controller)
        self.__idGen = SequenceIDGenerator()
        self.__cache = {}
        self.__idToIndex = {}
        self.__indexToID = {}
        self.__selectedUnit = None
        self.__isRequestInProcess = False
        self.__cooldownRequest = None
        return

    def __del__(self):
        LOG_DEBUG('Sortie cache deleted:', self)

    def clear(self):
        self.__controller = None
        self.__cache.clear()
        self.__idToIndex.clear()
        self.__indexToID.clear()
        self.__selectedUnit = None
        if self.__cooldownRequest is not None:
            BigWorld.cancelCallback(self.__cooldownRequest)
            self.__cooldownRequest = None
        return

    def start(self):
        fort = self.__controller.getFort()
        if fort:
            fort.onSortieChanged += self.__fort_onSortieChanged
            fort.onSortieRemoved += self.__fort_onSortieRemoved
            fort.onSortieUnitReceived += self.__fort_onSortieUnitReceived
            self.__cache = self.__buildCache()
        else:
            LOG_ERROR('Client fort is not found')

    def stop(self):
        fort = self.__controller.getFort()
        if fort:
            fort.onSortieChanged -= self.__fort_onSortieChanged
            fort.onSortieRemoved -= self.__fort_onSortieRemoved
            fort.onSortieUnitReceived -= self.__fort_onSortieUnitReceived
        self.clear()

    def setController(self, controller):
        self.__controller = weakref.proxy(controller)

    @property
    def isRequestInProcess(self):
        return self.__isRequestInProcess

    @classmethod
    def getSelectedID(cls):
        return cls.__selectedID

    def clearSelectedID(self):
        self.__selectedUnit = None
        self._setSelectedID((0, 0))
        return

    def setSelectedID(self, selectedID):
        if selectedID not in self.__cache:
            LOG_WARNING('Item is not found in cache', selectedID)
            return False
        else:
            self.__selectedUnit = None
            self._setSelectedID(selectedID)
            if BigWorld.player().isLongDisconnectedFromCenter:
                self.__controller._listeners.notify('onSortieUnitReceived', self.__getClientIdx(selectedID))
                return True
            unit = self.getSelectedUnit()
            if unit and not self.__cache[selectedID]._isDirty:
                self.__controller._listeners.notify('onSortieUnitReceived', self.__getClientIdx(selectedID))
            else:
                self._requestSortieUnit(selectedID)
            return True

    @classmethod
    def getRosterTypeID(cls):
        return cls.__rosterTypeID

    def setRosterTypeID(self, rosterTypeID):
        result = self._setRosterTypeID(rosterTypeID)
        if result:
            self.__cache = self.__buildCache()
        return result

    def getItem(self, sortieID):
        try:
            item = self.__cache[sortieID]
        except KeyError:
            LOG_ERROR('Item not found in cache', sortieID)
            item = None

        return item

    def getUnitByIndex(self, index):
        unit = None
        if index in self.__indexToID:
            sortieID = self.__indexToID[index]
            unit = self.__getUnit(sortieID)
        return unit

    def getSelectedUnit(self):
        return self.__getUnit(self.getSelectedID())

    def getIterator(self):
        for item in self.__cache.itervalues():
            if item.filter(self.__rosterTypeID):
                yield item

    def _requestSortieUnit(self, selectedID):
        Waiting.show('fort/sortie/get')
        if self.__cooldownRequest is not None:
            Waiting.hide('fort/sortie/get')
            BigWorld.cancelCallback(self.__cooldownRequest)
            self.__cooldownRequest = None
        ctx = RequestSortieUnitCtx(waitingID='', *selectedID)

        def requester():
            self.__cooldownRequest = None
            self.__isRequestInProcess = True
            self.__controller.request(ctx, self.__requestCallback)
            return

        if self.__controller._cooldown.isInProcess(ctx.getRequestType()):
            self.__cooldownRequest = BigWorld.callback(self.__controller._cooldown.getTime(ctx.getRequestType()), requester)
        else:
            requester()
        return

    @classmethod
    def _setSelectedID(cls, selectedID):
        result = False
        if selectedID != cls.__selectedID and len(selectedID) == 2:
            cls.__selectedID = selectedID
            result = True
        return result

    @classmethod
    def _setRosterTypeID(cls, rosterTypeID):
        result = False
        if rosterTypeID != cls.__rosterTypeID:
            cls.__rosterTypeID = rosterTypeID
            result = True
        return result

    @classmethod
    def _removeStoredData(cls):
        cls.__selectedID = (0, 0)
        cls.__rosterTypeID = 0

    def __buildCache(self):
        cache = {}
        fort = self.__controller.getFort()
        if not fort:
            LOG_WARNING('Client fort is not found')
            return cache
        sorties = fort.getSorties()
        selectedID = self.getSelectedID()
        found = False
        for sortieID, sortie in sorties.iteritems():
            item = SortieItem(sortieID, sortie)
            if not found and item.getID() == selectedID:
                found = True
            cache[sortieID] = item

        if not found:
            self.clearSelectedID()
        return cache

    def __updateItem(self, sortieID, fort):
        sortie = fort.getSortieShortData(*sortieID)
        if sortie is None:
            LOG_ERROR('Sortie is not found', sortieID, fort.sorties)
            return
        else:
            if sortieID in self.__cache:
                item = self.__cache[sortieID]
                item._updateItemData(sortie)
                if item._isDirty and self.__selectedID == item.getID() and item.filter(self.getRosterTypeID()):
                    self.__selectedUnit = None
                    self._requestSortieUnit(sortieID)
            else:
                item = SortieItem(sortieID, sortie)
                self.__cache[sortieID] = item
            return item

    def __requestCallback(self, _):
        Waiting.hide('fort/sortie/get')
        self.__isRequestInProcess = False

    def __removeItem(self, sortieID):
        result = False
        if sortieID in self.__cache:
            self.__cache.pop(sortieID)
            result = True
        if self.getSelectedID() == sortieID:
            self.clearSelectedID()
        clientIdx = self.__idToIndex.pop(sortieID, None)
        if clientIdx is not None:
            self.__indexToID.pop(clientIdx, None)
        return result

    def __getClientIdx(self, sortieID):
        if sortieID == (0, 0):
            return 0
        if sortieID not in self.__idToIndex:
            clientIdx = self.__idGen.next()
            self.__idToIndex[sortieID] = clientIdx
            self.__indexToID[clientIdx] = sortieID
        else:
            clientIdx = self.__idToIndex[sortieID]
        return clientIdx

    def __getUnit(self, sortieID):
        fort = self.__controller.getFort()
        if not fort:
            LOG_WARNING('Client fort is not found')
            return
        else:
            isSelected = self.getSelectedID() == sortieID
            if isSelected and self.__selectedUnit is not None:
                return self.__selectedUnit
            unit = fort.getSortieUnit(*sortieID)
            if isSelected:
                self.__selectedUnit = unit
            return unit

    def __fort_onSortieChanged(self, unitMgrID, peripheryID):
        fort = self.__controller.getFort()
        sortieID = (unitMgrID, peripheryID)
        if fort:
            item = self.__updateItem(sortieID, fort)
            if item:
                self.__controller._listeners.notify('onSortieChanged', self, item)

    def __fort_onSortieRemoved(self, unitMgrID, peripheryID):
        sortieID = (unitMgrID, peripheryID)
        if self.__removeItem(sortieID):
            self.__controller._listeners.notify('onSortieRemoved', self, sortieID)

    def __fort_onSortieUnitReceived(self, unitMgrID, peripheryID):
        fort = self.__controller.getFort()
        sortieID = (unitMgrID, peripheryID)
        if fort:
            if unitMgrID in self.__cache:
                self.__cache[sortieID]._isDirty = False
            if self.getSelectedID() == sortieID:
                self.__selectedUnit = None
            self.__controller._listeners.notify('onSortieUnitReceived', self.__getClientIdx(sortieID))
        return


_FortBattleItemData = namedtuple('_FortBattleItemData', ('defenderClanDBID',
 'attackerClanDBID',
 'direction',
 'isDefence',
 'attackTime',
 'roundStart',
 'attackerBuildList',
 'defenderBuildList',
 'attackerFullBuildList',
 'defenderFullBuildList',
 'battleResultList',
 'prevBuildNum',
 'currentBuildNum',
 'isEnemyReadyForBattle',
 'isBattleRound',
 'canUseEquipments',
 'division'))

@ReprInjector.simple(('_battleID', 'battleID'), ('_peripheryID', 'peripheryID'), ('itemData', 'data'), ('additionalData', 'additional'))

class BattleItem(object):

    def __init__(self, battleID, itemData, additionalData):
        super(BattleItem, self).__init__()
        self._battleID = battleID
        self._isDirty = True
        self.itemData = self._makeItemData(itemData)
        self.additionalData = additionalData

    def clear(self):
        self.unitMgrID = 0
        self.itemData = None
        self.additionalData = None
        return

    def filter(self):
        return True

    def getID(self):
        return self._battleID

    def getPeripheryID(self):
        return self.additionalData.getPeripheryID()

    def isDefence(self):
        return self.itemData.isDefence

    def getDirection(self):
        return self.itemData.direction

    def getAttackTime(self):
        return self.itemData.attackTime

    def getAttackFinishTime(self):
        return self.getAttackTime() + time_utils.ONE_HOUR

    def getAttackTimeLeft(self):
        return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.getAttackTime()))

    def getRoundStartTime(self):
        if self.itemData.roundStart:
            return self.itemData.roundStart
        return self.getAttackTime()

    def getRoundFinishTime(self):
        return self.getAttackFinishTime()

    def getRoundStartTimeLeft(self):
        return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.getRoundStartTime()))

    def getAttackerBuildList(self):
        return self.itemData.attackerBuildList or ()

    def getDefenderBuildList(self):
        return self.itemData.defenderBuildList or ()

    def getAttackerFullBuildList(self):
        return self.itemData.attackerFullBuildList or ()

    def getDefenderFullBuildList(self):
        return self.itemData.defenderFullBuildList or ()

    def getAllBuildList(self):
        result = []
        result += map(lambda item: (item, False), self.getDefenderBuildList())
        result += map(lambda item: (item, True), reversed(self.getAttackerBuildList()))
        return result

    def getLootedBuildList(self):
        result = []
        curIdx = self.getCurrentBuildNum()
        prevIdx = self.getPrevBuildNum()
        fightStartsFromCurIdx = len(self.getDefenderBuildList()) - 1
        fightStartsFromPrevIdx = fightStartsFromCurIdx + 1
        if not (curIdx == fightStartsFromCurIdx and prevIdx == fightStartsFromPrevIdx or curIdx == fightStartsFromPrevIdx and prevIdx == fightStartsFromCurIdx):
            for index, (buildingTypeID, isAttack) in enumerate(self.getAllBuildList()):
                if isAttack:
                    if index > prevIdx:
                        continue
                    if index == prevIdx and prevIdx > curIdx:
                        continue
                else:
                    if index < prevIdx:
                        continue
                    if index == prevIdx and prevIdx < curIdx:
                        continue
                result.append((buildingTypeID, isAttack))

        return result

    def getPrevBuildNum(self):
        return self.itemData.prevBuildNum

    def getCurrentBuildNum(self):
        return self.itemData.currentBuildNum

    def getOpponentClanInfo(self):
        return self.additionalData.getOpponentClanInfo()

    def isEnemyReadyForBattle(self):
        return self.itemData.isEnemyReadyForBattle

    def isBattleRound(self):
        return self.itemData.isBattleRound

    def _makeItemData(self, itemData):
        unsupportedFields = set(itemData) - set(_FortBattleItemData._fields)
        unsupportedData = {}
        if unsupportedFields:
            for f in unsupportedFields:
                unsupportedData[f] = itemData.pop(f)

            LOG_ERROR('Client got unsupported data from server: ', unsupportedData)
        return _FortBattleItemData(**itemData)

    def _updateItemData(self, itemData):
        newData = self._makeItemData(itemData)
        if self.itemData != newData:
            self._isDirty = True
        self.itemData = newData


class FortBattlesCache(object):
    __selectedID = 0

    def __init__(self, controller):
        self.__controller = weakref.proxy(controller)
        self.__idGen = SequenceIDGenerator()
        self.__cache = {}
        self.__idToIndex = {}
        self.__indexToID = {}
        self.__selectedUnit = None
        self.__isRequestInProcess = False
        return

    def __del__(self):
        LOG_DEBUG('Fort battles cache deleted:', self)

    def clear(self):
        self.__controller = None
        self.__cache.clear()
        self.__idToIndex.clear()
        self.__indexToID.clear()
        self.__selectedUnit = None
        return

    def start(self):
        fort = self.__controller.getFort()
        if fort:
            fort.onFortBattleChanged += self.__fort_onFortBattleChanged
            fort.onFortBattleRemoved += self.__fort_onFortBattleRemoved
            fort.onFortBattleUnitReceived += self.__fort_onFortBattleUnitReceived
            fort.onEnemyStateChanged += self.__fort_onEnemyStateChanged
            self.__cache = self.__buildCache()
        else:
            LOG_ERROR('Client fort is not found')

    def stop(self):
        fort = self.__controller.getFort()
        if fort:
            fort.onFortBattleChanged -= self.__fort_onFortBattleChanged
            fort.onFortBattleRemoved -= self.__fort_onFortBattleRemoved
            fort.onFortBattleUnitReceived -= self.__fort_onFortBattleUnitReceived
            fort.onEnemyStateChanged -= self.__fort_onEnemyStateChanged
        self.clear()

    @property
    def isRequestInProcess(self):
        return self.__isRequestInProcess

    @classmethod
    def getSelectedID(cls):
        return cls.__selectedID

    def getSelectedIdx(self):
        return self.__getClientIdx(self.getSelectedID())

    def clearSelectedID(self):
        self.__selectedUnit = None
        self._setSelectedID(0)
        return

    def setSelectedID(self, selectedID):
        if selectedID not in self.__cache:
            LOG_WARNING('Item is not found in cache', selectedID)
            return False
        else:
            self.__selectedUnit = None
            return self._setSelectedID(selectedID)

    def getItem(self, battleID):
        try:
            item, fortBattle = self.__cache[battleID]
        except KeyError:
            LOG_ERROR('Item not found in cache', battleID)
            item = None
            fortBattle = None

        return (item, fortBattle)

    def getUnitByIndex(self, index):
        unit = None
        if index in self.__indexToID:
            battleID = self.__indexToID[index]
            unit = self.__getUnit(battleID)
        return unit

    def getSelectedUnit(self):
        return self.__getUnit(self.getSelectedID())

    def getIterator(self):
        for item, battleItem in self.__cache.itervalues():
            if item.filter():
                yield (item, battleItem)

    @classmethod
    def _setSelectedID(cls, selectedID):
        result = False
        if selectedID != cls.__selectedID:
            cls.__selectedID = selectedID
            result = True
        return result

    @classmethod
    def _removeStoredData(cls):
        cls.__selectedID = (0, 0)

    def __buildCache(self):
        cache = {}
        fort = self.__controller.getFort()
        if not fort:
            LOG_WARNING('Client fort is not found')
            return cache
        fortBattles = fort.getAttacksAndDefencesIn(timePeriod=2 * time_utils.ONE_WEEK)
        selectedID = self.getSelectedID()
        found = False
        for item in fortBattles:
            battleID = item.getBattleID()
            if not found and battleID == selectedID:
                found = True
            battleItem = fort.getBattle(battleID)
            cache[battleID] = (item, battleItem)

        if not found:
            self.clearSelectedID()
        return cache

    def __updateItem(self, battleID, fort):
        item = fort.getBattleItemByBattleID(battleID)
        if item is None:
            LOG_ERROR('Fort battle is not found', battleID, fort.attacks, fort.defences)
            return (None, None)
        else:
            fortBattle = fort.getBattle(battleID)
            self.__cache[battleID] = (item, fortBattle)
            if self.getSelectedID() == battleID:
                self.__selectedUnit = None
            return (item, fortBattle)

    def __requestCallback(self, _):
        self.__isRequestInProcess = False

    def __removeItem(self, battleID):
        result = False
        if battleID in self.__cache:
            self.__cache.pop(battleID)
            result = True
        if self.getSelectedID() == battleID:
            self.clearSelectedID()
        clientIdx = self.__idToIndex.pop(battleID, None)
        if clientIdx is not None:
            self.__indexToID.pop(clientIdx, None)
        return result

    def __getClientIdx(self, battleID):
        if battleID == 0:
            return 0
        if battleID not in self.__idToIndex:
            clientIdx = self.__idGen.next()
            self.__idToIndex[battleID] = clientIdx
            self.__indexToID[clientIdx] = battleID
        else:
            clientIdx = self.__idToIndex[battleID]
        return clientIdx

    def __getUnit(self, battleID):
        fort = self.__controller.getFort()
        if not fort:
            LOG_WARNING('Client fort is not found')
            return
        else:
            isSelected = battleID == self.getSelectedID()
            if isSelected and self.__selectedUnit is not None:
                return self.__selectedUnit
            unit = fort.getFortBattleUnit(battleID)
            if isSelected:
                self.__selectedUnit = unit
            return unit

    def __fort_onEnemyStateChanged(self, battleID, isReady):
        fort = self.__controller.getFort()
        if fort:
            item, battleItem = self.__updateItem(battleID, fort)
            if item:
                self.__controller._listeners.notify('onFortBattleChanged', self, item, battleItem)

    def __fort_onFortBattleChanged(self, battleID):
        fort = self.__controller.getFort()
        if fort:
            item, battleItem = self.__updateItem(battleID, fort)
            if item:
                self.__controller._listeners.notify('onFortBattleChanged', self, item, battleItem)

    def __fort_onFortBattleRemoved(self, battleID):
        if self.__removeItem(battleID):
            self.__controller._listeners.notify('onFortBattleRemoved', self, battleID)

    def __fort_onFortBattleUnitReceived(self, battleID):
        fort = self.__controller.getFort()
        if fort:
            if self.__selectedID == battleID:
                self.__selectedUnit = None
            self.__controller._listeners.notify('onFortBattleUnitReceived', self.__getClientIdx(battleID))
        return


class IClanFortInfo(object):

    def getClanDBID(self):
        return None

    def getStartDefHour(self):
        return NOT_ACTIVATED

    def getFinishDefHour(self):
        return NOT_ACTIVATED

    def getDefencePeriod(self):
        if self.getStartDefHour() != NOT_ACTIVATED:
            return (time_utils.getTimeTodayForUTC(hour=self.getStartDefHour()), time_utils.getTimeTodayForUTC(hour=self.getFinishDefHour()))
        else:
            return (None, None)

    def getLocalDefHour(self):
        from gui.shared.fortifications.fort_helpers import adjustDefenceHourToLocal
        return adjustDefenceHourToLocal(self.getStartDefHour())

    def getOffDay(self):
        return NOT_ACTIVATED

    def getVacationPeriod(self):
        return (None, None)

    def getTimeNewDefHour(self):
        return None

    def getTimeNewOffDay(self):
        return None

    def getNewDefHour(self):
        return NOT_ACTIVATED

    def getNewOffDay(self):
        return NOT_ACTIVATED

    def getLocalOffDay(self):
        from gui.shared.fortifications.fort_helpers import adjustOffDayToLocal
        return adjustOffDayToLocal(self.getOffDay(), self.getLocalDefHour()[0])

    def getDefHourFor(self, timestamp):
        if self.getTimeNewDefHour() and timestamp >= self.getTimeNewDefHour():
            from gui.shared.fortifications.fort_helpers import adjustDefenceHourToLocal
            return adjustDefenceHourToLocal(self.getNewDefHour(), timestamp)
        from gui.shared.fortifications.fort_helpers import adjustDefenceHourToLocal
        return adjustDefenceHourToLocal(self.getStartDefHour(), timestamp)

    def getLocalOffDayFor(self, timestamp):
        if self.getTimeNewOffDay() and timestamp >= self.getTimeNewOffDay():
            from gui.shared.fortifications.fort_helpers import adjustOffDayToLocal
            return adjustOffDayToLocal(self.getNewOffDay(), self.getDefHourFor(timestamp))
        from gui.shared.fortifications.fort_helpers import adjustOffDayToLocal
        return adjustOffDayToLocal(self.getOffDay(), self.getDefHourFor(timestamp)[0])

    def isAvailableForAttack(self, timestamp):
        return (False, True)


_PublicInfoItemData = namedtuple('_PublicInfoItemData', ('clanDBID',
 'clanName',
 'clanAbbrev',
 'clanMotto',
 'clanDescr',
 'vacationStart',
 'vacationFinish',
 'startDefHour',
 'finishDefHour',
 'offDay',
 'homePeripheryID',
 'fortLevel',
 'avgBuildingLevel10',
 'profitFactor10',
 'battleCountForFort',
 'nextVacationStart',
 'nextVacationFinish',
 'nextStartDefHour',
 'nextFinishDefHour',
 'nextOffDay',
 'defHourChangeDay',
 'offDayChangeDay'))

@ReprInjector.simple(('__isFavorite', 'isFavorite'), ('itemData', 'data'))

class PublicInfoItem(IClanFortInfo):

    def __init__(self, itemData):
        super(PublicInfoItem, self).__init__()
        self.itemData = self._makeItemData(itemData)

    def clear(self):
        self.itemData = None
        return

    def filter(self, filterType, favorites):
        if filterType == FORT_SCOUTING_DATA_FILTER.ELECT and self.getClanDBID() not in favorites:
            return False
        return True

    def getClanDBID(self):
        return self.itemData.clanDBID

    def getClanName(self):
        return passCensor(html.escape(self.itemData.clanName))

    def getClanAbbrev(self):
        return self.itemData.clanAbbrev

    def getClanMotto(self):
        return passCensor(html.escape(self.itemData.clanMotto))

    def getVacationPeriod(self):
        if self.itemData.vacationStart is not None and self.itemData.vacationFinish is not None:
            start = time_utils.getTimestampFromUTC(self.itemData.vacationStart.timetuple())
            finish = time_utils.getTimestampFromUTC(self.itemData.vacationFinish.timetuple())
            return (start, finish)
        else:
            return (None, None)

    def getStartDefHour(self):
        return self.itemData.startDefHour

    def getFinishDefHour(self):
        return self.itemData.finishDefHour

    def getOffDay(self):
        if self.itemData.offDay != NOT_ACTIVATED:
            mysqlDayOfWeekConvertor = (2, 3, 4, 5, 6, 7, 1)
            return mysqlDayOfWeekConvertor.index(self.itemData.offDay)
        return NOT_ACTIVATED

    def getTimeNewDefHour(self):
        if self.itemData.defHourChangeDay is not None:
            return time_utils.getTimestampFromUTC(self.itemData.defHourChangeDay.timetuple())
        else:
            return

    def getTimeNewOffDay(self):
        if self.itemData.defHourChangeDay is not None:
            return time_utils.getTimestampFromUTC(self.itemData.defHourChangeDay.timetuple())
        else:
            return

    def getNewDefHour(self):
        return self.itemData.nextStartDefHour

    def getNewOffDay(self):
        return self.itemData.nextOffDay

    def getHomePeripheryID(self):
        return self.itemData.homePeripheryID

    def getLevel(self):
        return self.itemData.fortLevel

    def getAvgBuildingLevel(self):
        return float(self.itemData.avgBuildingLevel10) / 10

    def getProfitFactor(self):
        return float(self.itemData.profitFactor10) / 10

    def getBattleCount(self):
        return self.itemData.battleCountForFort

    def getAvailability(self):
        return DaysAvailabilityIterator(time_utils.getTimeTodayForLocal(*self.getLocalDefHour()), (self.getLocalOffDay(),), (self.getVacationPeriod(),), fortified_regions.g_cache.attackPreorderTime).next()

    def _makeItemData(self, itemData):
        supportedLen = len(_PublicInfoItemData._fields)
        unsupportedData = itemData[supportedLen:]
        itemData = itemData[:supportedLen]
        if unsupportedData:
            LOG_ERROR('Client got unsupported data from server: ', unsupportedData)
        return _PublicInfoItemData(*itemData)


class PublicInfoCache(object):
    __selectedID = 0

    def __init__(self, controller):
        self.__controller = weakref.proxy(controller)
        self.__idGen = SequenceIDGenerator()
        self.__cache = {}
        self.__idToIndex = {}
        self.__indexToID = {}
        self.__isRequestInProcess = False
        self.__cooldownRequest = None
        self.__firstDefaultQuery = False
        self.__ifDefaultQueryResult = False
        self.__selectedClanCard = None
        self.resetClanAbbrev()
        self.resetFilters()
        return

    def __del__(self):
        LOG_DEBUG('Public info cache deleted:', self)

    def clear(self):
        self.clearSelectedID()
        self.__cache.clear()
        self.__idToIndex.clear()
        self.__indexToID.clear()
        if self.__cooldownRequest is not None:
            BigWorld.cancelCallback(self.__cooldownRequest)
            self.__cooldownRequest = None
        return

    def start(self):
        pass

    def stop(self):
        self.__controller = None
        self.clear()
        return

    def setDefaultFilterData(self, lvlFrom, lvlTo, extStartDefHour, attackDay = NOT_ACTIVATED):
        self.__isFitlerApplied = True
        self.__lvlFrom = lvlFrom
        self.__lvlTo = lvlTo
        self.__extStartDefHour = extStartDefHour
        self.__attackDay = attackDay

    def getDefaultFilterData(self):
        return (self.__lvlFrom,
         self.__lvlTo,
         self.__extStartDefHour,
         self.__attackDay)

    def setFilterType(self, filterType):
        self.__filterType = filterType

    def getFilterType(self):
        return self.__filterType

    def setAbbrevPattern(self, abbrevPattern):
        self.__abbrevPattern = abbrevPattern

    def getAbbrevPattern(self):
        return self.__abbrevPattern

    def reset(self):
        self.resetFilters()
        self.resetClanAbbrev()

    def resetClanAbbrev(self):
        self.__filterType = FORT_SCOUTING_DATA_FILTER.DEFAULT
        self.__abbrevPattern = ''

    def resetFilters(self):
        self.__isFitlerApplied = False
        self.__limit = FORT_MAX_ELECTED_CLANS
        self.__lvlFrom = 5
        self.__lvlTo = 10
        self.__extStartDefHour = NOT_ACTIVATED
        self.__attackDay = NOT_ACTIVATED

    def setDefaultRequestFilters(self):
        self.__isFitlerApplied = False
        self.__filterType = FORT_SCOUTING_DATA_FILTER.DEFAULT
        self.__abbrevPattern = ''
        self.__limit = FORT_MAX_ELECTED_CLANS
        self.__lvlFrom = self.__controller.getFort().level
        self.__lvlTo = self.__controller.getFort().level
        self.__extStartDefHour = NOT_ACTIVATED
        self.__attackDay = NOT_ACTIVATED

    def request(self):
        self.__isRequestInProcess = True
        defenceHourFrom, defenceHourTo, attackDay = self.__adjustTimeToGM()
        self.__controller.request(FortPublicInfoCtx(self.__filterType, self.__abbrevPattern, self.__limit, self.__lvlFrom, self.__lvlTo, defenceHourFrom, defenceHourTo, attackDay, self.__firstDefaultQuery, waitingID='fort/publicInfo/get'), self.__requestCacheCallback)

    @property
    def isRequestInProcess(self):
        return self.__isRequestInProcess

    @classmethod
    def getSelectedID(cls):
        return cls.__selectedID

    def getRequestCacheCooldownInfo(self):
        cooldownMgr = self.__controller._cooldown
        return (cooldownMgr.isInProcess(FORT_REQUEST_TYPE.REQUEST_PUBLIC_INFO), cooldownMgr.getTime(FORT_REQUEST_TYPE.REQUEST_PUBLIC_INFO))

    def clearSelectedID(self):
        self._setSelectedID(0)
        self.__selectedClanCard = None
        if self.__controller:
            self.__controller._listeners.notify('onEnemyClanCardRemoved')
        return

    def setSelectedID(self, selectedID):
        if selectedID not in self.__cache:
            LOG_WARNING('Item is not found in cache', selectedID)
            return False
        self._setSelectedID(selectedID)
        self._requestClanCard(selectedID)
        return True

    def getItem(self, clanDBID):
        try:
            item = self.__cache[clanDBID]
        except KeyError:
            LOG_ERROR('Item not found in cache', clanDBID)
            item = None

        return item

    def getIterator(self):
        for item in self.__cache.itervalues():
            if item.filter(self.__filterType, self.getFavorites()):
                yield item

    def hasResults(self):
        return not isEmpty(self.getIterator())

    def isFilterApplied(self):
        return self.__isFitlerApplied

    def getItemsCount(self):
        return len(tuple(self.getIterator()))

    def getFavorites(self):
        return self.__controller.getFort().favorites

    def ifDefaultQueryResult(self):
        return self.__ifDefaultQueryResult

    def storeSelectedClanCard(self, card):
        self.__selectedClanCard = card

    def getSelectedClanCard(self):
        return self.__selectedClanCard

    def _requestClanCard(self, selectedID):

        def requester():
            self.__cooldownRequest = None
            self.__isRequestInProcess = True
            self.__controller.request(RequestClanCardCtx(selectedID, waitingID=''), self.__requestClanCardCallback)
            return

        if self.__controller._cooldown.isInProcess(FORT_REQUEST_TYPE.REQUEST_CLAN_CARD):
            self.__cooldownRequest = BigWorld.callback(self.__controller._cooldown.getTime(FORT_REQUEST_TYPE.REQUEST_CLAN_CARD), requester)
        else:
            requester()

    @classmethod
    def _setSelectedID(cls, selectedID):
        result = False
        if selectedID != cls.__selectedID:
            cls.__selectedID = selectedID
            result = True
        return result

    @classmethod
    def _removeStoredData(cls):
        cls.__selectedID = 0

    def __requestClanCardCallback(self, result):
        self.__requestCallback(result)
        if not result:
            self.clearSelectedID()

    def __requestCacheCallback(self, result, data = None):
        self.__requestCallback(result)
        if self.__firstDefaultQuery:
            self.__firstDefaultQuery = False
            self.__ifDefaultQueryResult = True
        else:
            self.__ifDefaultQueryResult = False
        data = data or tuple()
        if result != FORT_SCOUTING_DATA_ERROR.COOLDOWN:
            self.__cache = {}
            for item in map(PublicInfoItem, data):
                self.__cache[item.getClanDBID()] = item

    def __requestCallback(self, _):
        self.__isRequestInProcess = False

    def __adjustTimeToGM(self):
        if self.__extStartDefHour != NOT_ACTIVATED:
            attackDay = time_utils.getTimeTodayForLocal(self.__extStartDefHour)
            from gui.shared.fortifications.fort_helpers import adjustDefenceHourToUTC
            defenceHourGMTFrom = adjustDefenceHourToUTC(self.__extStartDefHour)
            defenceHourGMTTo = defenceHourGMTFrom + 1
        else:
            attackDay = calendar.timegm(time.gmtime())
            defenceHourGMTFrom = 0
            defenceHourGMTTo = 24
        if self.__attackDay != NOT_ACTIVATED:
            attackDay += self.__attackDay * time_utils.ONE_DAY
        else:
            startsFrom = 3
            endsAt = 13
            randomDay = random.randint(startsFrom, endsAt)
            attackDay += randomDay * time_utils.ONE_DAY
        return (defenceHourGMTFrom, defenceHourGMTTo, attackDay)


_ClanCardItemData = namedtuple('_ClanCardItemData', ('clanDBID',
 'fortLevel',
 'dirMask',
 'defHour',
 'offDay',
 'vacationStart',
 'vacationFinish',
 'timeNewDefHour',
 'timeNewOffDay',
 'newDefHour',
 'newOffDay',
 'clanName',
 'clanAbbrev',
 'clanDescr',
 'clanMotto',
 'statisticsCompDescr',
 'dictBuildingsBrief',
 'listScheduledAttacks',
 'dictDirOpenAttacks'))

def makeClanCardItemData():
    return _ClanCardItemData(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, '', '', '', '', -1, {}, (), {})


class ClanCardItem(IClanFortInfo):

    def __init__(self, itemData, fort = None):
        super(ClanCardItem, self).__init__()
        self.__fort = fort
        self.itemData = self._makeItemData(itemData)
        self.__setAttacksAndDefenses()

    def __repr__(self):
        return 'ClanCardItem(data = {0!r:s})'.format(self.itemData)

    def clear(self):
        self.itemData = None
        return

    def filter(self):
        return True

    def __setAttacksAndDefenses(self):
        clanID = self.itemData.clanDBID
        currentUserTime = time_utils.getCurrentLocalServerTimestamp()
        self.__upcomingAttacks = self.__fort.getAttacks(clanID, lambda item: item.isPlanned())
        self.__attacksInCooldown = self.__fort.getAttacks(clanID, lambda item: currentUserTime < item.getStartTime() + fortified_regions.g_cache.attackCooldownTime and item.isEnded())
        self.__defencesInCooldown = self.__fort.getDefences(clanID, lambda item: currentUserTime > item.getStartTime() and item.isEnded())

    @property
    def weAreAtWar(self):
        return self.__upcomingAttacks or self.__attacksInCooldown and not self.counterAttacked

    @property
    def upcomingAttack(self):
        if self.__upcomingAttacks:
            return self.__upcomingAttacks[0]
        else:
            return None

    @property
    def closestAttackInCooldown(self):
        if self.__attacksInCooldown:
            return self.__attacksInCooldown[-1]
        else:
            return None

    @property
    def closestDefenseInCooldown(self):
        if self.__defencesInCooldown:
            return self.__defencesInCooldown[-1]
        else:
            return None

    @property
    def counterAttacked(self):
        return self.closestAttackInCooldown is not None and self.closestDefenseInCooldown is not None and self.closestAttackInCooldown.getStartTime() < self.closestDefenseInCooldown.getStartTime() < self.closestAttackInCooldown.getStartTime() + time_utils.ONE_DAY * 7

    def getClanDBID(self):
        return self.itemData.clanDBID

    def getLevel(self):
        return self.itemData.fortLevel

    def getDirMask(self):
        return self.itemData.dirMask

    def getStartDefHour(self):
        return self.itemData.defHour

    def getFinishDefHour(self):
        return self.itemData.defHour + 1

    def getOffDay(self):
        if self.itemData.offDay != NOT_ACTIVATED:
            return self.itemData.offDay
        return NOT_ACTIVATED

    def getVacationPeriod(self):
        return (self.itemData.vacationStart, self.itemData.vacationFinish)

    def getTimeNewDefHour(self):
        return self.itemData.timeNewDefHour

    def getTimeNewOffDay(self):
        return self.itemData.timeNewOffDay

    def getNewDefHour(self):
        return self.itemData.newDefHour

    def getNewOffDay(self):
        return self.itemData.newOffDay

    def getClanName(self):
        return passCensor(html.escape(self.itemData.clanName))

    def getClanAbbrev(self):
        return self.itemData.clanAbbrev

    def getClanDescr(self):
        return passCensor(html.escape(self.itemData.clanDescr))

    def getClanMotto(self):
        return passCensor(html.escape(self.itemData.clanMotto))

    def getStatisticsCompDescr(self):
        return self.itemData.statisticsCompDescr

    def getStatistics(self):
        return FortDossier(dossiers2.getFortifiedRegionsDossierDescr(self.itemData.statisticsCompDescr), True)

    def getDictBuildingsBrief(self):
        return self.itemData.dictBuildingsBrief

    def getListScheduledAttacks(self):
        return self.itemData.listScheduledAttacks

    def getListScheduledAttacksAt(self, start, end):

        def filterThisDay(item):
            timestamp, dir, clanDBID, clanAbbrev = item
            if start <= timestamp < end:
                return True
            return False

        return filter(filterThisDay, self.itemData.listScheduledAttacks)

    def getDictDirOpenAttacks(self):
        return self.itemData.dictDirOpenAttacks

    def getAvailability(self):
        from ClientFortifiedRegion import ATTACK_PLAN_RESULT
        maxPreorderLimit = FORTIFICATION_ALIASES.ACTIVE_EVENTS_FUTURE_LIMIT * time_utils.ONE_DAY
        initialTime = time_utils.getTimeTodayForLocal(*self.getLocalDefHour())
        availableTimestamp = initialTime
        while not self.__fort.canPlanAttackOn(availableTimestamp, self) == ATTACK_PLAN_RESULT.OK:
            if time_utils.getTimeDeltaFromNow(availableTimestamp) <= maxPreorderLimit:
                availableTimestamp += time_utils.ONE_DAY
            else:
                availableTimestamp = initialTime
                break

        currentDayStart, _ = time_utils.getDayTimeBoundsForLocal()
        availableDayStart, _ = time_utils.getDayTimeBoundsForLocal(availableTimestamp)
        return availableTimestamp

    def isAvailableForAttack(self, timestamp):
        hasFreeDirections = False
        for direction in xrange(1, fortified_regions.g_cache.maxDirections + 1):
            if bool(self.getDirMask() & 1 << direction):
                availableTime = self.getDictDirOpenAttacks().get(direction, 0)
                if availableTime <= timestamp:
                    hasFreeDirections = True
                    for _, dir, _, _ in self.getListScheduledAttacksAt(timestamp, timestamp + time_utils.ONE_HOUR):
                        if direction == dir:
                            return (True, hasFreeDirections)

        return (False, hasFreeDirections)

    def _makeItemData(self, itemData):
        try:
            data = _ClanCardItemData(*itemData)
        except TypeError:
            data = makeClanCardItemData()
            LOG_ERROR('Client can not unpack item data of clan card', itemData)

        return data


class _BattleItemAbstract(object):

    def __init__(self, peripheryID, startTime, opponentClanDBID, opponentClanAbbrev, opponentDirection, ourDirection, atkLevel, defLevel, division, battleID, attackResult, attackResource):
        self._peripheryID = peripheryID
        self._startTime = startTime
        self._ourDirection = ourDirection
        self._opponentClanDBID = opponentClanDBID
        self._opponentClanAbbrev = opponentClanAbbrev
        self._opponentDirection = opponentDirection
        self._battleID = battleID
        self._attackResult = attackResult
        self._attackResource = attackResource
        self.__attackerFortLevel = atkLevel
        self.__defenderFortLevel = defLevel
        self.__division = division

    @property
    def division(self):
        return self.__division

    @property
    def capturedResources(self):
        return abs(self._attackResource)

    @property
    def attackerFortLevel(self):
        return self.__attackerFortLevel

    @property
    def defenderFortLevel(self):
        return self.__defenderFortLevel

    @property
    def opponentClanAbbrev(self):
        return self._opponentClanAbbrev

    def filter(self):
        return not self.isEnded()

    def getCapturedBuildingsNumber(self):
        attackResult = abs(self._attackResult)
        if FORT_ATTACK_RESULT.PLANNED > attackResult > FORT_ATTACK_RESULT.DRAW:
            if attackResult < FORT_ATTACK_RESULT.BASE_CAPTURED_FLAG:
                return attackResult
            else:
                return attackResult - FORT_ATTACK_RESULT.BASE_CAPTURED_FLAG

    def getType(self):
        return BATTLE_ITEM_TYPE.UNKNOWN

    def getPeripheryID(self):
        return self._peripheryID

    def getStartTime(self):
        return self._startTime

    def getFinishTime(self):
        return self._startTime + time_utils.ONE_HOUR

    def getStartTimeLeft(self):
        return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.getStartTime()))

    def getStartTimePast(self):
        return time_utils.getTimeDeltaTilNow(time_utils.makeLocalServerTime(self.getStartTime()))

    def getDirection(self):
        return self._ourDirection

    def getOpponentClanDBID(self):
        return self._opponentClanDBID

    def getOpponentClanInfo(self):
        return (self._opponentClanDBID, self._opponentClanAbbrev, self._opponentDirection)

    def getBattleID(self):
        return self._battleID

    def getBattleResults(self):
        return (self._attackResult, self._attackResource)

    def isResultsPresent(self):
        return self._attackResult not in FORT_ATTACK_RESULT.SPECIAL_RESULTS

    def isEnded(self):
        return self._attackResult not in (FORT_ATTACK_RESULT.PLANNED, FORT_ATTACK_RESULT.IN_PROGRESS)

    def isInProgress(self):
        return self._attackResult == FORT_ATTACK_RESULT.IN_PROGRESS

    def isPlanned(self):
        return self._attackResult == FORT_ATTACK_RESULT.PLANNED

    def isWin(self):
        return self.isResultsPresent() and self._attackResult > 0

    def isLose(self):
        return self.isResultsPresent() and self._attackResult <= 0 or self._attackResult == FORT_ATTACK_RESULT.TECHNICAL_DRAW

    def isHot(self):
        return self.isPlanned() and self.getStartTimeLeft() <= time_utils.QUARTER_HOUR or self.isInProgress()

    def __cmp__(self, other):
        return cmp(self.getStartTimeLeft(), other.getStartTimeLeft())


class AttackItem(_BattleItemAbstract):

    def __init__(self, startTime, ourDirection, defClanDBID, defClanAbbrev, dirTo, battleID, atkLevel, defLevel, division, peripheryID, attackResult, attackResource):
        super(AttackItem, self).__init__(peripheryID, startTime, defClanDBID, defClanAbbrev, dirTo, ourDirection, atkLevel, defLevel, division, battleID, attackResult, attackResource)

    def getType(self):
        return BATTLE_ITEM_TYPE.ATTACK


class DefenceItem(_BattleItemAbstract):

    def __init__(self, startTime, ourDirection, peripheryID, attackerClanDBID, attackerClanAbbrev, dirFrom, battleID, atkLevel, defLevel, division, attackResult, attackResource):
        super(DefenceItem, self).__init__(peripheryID, startTime, attackerClanDBID, attackerClanAbbrev, dirFrom, ourDirection, atkLevel, defLevel, division, battleID, attackResult, attackResource)

    def getType(self):
        return BATTLE_ITEM_TYPE.DEFENCE

    def isWin(self):
        return self.isResultsPresent() and self._attackResult <= 0

    def isLose(self):
        return self.isResultsPresent() and self._attackResult > 0 or self._attackResult == FORT_ATTACK_RESULT.TECHNICAL_DRAW

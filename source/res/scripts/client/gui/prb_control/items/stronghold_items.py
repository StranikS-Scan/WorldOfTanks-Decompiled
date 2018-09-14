# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/items/stronghold_items.py
import itertools
from debug_utils import LOG_ERROR
from helpers.time_utils import ONE_MINUTE, ONE_HOUR
BYTTLETYPE_SORTIE = u'SORTIE'
AIRSTRIKE = 'AIRSTRIKE'
ARTILLERY_STRIKE = 'ARTILLERY_STRIKE'
REQUISITION = 'REQUISITION'
HIGH_CAPACITY_TRANSPORT = 'HIGH_CAPACITY_TRANSPORT'
SUPPORT_TYPE = 'SUPPORT'
REQUISITION_TYPE = 'REQUISITION'
HEAVYTRUCKS_TYPE = 'HEAVYTRUCKS'
RESERVE_STRONGHOLD_ORDER = (SUPPORT_TYPE, HEAVYTRUCKS_TYPE, REQUISITION_TYPE)
RESERVE_SORTIE_ORDER = (SUPPORT_TYPE, HEAVYTRUCKS_TYPE)
SUPPORT_ORDER = (AIRSTRIKE, ARTILLERY_STRIKE)
RESERVE_ITEMS = {SUPPORT_TYPE: (AIRSTRIKE, ARTILLERY_STRIKE),
 REQUISITION_TYPE: (REQUISITION,),
 HEAVYTRUCKS_TYPE: (HIGH_CAPACITY_TRANSPORT,)}
_OldStrongholdDataScheme = ('type', 'min_level', 'max_level', 'min_players_count', 'max_players_count', 'industrial_resource_multiplier', 'max_legionaries_count', 'public', 'battle_duration', 'battle_series_duration', 'battle_idx', 'matchmaker_next_tick', 'time_to_ready', 'direction', 'requisition_bonus_percent', 'enemy_clan', 'clan', 'available_reserves', 'permissions', 'ready_button_enabled', 'selected_reserves', 'battle_series_status', 'battles_end_time', 'battles_start_time', 'fort_battles_before_start_lag', 'sorties_before_start_lag', 'sorties_before_end_lag')
_OldStrongholdDataProxyScheme = {'header': ('max_legionaries_count', 'max_players_count', 'direction', 'battle_duration', 'min_level', 'max_level', 'industrial_resource_multiplier', 'type', 'min_players_count', 'battle_idx', 'battle_series_status', 'battle_series_duration', 'enemy_clan', 'clan'),
 'timer': ('sorties_before_start_lag', 'fort_battles_before_start_lag', 'sorties_before_end_lag', 'time_to_ready', 'matchmaker_next_tick', 'battles_start_time', 'battles_end_time'),
 'state': ('public',),
 'reserve': ('available_reserves', 'selected_reserves', 'requisition_bonus_percent', 'permissions'),
 'all': ('ready_button_enabled',)}
_StrongholdDataScheme = ('header', 'timer', 'state', 'reserve', 'all')

def isEnemyBattleIndex(index):
    return index >= 3


class StrongholdSettings(object):

    def __init__(self):
        self.__data = StrongholdData()
        self.__rawData = None
        self.__setDataMapping = {'header': self.__setHeader,
         'timer': self.__setTimer,
         'state': self.__setState,
         'reserve': self.__setReserve,
         'all': self.__setReadyButtonEnabled}
        return

    def init(self):
        self.__setDataMapping = {'header': self.__setHeader,
         'timer': self.__setTimer,
         'state': self.__setState,
         'reserve': self.__setReserve,
         'all': self.__setReadyButtonEnabled}

    def fini(self):
        self.__setDataMapping = {}

    def forceCleanData(self):
        if self.__rawData:
            self.__rawData = {}

    def updateData(self, rawData):
        if self.__validateData(rawData):
            newRawData = self.__strongholdDataProxy(rawData)
            diffToUpdate = self.__makeDiff(newRawData)
            self.__setData(newRawData, diffToUpdate)
            return diffToUpdate
        else:
            LOG_ERROR('StrongholdSettings::updateData invalid data format')
            return None
            return None

    def getData(self):
        return self.__data

    def getHeader(self):
        return self.__data.getHeader()

    def getTimer(self):
        return self.__data.getTimer()

    def getState(self):
        return self.__data.getState()

    def getReserve(self):
        return self.__data.getReserve()

    def isValid(self):
        return self.__data is not None and self.__rawData is not None

    def isStrongholdUnitFreezed(self):
        return not self.__data.getReadyButtonEnabled()

    def isFirstBattle(self):
        return self.__data.getHeader().getCurrentBattle() is None

    def isSortie(self):
        return self.__data.getHeader().isSortie()

    def getReserveOrder(self):
        """
            :return: reserve order
        """
        return RESERVE_SORTIE_ORDER if self.isSortie() else RESERVE_STRONGHOLD_ORDER

    def __validateData(self, rawData):
        for field in _OldStrongholdDataScheme:
            if field not in rawData:
                return False

        return True

    def __makeDiff(self, newRawData):
        diff = set()
        if newRawData is not None:
            for k, v in newRawData.iteritems():
                if self.__rawData is None or cmp(self.__rawData.get(k), v):
                    diff.add(k)

            self.__rawData = newRawData
        return diff

    def __setData(self, newRawData, diff):
        self.__rawData = newRawData
        for toUpdate in diff:
            dataSetFunc = self.__setDataMapping.get(toUpdate)
            if dataSetFunc is not None:
                dataSetFunc()

        return

    def __setHeader(self):
        self.__data.setHeader(self.__rawData['header'])

    def __setTimer(self):
        self.__data.setTimer(self.__rawData['timer'])

    def __setState(self):
        self.__data.setState(self.__rawData['state'])

    def __setReadyButtonEnabled(self):
        self.__data.setReadyButtonEnabled(self.__rawData['all'])

    def __setReserve(self):
        self.__data.setReserve(self.__rawData['reserve'])

    def __strongholdDataProxy(self, rawData):
        correctRawData = {}
        for rootField, rootFieldValues in _OldStrongholdDataProxyScheme.iteritems():
            correctRawData[rootField] = {}
            for rootFieldItem in rootFieldValues:
                if rootFieldItem in rawData:
                    correctRawData[rootField][rootFieldItem] = rawData[rootFieldItem]

        return correctRawData


class StrongholdData(object):

    class StrongholdDataHeader(object):

        class StrongholdBattleSeriesItem(object):

            def __init__(self, index, data):
                self.__index = index
                self.__clan_owner_id = data['clan_owner_id']
                self.__map_id = data['map_id']
                self.__geometry_id = data['geometry_id']
                self.__gameplay_id = data['gameplay_id']
                self.__first_resp_clan_id = data['first_resp_clan_id']
                self.__battle_reward = data['battle_reward']
                self.__current_battle = data['current_battle']
                self.__attacker = data['attacker']

            def getIndex(self):
                return self.__index

            def getClanId(self):
                """
                    :return: clan id
                """
                return self.__clan_owner_id

            def getMapId(self):
                """
                    :return: map id
                """
                return self.__map_id

            def getGeometryId(self):
                """
                    :return: geometry id
                """
                return self.__geometry_id

            def getGameplayId(self):
                """
                    :return: gameplay id
                """
                return self.__gameplay_id

            def getFirstClanId(self):
                """
                    :return: clan id on first (green) spawn point
                """
                return self.__first_resp_clan_id

            def getBattleReward(self):
                """
                    :return: reward for battle
                """
                return self.__battle_reward

            def getCurrentBattle(self):
                """
                    :return: is this battle current
                """
                return self.__current_battle

            def getAttacker(self):
                """
                    :return: attack or defence. For current battle only
                """
                return self.__attacker

        class StrongholdClanData(object):

            def __init__(self, data):
                self.__id = data['id']
                self.__tag = data['tag']
                self.__name = data['name']
                self.__color = data['color']
                self.__status_ready = data['status_ready']

            def getId(self):
                return self.__id

            def getTag(self):
                return self.__tag

            def getName(self):
                return self.__name

            def getColor(self):
                return self.__color

            def getReadyStatus(self):
                return self.__status_ready

        def __init__(self):
            self.__max_legionaries_count = None
            self.__max_players_count = None
            self.__min_players_count = None
            self.__max_level = None
            self.__min_level = None
            self.__type = None
            self.__direction = None
            self.__battle_duration = None
            self.__battle_idx = None
            self.__battle_series_duration = None
            self.__industrial_resource_multiplier = None
            self.__battle_series_status = None
            self.__current_battle = None
            self.__clan = None
            self.__enemy_clan = None
            return

        def setData(self, data):
            clan = data['clan']
            enemy_clan = data['enemy_clan']
            self.__clan = self.StrongholdClanData(clan) if clan else None
            self.__enemy_clan = self.StrongholdClanData(enemy_clan) if enemy_clan else None
            self.__max_legionaries_count = data['max_legionaries_count']
            self.__max_players_count = data['max_players_count']
            self.__min_players_count = data['min_players_count']
            self.__max_level = data['max_level']
            self.__min_level = data['min_level']
            self.__type = data['type']
            self.__direction = data['direction']
            self.__battle_duration = data['battle_duration']
            self.__battle_idx = data['battle_idx']
            self.__battle_series_duration = data['battle_series_duration']
            self.__industrial_resource_multiplier = data['industrial_resource_multiplier']
            self.__battle_series_status = [ self.StrongholdBattleSeriesItem(index, v) for index, v in enumerate(data['battle_series_status']) ]
            self.__current_battle = None
            for bs in self.__battle_series_status:
                if bs.getCurrentBattle():
                    self.__current_battle = bs

            return

        def getMaxLegionariesCount(self):
            return self.__max_legionaries_count

        def getMaxPlayersCount(self):
            return self.__max_players_count

        def getMinPlayersCount(self):
            return self.__min_players_count

        def getMaxLevel(self):
            return self.__max_level

        def getMinLevel(self):
            return self.__min_level

        def getType(self):
            return self.__type

        def getDirection(self):
            return self.__direction

        def getBattleDuration(self):
            return self.__battle_duration

        def getBattleIdx(self):
            return self.__battle_idx

        def getBattleSeriesStatus(self):
            return self.__battle_series_status

        def getBattleSeriesDuration(self):
            return self.__battle_series_duration

        def getIndustrialResourceMultiplier(self):
            return self.__industrial_resource_multiplier

        def getCurrentBattle(self):
            return self.__current_battle

        def getClan(self):
            return self.__clan

        def getEnemyClan(self):
            return self.__enemy_clan

        def getBattleDurationMinutes(self):
            return self.__battle_duration / ONE_MINUTE

        def getBattleSeriesDurationMinuts(self):
            return self.__battle_series_duration / ONE_MINUTE

        def getBattleSeriesDurationHours(self):
            return self.__battle_series_duration / ONE_HOUR

        def isSortie(self):
            return self.getType() == BYTTLETYPE_SORTIE

    class StrongholdDataTimer(object):

        def __init__(self):
            self.__sorties_before_start_lag = None
            self.__fort_battles_before_start_lag = None
            self.__sorties_before_end_lag = None
            self.__time_to_ready = None
            self.__matchmaker_next_tick = None
            self.__battles_start_time = None
            self.__battles_end_time = None
            return

        def setData(self, data):
            self.__sorties_before_start_lag = data['sorties_before_start_lag']
            self.__fort_battles_before_start_lag = data['fort_battles_before_start_lag']
            self.__sorties_before_end_lag = data['sorties_before_end_lag']
            self.__time_to_ready = data['time_to_ready']
            self.__matchmaker_next_tick = data['matchmaker_next_tick']
            self.__battles_start_time = data['battles_start_time']
            self.__battles_end_time = data['battles_end_time']

        def getSortiesBeforeStartLag(self):
            return self.__sorties_before_start_lag

        def getFortBattlesBeforeStartLag(self):
            return self.__fort_battles_before_start_lag

        def getSortiesBeforeEndLag(self):
            return self.__sorties_before_end_lag

        def getTimeToReady(self):
            return self.__time_to_ready

        def getMatchmakerNextTick(self):
            return self.__matchmaker_next_tick

        def getBattlesStartTime(self):
            return self.__battles_start_time

        def getBattlesEndTime(self):
            return self.__battles_end_time

    class StrongholdDataState(object):

        def __init__(self):
            self.__public = None
            return

        def setData(self, data):
            self.__public = data['public']

        def getPublic(self):
            return self.__public

    class StrongholdDataReserve(object):

        class StrongholdReserveItem(object):

            def __init__(self, data):
                self.__id = data['id']
                self.__type = data['type']
                self.__level = data['level']
                self.__bonus_percent = data['bonus_percent']
                self.__description = data['description']
                self.__title = data['title']
                self.__production_elapsed = data['production_elapsed']

            def getId(self):
                """
                    :return: reserve id
                """
                return self.__id

            def getType(self):
                """
                    :return: reserve type
                """
                return self.__type

            def getGroupType(self):
                """
                    :return: reserve group type
                """
                for groupType, group in RESERVE_ITEMS.iteritems():
                    if self.__type in group:
                        return groupType

            def getLevel(self):
                """
                    :return: reserve level
                """
                return self.__level

            def getBonusPercent(self):
                """
                    :return: reserve bonus percent
                """
                return self.__bonus_percent

            def getDescription(self):
                """
                    :return: reserve description
                """
                return self.__description

            def getTitle(self):
                """
                    :return: reserve title
                """
                return self.__title

            def getProductionElapsed(self):
                """
                    :return: production elapsed
                """
                return self.__production_elapsed

            def isRequsition(self):
                """
                    :return: reserve is requisition
                """
                return self.getGroupType() == REQUISITION

            def __eq__(self, other):
                if isinstance(other, self.__class__):
                    return self.__type == other.__type and self.__level == other.__level
                else:
                    return False

            def __cmp__(self, other):
                if not isinstance(other, self.__class__):
                    return NotImplemented
                group = RESERVE_ITEMS[self.getGroupType()]
                typeOrder1 = group.index(self.__type)
                typeOrder2 = group.index(other.__type)
                return cmp((other.__level, typeOrder1), (self.__level, typeOrder2))

        def __init__(self):
            self.__permissions = None
            self.__selected_reserves = []
            self.__available_reserves = {}
            self.__requisition_bonus_percent = None
            return

        def setData(self, data):
            self.__permissions = data['permissions']
            self.__requisition_bonus_percent = data['requisition_bonus_percent']
            self.__available_reserves = {group:[ self.StrongholdReserveItem(v) for v in groupvalues ] for group, groupvalues in data['available_reserves'].iteritems()}
            self.__selected_reserves = [ self.getReserveById(reserveId) for reserveId in data['selected_reserves'] ]

        def getPermissions(self):
            return self.__permissions

        def getSelectedReserves(self):
            return self.__selected_reserves

        def getAvailableReserves(self):
            return self.__available_reserves

        def getRequisitionBonusPercent(self):
            return self.__requisition_bonus_percent

        def getReserveById(self, reserveId):
            """
                :return: find reserve by reserveId
            """
            if reserveId is None or self.__available_reserves is None:
                return
            else:
                for reserve in itertools.chain(*self.__available_reserves.itervalues()):
                    if reserve.getId() == reserveId:
                        return reserve

                return

        def getUniqueReservesByGroupType(self, groupType):
            """
                :return: unique and sorted reserves by choosen type
            """
            reserves = []
            for rType in RESERVE_ITEMS[groupType]:
                reserves.extend(self.__available_reserves[rType])

            unique = []
            for reserve in self.__selected_reserves:
                if reserve and reserve.getGroupType() == groupType:
                    unique.append(reserve)

            for item in reserves:
                if item not in unique:
                    unique.append(item)

            uniqueAndSorted = sorted(unique, cmp=lambda x, y: x.__cmp__(y))
            return uniqueAndSorted

        def getReserveCount(self, type, level):
            """
                :return: reserves count by type and level
            """
            count = 0
            for reserve in itertools.chain(*self.__available_reserves.itervalues()):
                if reserve.getType() == type and reserve.getLevel() == level:
                    count += 1

            return count

    def __init__(self):
        self.__header = self.StrongholdDataHeader()
        self.__timer = self.StrongholdDataTimer()
        self.__state = self.StrongholdDataState()
        self.__reserve = self.StrongholdDataReserve()
        self.__ready_button_enabled = None
        return

    def getHeader(self):
        return self.__header

    def setHeader(self, data):
        self.__header.setData(data)

    def getTimer(self):
        return self.__timer

    def setTimer(self, data):
        self.__timer.setData(data)

    def getState(self):
        return self.__state

    def setState(self, data):
        self.__state.setData(data)

    def getReadyButtonEnabled(self):
        return self.__ready_button_enabled

    def setReadyButtonEnabled(self, data):
        self.__ready_button_enabled = data['ready_button_enabled']

    def getReserve(self):
        return self.__reserve

    def setReserve(self, data):
        self.__reserve.setData(data)

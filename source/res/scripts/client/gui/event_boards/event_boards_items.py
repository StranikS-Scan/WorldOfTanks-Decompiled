# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/event_boards/event_boards_items.py
import itertools
from collections import defaultdict
import BigWorld
from gui import GUI_NATIONS
from gui.shared.utils import mapTextureToTheMemory, removeTextureFromMemory
from shared_utils import findFirst, CONST_CONTAINER
from debug_utils import LOG_ERROR, LOG_WARNING
from items import parseIntCompactDescr
from gui.event_boards import event_boards_timer
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from helpers import time_utils
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class CALCULATION_METHODS(CONST_CONTAINER):
    MAX = 'max'
    SUMN = 'sumN'
    SUMSEQN = 'sumSeqN'
    SUMALL = 'sumAll'
    SUMMSEQN = 'sumMSeqN'


class OBJECTIVE_PARAMETERS(CONST_CONTAINER):
    ORIGINALXP = 'originalXP'
    XP = 'xp'
    DAMAGEDEALT = 'damageDealt'
    DAMAGEASSISTED = 'damageAssisted'
    WINS = 'wins'


class EVENT_TYPE(CONST_CONTAINER):
    VEHICLE = 'vehicle'
    NATION = 'nation'
    LEVEL = 'level'
    CLASS = 'class'


class EVENT_STATE(CONST_CONTAINER):
    UNDEFINED = 0
    JOINED = 1
    CANCELED = 2


class PLAYER_STATE_REASON(CONST_CONTAINER):
    BYWINRATE = 1
    BYAGE = 2
    BYBATTLESCOUNT = 3
    BYBAN = 4
    WASUNREGISTERED = 5
    SPECIALACCOUNT = 6
    VEHICLESMISSING = 7


class SET_DATA_STATUS_CODE(CONST_CONTAINER):
    OK = 0
    ERROR = 1
    RETURN = 2


class EVENTS_ERROR_CODE(CONST_CONTAINER):
    GET_DATA = 0
    JOIN = 1
    LEAVE = 2


class EVENT_DATE_TYPE(CONST_CONTAINER):
    PUBLISH = 0
    START = 1
    END = 2
    PARTICIPANTS_FREEZE = 3
    REWARDING = 4


EVENTS_TYPES = EVENT_TYPE.ALL()
WOODEN_RIBBON = 5

class EventBoardsSettings(object):

    def __init__(self):
        self.__eventsSettings = EventsSettings()
        self.__playerEventsData = PlayerEventsData()
        self.__myEventsTop = MyEventsTop()

    def getPlayerEventsData(self):
        return self.__playerEventsData

    def getEventsSettings(self):
        return self.__eventsSettings

    def getMyEventsTop(self):
        return self.__myEventsTop

    def hasEvents(self):
        eventsSettings = self.__eventsSettings.getEvents()
        return eventsSettings and len(eventsSettings)

    def fini(self):
        self.__eventsSettings.fini()

    def cleanEventsData(self):
        self.__eventsSettings.cleanData()
        self.__playerEventsData.cleanData()
        self.__myEventsTop.cleanData()


class EventsSettings(object):
    EXPECTED_FIELDS = ['battle_type',
     'cardinality',
     'end_date',
     'event_id',
     'is_squad_allowed',
     'leaderboard_view_size',
     'limits',
     'manual',
     'method',
     'name',
     'objective_parameter',
     'participants_freeze_deadline',
     'prime_times',
     'publish_date',
     'rewarding_date',
     'rewards_by_rank',
     'start_date',
     'type',
     'distance']
    EXPECTED_FIELDS_PRIME_TIMES = ['server', 'start_time', 'end_time']
    EXPECTED_FIELDS_LIMITS = ['win_rate_min',
     'win_rate_max',
     'registration_date_max',
     'is_registration_needed',
     'battles_count_min',
     'nations',
     'vehicles',
     'vehicles_levels',
     'vehicles_classes']
    EXPECTED_FIELDS_REWARDS_CATEGORIES = ['leaderboard_id', 'categories']
    EXPECTED_FIELDS_REWARDS_CATEGORIES_CATEGORY = ['rank_min', 'rank_max', 'reward_category_number']
    EXPECTED_FIELDS_REWARDS_BY_RANK = ['leaderboard_id', 'reward_groups']
    EXPECTED_FIELDS_REWARDS_BY_RANK_GROUP = ['reward_category_number',
     'rank_min',
     'rank_max',
     'rewards']

    def __init__(self):
        self.__events = []

    def fini(self):
        for event in self.__events:
            event.removeImages()

    def cleanData(self):
        for event in self.__events:
            event.removeImages()

        self.__events = []

    def setData(self, rawData, prefetchKeyArtBig=True):
        oldEvents = {event.getEventID():event for event in self.__events}
        self.__events = []
        if not self.__isDataStructureValid(rawData):
            if rawData:
                LOG_WARNING('EventsSettings setData error: data structure error')
            return SET_DATA_STATUS_CODE.ERROR
        else:
            for event in rawData:
                eventSettings = EventSettings()
                eventSettings.setData(event)
                oldEvent = oldEvents.pop(eventSettings.getEventID(), None)
                eventSettings.setImages(oldEvent.getImages() if oldEvent else {}, prefetchKeyArtBig)
                self.__events.append(eventSettings)

            for event in oldEvents.values():
                event.removeImages()

            return SET_DATA_STATUS_CODE.OK

    def getEvents(self):
        return self.__events

    def getEvent(self, eventId):
        for event in self.__events:
            if event.getEventID() == eventId:
                return event

        return None

    def getEventForVehicle(self, vehCD):
        for event in self.__events:
            if vehCD in event.getLimits().getVehiclesWhiteList():
                return event

        return None

    def hasActiveEvents(self):
        for event in self.__events:
            if event.isActive():
                return True

        return False

    def hasActiveOrSoonEvents(self):
        if self.hasActiveEvents():
            return True
        for event in self.__events:
            value, _ = event_boards_timer.getTimeStatus(event.getStartDate())
            if value > 0:
                return True

        return False

    def hasAnotherActiveEvents(self, eventID):
        for event in self.__events:
            if event.isActive() and event.getEventID() != eventID:
                return True

        return False

    def hasActiveEventsByState(self, hangarFlagData):
        if hangarFlagData is not None:
            for eID, eState in hangarFlagData.items():
                event = self.getEvent(eID)
                if event is not None:
                    regIsFailed = event.isRegistrationFinished() and eState != EVENT_STATE.JOINED
                    if event.isActive() and eState != EVENT_STATE.CANCELED and not regIsFailed:
                        return True

        return False

    def __isDataStructureValid(self, data):
        if not data:
            return False
        for item in data:
            if not isDataSchemaValid(self.EXPECTED_FIELDS, item):
                return False
            for primeTimeItem in item['prime_times']:
                if not isDataSchemaValid(self.EXPECTED_FIELDS_PRIME_TIMES, primeTimeItem):
                    return False

            if not isDataSchemaValid(self.EXPECTED_FIELDS_LIMITS, item['limits']):
                return False
            for rewardsByRank in item['rewards_by_rank']:
                if not isDataSchemaValid(self.EXPECTED_FIELDS_REWARDS_BY_RANK, rewardsByRank):
                    return False
                for rGroup in rewardsByRank['reward_groups']:
                    if not isDataSchemaValid(self.EXPECTED_FIELDS_REWARDS_BY_RANK_GROUP, rGroup):
                        return False

        return True


class EventSettings(object):
    __mapping = {EVENT_TYPE.VEHICLE: ('vehicles', 'vehicles', None),
     EVENT_TYPE.NATION: ('nations', 'nation', GUI_NATIONS),
     EVENT_TYPE.LEVEL: ('vehicles_levels', 'level', range(1, 11)),
     EVENT_TYPE.CLASS: ('vehicles_classes', 'class', VEHICLE_TYPES_ORDER)}
    EVENT_DAYS_LEFT_TO_START = 5
    EVENT_FINISHED_DURATION = 5 * time_utils.ONE_DAY
    EVENT_STARTED_DURATION_PERCENTAGE = 0.1
    EVENT_TO_END_DATA_DURATION_PERCENTAGE = 0.1

    def __init__(self):
        self.__eventID = None
        self.__name = None
        self.__type = None
        self.__objectiveParameter = None
        self.__method = None
        self.__publishDate = None
        self.__startDate = None
        self.__participantsFreezeDeadline = None
        self.__endDate = None
        self.__rewardingDate = None
        self.__cardinality = None
        self.__distance = None
        self.__manual = None
        self.__battleType = None
        self.__isSquadAllowed = None
        self.__leaderboardViewSize = None
        self.__primeTimes = PrimeTimes()
        self.__limits = Limits()
        self.__rewardsByRank = RewardsByRank()
        self.__keyArtBig = None
        self.__keyArtSmall = None
        self.__promoBonuses = None
        self.__leaderboards = {}
        self.__leaderboardsIndex = {}
        self.__images = {}
        return

    def setImages(self, images, prefetchKeyArtBig):
        self.__images = images
        self.__prefetchImages(prefetchKeyArtBig)

    def getImages(self):
        return self.__images

    def removeImages(self):
        for image in self.__images.values():
            if image:
                removeTextureFromMemory(image)

    def setData(self, rawData):
        self.__eventID = rawData['event_id']
        self.__name = rawData['name']
        self.__type = rawData['type']
        self.__objectiveParameter = rawData['objective_parameter']
        self.__method = rawData['method']
        self.__publishDate = rawData['publish_date']
        self.__startDate = rawData['start_date']
        self.__participantsFreezeDeadline = rawData['participants_freeze_deadline']
        self.__endDate = rawData['end_date']
        self.__rewardingDate = rawData['rewarding_date']
        self.__cardinality = rawData['cardinality']
        self.__distance = rawData['distance']
        self.__manual = rawData['manual']
        self.__battleType = rawData['battle_type']
        self.__isSquadAllowed = rawData['is_squad_allowed']
        self.__leaderboardViewSize = rawData['leaderboard_view_size']
        self.__limits.setData(rawData['limits'])
        self.__primeTimes.setData(rawData['prime_times'])
        self.__rewardsByRank.setData(rawData['rewards_by_rank'])
        self.__keyArtBig = rawData.get('key_art_big')
        self.__keyArtSmall = rawData.get('key_art_small')
        self.__promoBonuses = rawData.get('promo_bonuses')
        self.__makeLeaderboards(rawData['limits'])

    def getLeaderboards(self):
        if self.__type in self.__mapping:
            _, _, order = self.__mapping[self.__type]
            if order:
                inversed = self.__leaderboardsIndex
                return [ (inversed[value], value) for value in order if value in inversed ]
        return self.__leaderboards.items()

    def getLeaderboard(self, leaderboardID):
        return self.__leaderboards.get(leaderboardID)

    def getLeaderboardID(self, value):
        return self.__leaderboardsIndex.get(value)

    def getEventID(self):
        return self.__eventID

    def getName(self):
        return self.__name

    def getType(self):
        return self.__type

    def getObjectiveParameter(self):
        return self.__objectiveParameter

    def getMethod(self):
        return self.__method

    def getPublishDate(self):
        return self.__publishDate

    def getStartDate(self):
        return self.__startDate

    def getStartDateTs(self):
        return event_boards_timer.getTimeStampFromDate(self.__startDate)

    def isAtBeginning(self):
        startTs = self.getStartDateTs()
        duration = (self.getEndDateTs() - startTs) * self.EVENT_STARTED_DURATION_PERCENTAGE
        passed = event_boards_timer.getCurrentUTCTimeTs() - startTs
        return 0 < passed < duration

    def isAfterEnd(self):
        passed = event_boards_timer.getCurrentUTCTimeTs() - self.getEndDateTs()
        return 0 < passed < self.EVENT_FINISHED_DURATION

    def getParticipantsFreezeDeadline(self):
        return self.__participantsFreezeDeadline

    def getParticipantsFreezeDeadlineTs(self):
        return event_boards_timer.getTimeStampFromDate(self.__participantsFreezeDeadline)

    def getEndDate(self):
        return self.__endDate

    def getEndDateTs(self):
        return event_boards_timer.getTimeStampFromDate(self.__endDate)

    def getFormattedRemainingTime(self, dateType):
        if dateType == EVENT_DATE_TYPE.PUBLISH:
            return event_boards_timer.getFormattedRemainingTime(self.__publishDate)
        if dateType == EVENT_DATE_TYPE.START:
            return event_boards_timer.getFormattedRemainingTime(self.__startDate)
        if dateType == EVENT_DATE_TYPE.PARTICIPANTS_FREEZE:
            return event_boards_timer.getFormattedRemainingTime(self.__participantsFreezeDeadline)
        if dateType == EVENT_DATE_TYPE.END:
            return event_boards_timer.getFormattedRemainingTime(self.__endDate)
        return event_boards_timer.getFormattedRemainingTime(self.__rewardingDate) if dateType == EVENT_DATE_TYPE.REWARDING else event_boards_timer.getFormattedRemainingTime('')

    def isStarted(self):
        value, _ = event_boards_timer.getTimeStatus(self.__startDate)
        return value < 0

    def isRegistrationFinished(self):
        value, _ = event_boards_timer.getTimeStatus(self.__participantsFreezeDeadline)
        return value < 0

    def isFinished(self):
        value, _ = event_boards_timer.getTimeStatus(self.__endDate)
        return value < 0

    def isStartSoon(self):
        value, period = event_boards_timer.getTimeStatus(self.__startDate)
        if period == event_boards_timer.FORMAT_DAY_STR:
            return self.EVENT_DAYS_LEFT_TO_START > value > 0
        return value > 0

    def isEndSoon(self):
        return event_boards_timer.isPeriodCloseToEnd(self.__startDate, self.__endDate, self.EVENT_TO_END_DATA_DURATION_PERCENTAGE)

    def isRegistrationFinishSoon(self):
        return event_boards_timer.isPeriodCloseToEnd(self.__startDate, self.__participantsFreezeDeadline, self.EVENT_TO_END_DATA_DURATION_PERCENTAGE)

    def isActive(self):
        value1, _ = event_boards_timer.getTimeStatus(self.__startDate)
        value2, _ = event_boards_timer.getTimeStatus(self.__endDate)
        return value1 < 0 < value2

    def getRewardingDate(self):
        return self.__rewardingDate

    def getCardinality(self):
        return self.__cardinality

    def getDistance(self):
        return self.__distance

    def getManual(self):
        return self.__manual

    def getBattleType(self):
        return self.__battleType

    def getIsSquadAllowed(self):
        return self.__isSquadAllowed

    def getLeaderboardViewSize(self):
        return self.__leaderboardViewSize

    def getLimits(self):
        return self.__limits

    def getPrimeTimes(self):
        return self.__primeTimes

    def getRewardsByRank(self):
        return self.__rewardsByRank

    def isAvailableServer(self, peripheryID):
        return True if self.__primeTimes.isEmpty() else findFirst(lambda pt: pt.isActive() and pt.getServer() == str(peripheryID), self.__primeTimes.getPrimeTimes(), None) is not None

    def getAvailableServers(self):
        return [ pt for pt in self.__primeTimes.getPrimeTimes() if pt.isActive() ]

    def getKeyArtBig(self):
        return self.__getImage(self.__keyArtBig, RES_ICONS.MAPS_ICONS_EVENTBOARDS_BLANK_EVENT_BGR_LANDING_BLANK)

    def getKeyArtSmall(self):
        return self.__getImage(self.__keyArtSmall, RES_ICONS.MAPS_ICONS_EVENTBOARDS_BLANK_TOOLTIP_BACKGROUND_BLANK)

    def getPromoBonuses(self):
        return self.__getImage(self.__promoBonuses, RES_ICONS.MAPS_ICONS_EVENTBOARDS_BLANK_EVENT_PROMO_REWARD_BLANK)

    def __requestImage(self, url):
        bwPlayer = BigWorld.player()
        if url and bwPlayer:
            bwPlayer.customFilesCache.get(url, self.__onImageReceive)

    def __onImageReceive(self, url, img):
        if img:
            self.__images[url] = mapTextureToTheMemory(img, temp=False)

    def __getImage(self, url, default):
        if url not in self.__images:
            self.__requestImage(url)
            return default
        return 'img://{}'.format(self.__images[url])

    def __prefetchImages(self, prefetchKeyArtBig):
        if prefetchKeyArtBig:
            self.getKeyArtBig()
        self.getKeyArtSmall()
        self.getPromoBonuses()

    def __makeLeaderboards(self, rawData):
        self.__leaderboards = {}
        self.__leaderboardsIndex = {}
        if self.__type in self.__mapping:
            listKey, itemKey, _ = self.__mapping[self.__type]
            for leaderboard in rawData[listKey]:
                key = int(leaderboard['leaderboard_id'])
                val = leaderboard[itemKey]
                if isinstance(val, list):
                    val = val[0]
                self.__leaderboards[key] = val
                self.__leaderboardsIndex[val] = key

        else:
            LOG_WARNING('__makeLeaderboards: Unknown event type')


class PrimeTimes(object):

    def __init__(self):
        self.__primeTimes = None
        return

    def setData(self, data):
        if data is not None:
            self.__primeTimes = []
            for serverData in data:
                primeTime = PrimeTime()
                primeTime.setData(serverData)
                self.__primeTimes.append(primeTime)

        return

    def getPrimeTimes(self):
        return self.__primeTimes

    def isEmpty(self):
        return len(self.__primeTimes) is 0


class PrimeTime(object):

    def __init__(self):
        self.__server = None
        self.__startTime = None
        self.__endTime = None
        return

    def setData(self, data):
        self.__server = data['server']
        self.__startTime = data['start_time']
        self.__endTime = data['end_time']

    def getServer(self):
        return self.__server

    def getStartTime(self):
        return self.__startTime

    def getEndTime(self):
        return self.__endTime

    def getStartLocalTime(self):
        return event_boards_timer.getPeripheryTime(self)[0]

    def getEndLocalTime(self):
        return event_boards_timer.getPeripheryTime(self)[1]

    def isActive(self):
        return event_boards_timer.isPeripheryActiveAtCurrentMoment(self)[0]

    def timeToActive(self):
        return event_boards_timer.isPeripheryActiveAtCurrentMoment(self)[1]


class Limits(object):

    def __init__(self):
        self.__winRateMin = None
        self.__winRateMax = None
        self.__registrationDateMax = None
        self.__isRegistrationNeeded = None
        self.__battlesCountMin = None
        self.__vehicles = {}
        self.__nations = None
        self.__vehiclesLevels = None
        self.__vehiclesClasses = None
        return

    def setData(self, data):
        self.__winRateMin = data['win_rate_min']
        self.__winRateMax = data['win_rate_max']
        self.__registrationDateMax = data['registration_date_max']
        self.__isRegistrationNeeded = data['is_registration_needed']
        self.__battlesCountMin = data['battles_count_min']
        self.__vehicles = {}
        if data['vehicles'] is not None:
            for leaderboard in data['vehicles']:
                self.__vehicles[int(leaderboard['leaderboard_id'])] = [ vehicle for vehicle in leaderboard['vehicles'] if self.__doesVehicleExist(vehicle) ]

        if data['nations'] is not None:
            self.__nations = []
            for nation in data['nations']:
                self.__nations.append(nation['nation'])

        if data['vehicles_levels'] is not None:
            self.__vehiclesLevels = []
            for vehicleLevels in data['vehicles_levels']:
                self.__vehiclesLevels.append(vehicleLevels['level'])

        if data['vehicles_classes'] is not None:
            self.__vehiclesClasses = []
            for vehicleClasses in data['vehicles_classes']:
                self.__vehiclesClasses.append(vehicleClasses['class'])

        return

    def getWinRateMin(self):
        return self.__winRateMin

    def getWinRateMax(self):
        return self.__winRateMax

    def getRegistrationDateMax(self):
        return self.__registrationDateMax

    def getRegistrationDateMaxTs(self):
        return event_boards_timer.getTimeStampFromDate(self.__registrationDateMax)

    def getIsRegistrationNeeded(self):
        return self.__isRegistrationNeeded

    def getBattlesCountMin(self):
        return self.__battlesCountMin

    def getVehicles(self, leaderboardID):
        return self.__vehicles.get(leaderboardID)

    def getNations(self):
        return self.__nations

    def getVehiclesLevels(self):
        return self.__vehiclesLevels

    def getVehiclesClasses(self):
        return self.__vehiclesClasses

    def getVehiclesWhiteList(self):
        return tuple(set(itertools.chain(*self.__vehicles.itervalues())))

    def __doesVehicleExist(self, vehIntCD):
        itemTypeID, _, _ = parseIntCompactDescr(vehIntCD)
        return True if itemTypeID == GUI_ITEM_TYPE.VEHICLE else False


class RewardsByRank(object):

    def __init__(self):
        self.__rewardsByRank = None
        return

    def setData(self, data):
        if data is not None:
            self.__rewardsByRank = []
            for reward in data:
                rewardByRank = RewardByRank()
                rewardByRank.setData(reward)
                self.__rewardsByRank.append(rewardByRank)

        return

    def getRewardsByRank(self):
        return self.__rewardsByRank

    def getRewardByRank(self, leaderboardID):
        try:
            return next(itertools.ifilter(lambda l: l.getLeaderboardID() is leaderboardID, self.__rewardsByRank))
        except StopIteration:
            LOG_ERROR('leaderboardID not found in data. leaderboardID=', leaderboardID)
            return None

        return None


class RewardByRank(object):

    def __init__(self):
        self.__leaderboardID = None
        self.__rewardGroups = None
        return

    def setData(self, rawData):
        if rawData is not None:
            self.__leaderboardID = int(rawData['leaderboard_id'])
            self.__rewardGroups = []
            for rewardGroup in rawData['reward_groups']:
                rewardGroupItem = RewardGroups()
                rewardGroupItem.setData(rewardGroup)
                self.__rewardGroups.append(rewardGroupItem)

        return

    def getLeaderboardID(self):
        return self.__leaderboardID

    def getRewardGroups(self):
        return self.__rewardGroups

    def getRewardCategoryNumber(self, myPosition):
        if myPosition is not None and self.__rewardGroups is not None:
            for group in self.__rewardGroups:
                minPos, maxPos = group.getRankMinMax()
                if minPos <= myPosition <= maxPos:
                    return group.getRewardCategoryNumber()

        return

    def getCategoryMinMax(self, category):
        groups = [ g for g in self.__rewardGroups if g.getRewardCategoryNumber() is category ]
        minimum = min(groups, key=lambda group: group.getRankMinMax()[0])
        maximum = max(groups, key=lambda group: group.getRankMinMax()[1])
        return (minimum.getRankMinMax()[0], maximum.getRankMinMax()[1])


class RewardGroups(object):

    def __init__(self):
        self.__rewardCategoryNumber = None
        self.__rankMin = None
        self.__rankMax = None
        self.__rewards = []
        return

    def setData(self, data):
        if data is not None:
            from gui.Scaleform.daapi.view.lobby.event_boards.event_helpers import convertRewardsDictToBonusObjects
            self.__rewardCategoryNumber = data['reward_category_number']
            self.__rewards = convertRewardsDictToBonusObjects(data, 'rewards')
            self.__rankMin = data['rank_min']
            self.__rankMax = data['rank_max']
        return

    def getRewards(self):
        return self.__rewards

    def getRewardCategoryNumber(self):
        return self.__rewardCategoryNumber

    def getRankMinMax(self):
        return (self.__rankMin, self.__rankMax)


class RewardGroup(object):

    def __init__(self):
        self.__rewardType = None
        self.__rewardsAmount = None
        return

    def setData(self, data):
        self.__rewardType = data['reward_type']
        self.__rewardsAmount = data['rewards_amount']

    def getRewardType(self):
        return self.__rewardType

    def getRewardsAmount(self):
        return self.__rewardsAmount


class PlayerEventsData(object):
    EXPECTED_FIELDS = ['all_battles_count', 'win_rate', 'events_list']
    EXPECTED_FIELDS_EVENTS_LIST = ['event_id',
     'player_state',
     'can_join',
     'player_state_reasons',
     'players_in_event']

    def __init__(self):
        self.__winRate = None
        self.__allBattlesCount = None
        self.__eventsList = None
        return

    def cleanData(self):
        self.__winRate = None
        self.__allBattlesCount = None
        self.__eventsList = []
        return

    def setData(self, rawData):
        if not self.__isDataStructureValid(rawData):
            if rawData:
                LOG_WARNING('PlayerEventsData setData error: data structure error')
            return SET_DATA_STATUS_CODE.ERROR
        self.__eventsList = []
        self.__winRate = rawData['win_rate']
        self.__allBattlesCount = rawData['all_battles_count']
        for eventData in rawData['events_list']:
            eventModel = EventsList()
            eventModel.setData(eventData)
            self.__eventsList.append(eventModel)

        return SET_DATA_STATUS_CODE.OK

    def clearData(self):
        self.__eventsList = None
        return

    def getWinRate(self):
        return self.__winRate

    def getBattlesCount(self):
        return self.__allBattlesCount

    def getPlayerStateByEventId(self, eventId):
        if self.__eventsList:
            for eventData in self.__eventsList:
                if eventData and eventData.getEventID() == eventId:
                    return eventData

        return None

    def getEventsList(self):
        return self.__eventsList

    def __isDataStructureValid(self, data):
        if data and isDataSchemaValid(self.EXPECTED_FIELDS, data):
            for item in data['events_list']:
                if not isDataSchemaValid(self.EXPECTED_FIELDS_EVENTS_LIST, item):
                    return False

            return True
        return False


class EventsList(object):

    def __init__(self):
        self.__eventID = None
        self.__playerState = None
        self.__canJoin = None
        self.__playersInEvent = None
        self.__playerStateReasons = None
        return

    def setData(self, data):
        self.__eventID = data['event_id']
        self.__playerState = data['player_state']
        self.__canJoin = data['can_join']
        self.__playersInEvent = data['players_in_event']
        self.__playerStateReasons = data['player_state_reasons']

    def updateStateReason(self, reason):
        self.__canJoin = False
        self.__playerStateReasons.append(reason)

    def getEventID(self):
        return self.__eventID

    def getPlayerState(self):
        return self.__playerState

    def getCanJoin(self):
        return self.__canJoin

    def getPlayersInEvent(self):
        return self.__playersInEvent

    def getPlayerStateReasons(self):
        return self.__playerStateReasons


class MyEventsTop(object):
    EXPECTED_FIELDS = ['data', 'event_id']
    EXPECTED_FIELDS_DATA = ['meta', 'data']
    EXPECTED_FIELDS_ITEM_DATA = ['leaderboard_id',
     'my_position',
     'battles_count',
     'my_value',
     'last_in_leaderboard_value']
    EXPECTED_FIELDS_ITEM_META = ['recalculation_interval', 'last_leaderboard_recalculation_ts', 'next_leaderboard_recalculation_ts']

    def __init__(self):
        self.__myEventsTopList = []
        self.__myEventsTopMeta = defaultdict()

    def cleanData(self):
        self.__myEventsTopList = []
        self.__myEventsTopMeta = defaultdict()

    def setData(self, data):
        if not self.__isDataStructureValid(data):
            if data:
                LOG_WARNING('MyEventsTop setData error: data structure error')
            return SET_DATA_STATUS_CODE.ERROR
        self.__myEventsTopList = []
        for eventTopData in data:
            dataItem = eventTopData['data']
            topMetaItem = TopMetaItem()
            topMetaItem.setData(dataItem['meta'])
            self.__myEventsTopMeta[eventTopData['event_id']] = topMetaItem
            for dataTopItem in dataItem['data']:
                topItem = TopItem()
                topItem.setData(dataTopItem, eventTopData['event_id'])
                self.__myEventsTopList.append(topItem)

        return SET_DATA_STATUS_CODE.OK

    def getMyEventsTopList(self):
        return self.__myEventsTopList

    def getMyEventTop(self, eventId):
        return [ eventTop for eventTop in self.__myEventsTopList if eventTop.getEventID() == eventId ]

    def getMyLeaderboardEventTop(self, eventId, leadeboardId):
        return findFirst(lambda eventTop: eventTop.getEventID() == eventId and eventTop.getLeaderboardID() == leadeboardId, self.__myEventsTopList, None)

    def getMyEventsTopMeta(self, eventID):
        return self.__myEventsTopMeta.get(eventID)

    def __isDataStructureValid(self, rawData):
        if not rawData:
            return False
        else:
            for data in rawData:
                if data is None:
                    return False
                if not isDataSchemaValid(self.EXPECTED_FIELDS, data):
                    return False
                itemData = data['data']
                if not isDataSchemaValid(self.EXPECTED_FIELDS_DATA, itemData):
                    return False
                if not isDataSchemaValid(self.EXPECTED_FIELDS_ITEM_META, itemData['meta']):
                    return False
                for dataItem in itemData['data']:
                    if not isDataSchemaValid(self.EXPECTED_FIELDS_ITEM_DATA, dataItem):
                        return False

            return True


class TopMetaItem(object):

    def __init__(self):
        self.__recalculationInterval = None
        self.__lastLeaderboardRecalculationTS = None
        self.__nextLeaderboardRecalculationTS = None
        return

    def setData(self, data):
        self.__recalculationInterval = data['recalculation_interval']
        self.__lastLeaderboardRecalculationTS = data['last_leaderboard_recalculation_ts']
        self.__nextLeaderboardRecalculationTS = data['next_leaderboard_recalculation_ts']

    def getRecalculationInterval(self):
        return self.__recalculationInterval

    def getLastLeaderboardRecalculationTS(self):
        return self.__lastLeaderboardRecalculationTS

    def getNextLeaderboardRecalculationTS(self):
        return self.__nextLeaderboardRecalculationTS


class TopItem(object):

    def __init__(self):
        self.__eventID = None
        self.__leaderboardID = None
        self.__myPosition = None
        self.__battlesCount = None
        self.__myValue = None
        self.__lastInLeaderboardValue = None
        return

    def setData(self, data, eventID):
        self.__eventID = eventID
        self.__leaderboardID = int(data['leaderboard_id'])
        self.__myPosition = data['my_position']
        self.__battlesCount = data['battles_count']
        self.__myValue = data['my_value']
        self.__lastInLeaderboardValue = data['last_in_leaderboard_value']

    def getLeaderboardID(self):
        return self.__leaderboardID

    def getMyPosition(self):
        return self.__myPosition

    def getBattlesCount(self):
        return self.__battlesCount

    def getMyValue(self):
        return self.__myValue

    def getLastInLeaderboardValue(self):
        return self.__lastInLeaderboardValue

    def getEventID(self):
        return self.__eventID


class MyInfoInLeaderBoard(object):
    EXPECTED_FIELDS = ['rank',
     'p1',
     'p2',
     'p3',
     'page_number',
     'is_inside_viewsize',
     'last_in_leaderboard_value',
     'battles_count',
     'clan_tag',
     'clan_color']

    def __init__(self):
        self.__eventID = None
        self.__leaderboardID = None
        self.__rank = None
        self.__p1 = None
        self.__p2 = None
        self.__p3 = None
        self.__pageNumber = None
        self.__isInsideViewsize = None
        self.__lastInLeaderboardValue = None
        self.__battlesCount = None
        self.__clanTag = None
        self.__clanColor = None
        return

    def setData(self, rawData, eventID, leaderboardID):
        if not self.__isDataStructureValid(rawData):
            if rawData:
                LOG_WARNING('MyInfoInLeaderBoard setData error: data structure error')
            return SET_DATA_STATUS_CODE.ERROR
        self.__eventID = eventID
        self.__leaderboardID = leaderboardID
        self.__rank = rawData['rank']
        self.__p1 = rawData['p1']
        self.__p2 = rawData['p2']
        self.__p3 = rawData['p3']
        self.__pageNumber = rawData['page_number']
        self.__isInsideViewsize = rawData['is_inside_viewsize']
        self.__lastInLeaderboardValue = rawData['last_in_leaderboard_value']
        self.__battlesCount = rawData['battles_count']
        self.__clanTag = rawData['clan_tag']
        self.__clanColor = rawData['clan_color']
        return SET_DATA_STATUS_CODE.OK

    def getEventID(self):
        return self.__eventID

    def getLeaderboardID(self):
        return self.__leaderboardID

    def getRank(self):
        return self.__rank

    def getP1(self):
        return self.__p1

    def getP2(self):
        return self.__p2

    def getP3(self):
        return self.__p3

    def getPageNumber(self):
        return self.__pageNumber

    def getIsInsideViewsize(self):
        return self.__isInsideViewsize

    def getLastInLeaderboardValue(self):
        return self.__lastInLeaderboardValue

    def getBattlesCount(self):
        return self.__battlesCount

    def getClanTag(self):
        return self.__clanTag

    def getClanColor(self):
        return self.__clanColor

    def __isDataStructureValid(self, data):
        return True if data and isDataSchemaValid(self.EXPECTED_FIELDS, data) else False


class LeaderBoard(object):
    EXPECTED_FIELDS = ['meta', 'data']
    EXPECTED_FIELDS_META = ['page_number',
     'pages_amount',
     'rewards',
     'recalculation_interval',
     'last_leaderboard_recalculation_ts',
     'next_leaderboard_recalculation_ts']
    EXPECTED_FIELDS_DATA = ['spa_id',
     'name',
     'clan_tag',
     'clan_color',
     'rank',
     'p1',
     'p2',
     'p3',
     'info']
    EXPECTED_FIELDS_META_REWARDS = ['reward_category_number', 'page_number']
    CALCULATION_METHODS_EXPECTED_FIELDS = {CALCULATION_METHODS.MAX: ['battle_ts',
                               'vehicle_cd',
                               'battle_result',
                               'is_in_squad',
                               'exp',
                               'damage',
                               'assisted_damage',
                               'frags',
                               'blocked_damage'],
     CALCULATION_METHODS.SUMN: ['battle_ts',
                                'vehicle_cd',
                                'battle_result',
                                'is_in_squad',
                                'exp',
                                'damage',
                                'assisted_damage',
                                'frags'],
     CALCULATION_METHODS.SUMSEQN: ['battle_ts',
                                   'vehicle_cd',
                                   'battle_result',
                                   'is_in_squad',
                                   'exp',
                                   'damage',
                                   'assisted_damage',
                                   'frags'],
     CALCULATION_METHODS.SUMALL: ['avg_exp',
                                  'avg_damage_dealt',
                                  'avg_damage_assisted',
                                  'win_rate'],
     CALCULATION_METHODS.SUMMSEQN: ['battle_ts',
                                    'vehicle_cd',
                                    'battle_result',
                                    'is_in_squad',
                                    'exp',
                                    'damage',
                                    'assisted_damage',
                                    'frags',
                                    'used_in_calculations']}

    def __init__(self):
        self.__infoByType = {}
        self.__leaderboardID = None
        self.__leaderboardType = None
        self.__pageNumber = 1
        self.__pagesAmount = None
        self.__recalculationInterval = None
        self.__lastLeaderboardRecalculationTS = None
        self.__nextLeaderboardRecalculationTS = None
        self.__rewards = []
        self.__excelItems = []
        return

    def setData(self, rawData, leaderboardID, infoType, leaderboardType):
        if not self.__isDataStructureValid(rawData, infoType):
            if rawData:
                LOG_WARNING('LeaderBoard setData error: data structure error')
            return SET_DATA_STATUS_CODE.ERROR
        else:
            meta = rawData['meta']
            data = rawData['data']
            self.__infoByType = {}
            self.__leaderboardID = leaderboardID
            self.__leaderboardType = leaderboardType
            self.__pageNumber = meta['page_number']
            self.__pagesAmount = meta['pages_amount']
            self.__recalculationInterval = meta['recalculation_interval']
            self.__lastLeaderboardRecalculationTS = meta['last_leaderboard_recalculation_ts']
            self.__nextLeaderboardRecalculationTS = meta['next_leaderboard_recalculation_ts']
            rewardCategoryPage = 1
            self.__rewards = []
            for reward in meta['rewards']:
                rewardItem = RewardItem()
                rewardItem.setData(reward, rewardCategoryPage)
                rewardCategoryPage = reward['page_number']
                self.__rewards.append(rewardItem)

            if rewardCategoryPage is not None:
                rewardItem = RewardItem()
                rewardCat = defaultdict()
                rewardCat['reward_category_number'] = 5
                rewardItem.setData(rewardCat, rewardCategoryPage)
                self.__rewards.append(rewardItem)
            self.__excelItems = []
            for item in data:
                excelItem = ExcelItem()
                excelItem.setData(item, infoType)
                self.__excelItems.append(excelItem)

            return SET_DATA_STATUS_CODE.OK

    def getLeaderboardID(self):
        return self.__leaderboardID

    def getLeaderboardType(self):
        return self.__leaderboardType

    def getPageNumber(self):
        return self.__pageNumber

    def getPagesAmount(self):
        return self.__pagesAmount

    def getRewards(self):
        return self.__rewards

    def getExcelItems(self):
        return self.__excelItems

    def getRecalculationInterval(self):
        return self.__recalculationInterval

    def getLastLeaderboardRecalculationTS(self):
        return self.__lastLeaderboardRecalculationTS

    def getNextLeaderboardRecalculationTS(self):
        return self.__nextLeaderboardRecalculationTS

    def __isDataStructureValid(self, rawData, infoType):
        if not rawData or not isDataSchemaValid(self.EXPECTED_FIELDS, rawData):
            return False
        data = rawData['data']
        meta = rawData['meta']
        if not isDataSchemaValid(self.EXPECTED_FIELDS_META, meta):
            return False
        for rewardItem in meta['rewards']:
            if not isDataSchemaValid(self.EXPECTED_FIELDS_META_REWARDS, rewardItem):
                return False

        singleMethods = (CALCULATION_METHODS.MAX, CALCULATION_METHODS.SUMALL)
        if infoType in singleMethods:
            for dataItem in data:
                if not isDataSchemaValid(self.EXPECTED_FIELDS_DATA, dataItem):
                    return False
                if not isDataSchemaValid(self.CALCULATION_METHODS_EXPECTED_FIELDS[infoType], dataItem['info']):
                    return False

        else:
            for dataItem in data:
                if not isDataSchemaValid(self.EXPECTED_FIELDS_DATA, dataItem):
                    return False
                for infoItem in dataItem['info']:
                    if not isDataSchemaValid(self.CALCULATION_METHODS_EXPECTED_FIELDS[infoType], infoItem):
                        return False

        return True


class InfoItem(object):

    def __init__(self, methodType):
        self.__methodType = methodType

    def getMethodType(self):
        return self.__methodType


class InfoMax(InfoItem):

    def __init__(self, methodType, data):
        super(InfoMax, self).__init__(methodType)
        self.__battleTs = data['battle_ts']
        self.__vehicleCd = data['vehicle_cd']
        self.__battleResult = data['battle_result']
        self.__isInSquad = data['is_in_squad']
        self.__exp = data['exp']
        self.__damage = data['damage']
        self.__assistedDamage = data['assisted_damage']
        self.__frags = data['frags']
        self.__blockedDamage = data['blocked_damage']

    def getBattleTs(self):
        return self.__battleTs

    def getVehicleCd(self):
        return self.__vehicleCd

    def getBattleResult(self):
        return self.__battleResult

    def getIsInSquad(self):
        return self.__isInSquad

    def getExp(self):
        return self.__exp

    def getDamage(self):
        return self.__damage

    def getAssistedDamage(self):
        return self.__assistedDamage

    def getFrags(self):
        return self.__frags

    def getBlockedDamage(self):
        return self.__blockedDamage


class InfoSumM(InfoItem):

    def __init__(self, methodType, data):
        super(InfoSumM, self).__init__(methodType)
        self.__battleTs = data['battle_ts']
        self.__vehicleCd = data['vehicle_cd']
        self.__battleResult = data['battle_result']
        self.__isInSquad = data['is_in_squad']
        self.__exp = data['exp']
        self.__damage = data['damage']
        self.__assistedDamage = data['assisted_damage']
        self.__frags = data['frags']

    def getBattleTs(self):
        return self.__battleTs

    def getVehicleCd(self):
        return self.__vehicleCd

    def getBattleResult(self):
        return self.__battleResult

    def getIsInSquad(self):
        return self.__isInSquad

    def getExp(self):
        return self.__exp

    def getDamage(self):
        return self.__damage

    def getAssistedDamage(self):
        return self.__assistedDamage

    def getFrags(self):
        return self.__frags


class InfoSumSeqN(InfoItem):

    def __init__(self, methodType, data):
        super(InfoSumSeqN, self).__init__(methodType)
        self.__battleTs = data['battle_ts']
        self.__vehicleCd = data['vehicle_cd']
        self.__battleResult = data['battle_result']
        self.__isInSquad = data['is_in_squad']
        self.__exp = data['exp']
        self.__damage = data['damage']
        self.__assistedDamage = data['assisted_damage']
        self.__frags = data['frags']

    def getBattleTs(self):
        return self.__battleTs

    def getVehicleCd(self):
        return self.__vehicleCd

    def getBattleResult(self):
        return self.__battleResult

    def getIsInSquad(self):
        return self.__isInSquad

    def getExp(self):
        return self.__exp

    def getDamage(self):
        return self.__damage

    def getAssistedDamage(self):
        return self.__assistedDamage

    def getFrags(self):
        return self.__frags


class InfoSumAll(InfoItem):

    def __init__(self, methodType, data):
        super(InfoSumAll, self).__init__(methodType)
        self.__exp = data['avg_exp']
        self.__avgDamageDealt = data['avg_damage_dealt']
        self.__avgAssistedDamage = data['avg_damage_assisted']
        self.__winRate = data['win_rate']

    def getExp(self):
        return self.__exp

    def getAvgDamageDealt(self):
        return self.__avgDamageDealt

    def getAvgAssistedDamage(self):
        return self.__avgAssistedDamage

    def getWinRate(self):
        return self.__winRate


class InfoSumMSeqN(InfoItem):

    def __init__(self, methodType, data):
        super(InfoSumMSeqN, self).__init__(methodType)
        self.__battleTs = data['battle_ts']
        self.__vehicleCd = data['vehicle_cd']
        self.__battleResult = data['battle_result']
        self.__isInSquad = data['is_in_squad']
        self.__exp = data['exp']
        self.__damage = data['damage']
        self.__assistedDamage = data['assisted_damage']
        self.__frags = data['frags']
        self.__usedInCalculations = data['used_in_calculations']

    def getBattleTs(self):
        return self.__battleTs

    def getVehicleCd(self):
        return self.__vehicleCd

    def getBattleResult(self):
        return self.__battleResult

    def getIsInSquad(self):
        return self.__isInSquad

    def getExp(self):
        return self.__exp

    def getDamage(self):
        return self.__damage

    def getAssistedDamage(self):
        return self.__assistedDamage

    def getFrags(self):
        return self.__frags

    def getUsedInCalculations(self):
        return self.__usedInCalculations


CALCULATION_METHODS_TYPE = {CALCULATION_METHODS.MAX: InfoMax,
 CALCULATION_METHODS.SUMN: InfoSumM,
 CALCULATION_METHODS.SUMSEQN: InfoSumSeqN,
 CALCULATION_METHODS.SUMALL: InfoSumAll,
 CALCULATION_METHODS.SUMMSEQN: InfoSumMSeqN}

class ExcelItem(object):

    def __init__(self):
        self.__spaId = None
        self.__name = None
        self.__clanTag = None
        self.__clanColor = None
        self.__rank = None
        self.__p1 = None
        self.__p2 = None
        self.__p3 = None
        self.__info = None
        return

    def setData(self, data, methodType):
        self.__spaId = data['spa_id']
        self.__name = data['name']
        self.__clanTag = data['clan_tag']
        self.__clanColor = data['clan_color']
        self.__rank = data['rank']
        self.__p1 = data['p1']
        self.__p2 = data['p2']
        self.__p3 = data['p3']
        if methodType in CALCULATION_METHODS_TYPE and 'info' in data:
            self.__setInfoData(methodType, data['info'])

    def getSpaId(self):
        return self.__spaId

    def getName(self):
        return self.__name

    def getClanTag(self):
        return self.__clanTag

    def getClanColor(self):
        return self.__clanColor

    def getRank(self):
        return self.__rank

    def getP1(self):
        return self.__p1

    def getP2(self):
        return self.__p2

    def getP3(self):
        return self.__p3

    def getInfo(self):
        return self.__info

    def __setInfoData(self, methodType, data):
        singleMethods = (CALCULATION_METHODS.MAX, CALCULATION_METHODS.SUMALL)
        if methodType in singleMethods:
            self.__info = CALCULATION_METHODS_TYPE[methodType](methodType, data)
        else:
            self.__info = []
            for item in data:
                self.__info.append(CALCULATION_METHODS_TYPE[methodType](methodType, item))


class RewardItem(object):

    def __init__(self):
        self.__pageNumber = None
        self.__rewardCategoryNumber = None
        return

    def setData(self, data, pageNumber):
        self.__pageNumber = pageNumber
        self.__rewardCategoryNumber = data['reward_category_number']

    def getPageNumber(self):
        return self.__pageNumber

    def getRewardCategoryNumber(self):
        return self.__rewardCategoryNumber


class HangarFlagData(object):
    EXPECTED_FIELDS = ['meta', 'data']
    EXPECTED_FIELDS_META = ['is_special_account']
    EXPECTED_FIELDS_DATA = ['event_id', 'player_state']

    def __init__(self):
        self.__isSpecialAccount = False
        self.__hangarFlags = defaultdict()

    def cleanEventsData(self):
        self.__isSpecialAccount = False
        self.__hangarFlags.clear()

    def setData(self, rawData):
        if not self.__isDataStructureValid(rawData):
            if rawData:
                LOG_WARNING('HangarFlagData setData error: data structure error')
            return SET_DATA_STATUS_CODE.ERROR
        self.__isSpecialAccount = rawData['meta']['is_special_account']
        self.__hangarFlags.clear()
        for event in rawData['data']:
            self.__hangarFlags[event['event_id']] = event['player_state']

        return SET_DATA_STATUS_CODE.OK

    def getHangarFlags(self):
        return self.__hangarFlags

    def isSpecialAccount(self):
        return self.__isSpecialAccount

    def isRegistered(self, eventID):
        playerEventState = self.__hangarFlags.get(eventID, None)
        return playerEventState == EVENT_STATE.JOINED if playerEventState is not None else False

    def canJoin(self, eventID):
        playerEventState = self.__hangarFlags.get(eventID, None)
        return playerEventState == EVENT_STATE.UNDEFINED if playerEventState is not None else False

    def wasCanceled(self, eventID):
        playerEventState = self.__hangarFlags.get(eventID, None)
        return playerEventState == EVENT_STATE.CANCELED if playerEventState is not None else False

    def __isDataStructureValid(self, rawData):
        if rawData:
            if not isDataSchemaValid(self.EXPECTED_FIELDS, rawData):
                return False
            if not isDataSchemaValid(self.EXPECTED_FIELDS_META, rawData['meta']):
                return False
            for event in rawData['data']:
                if not isDataSchemaValid(self.EXPECTED_FIELDS_DATA, event):
                    return False

            return True
        return False


def isDataSchemaValid(expectedFields, data):
    if expectedFields is None or data is None:
        return False
    else:
        for field in expectedFields:
            if field not in data:
                return False

        return True

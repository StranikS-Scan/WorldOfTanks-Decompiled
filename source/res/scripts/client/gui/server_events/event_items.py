# Embedded file name: scripts/client/gui/server_events/event_items.py
import operator
import time
from abc import ABCMeta
from collections import namedtuple, OrderedDict
import nations
import constants
import ResMgr
import BigWorld
import ArenaType
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from potapov_quests import PQ_STATE as _PQS
from account_shared import AmmoIterator, getHistoricalCustomizedVehCompDescr
from helpers import getLocalizedData, i18n, time_utils, getClientLanguage
from gui import makeHtmlString
from gui.shared import g_itemsCache
from gui.shared.utils import CONST_CONTAINER, findFirst
from gui.shared.utils.functions import getAbsoluteUrl
from gui.server_events.bonuses import getBonusObj
from gui.server_events.modifiers import getModifierObj, compareModifiers
from gui.server_events.parsers import AccountRequirements, VehicleRequirements, PreBattleConditions, PostBattleConditions, BonusConditions
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.QUESTS import QUESTS
EventBattles = namedtuple('EventBattles', ['vehicleTags',
 'vehicles',
 'enabled',
 'arenaTypeID'])

class ServerEventAbstract(object):
    __metaclass__ = ABCMeta

    def __init__(self, eID, data):
        self._id = eID
        self._data = dict(data)

    def isGuiDisabled(self):
        return self._data.get('disableGui', False)

    def isHidden(self):
        return self._data.get('hidden', False)

    def getWeekDays(self):
        return self._data.get('weekDays', set())

    def getActiveTimeIntervals(self):
        if 'activeTimeIntervals' in self._data:
            return map(lambda (l, h): (l[0] * 3600 + l[1] * 60, h[0] * 3600 + h[1] * 60), self._data['activeTimeIntervals'])
        return []

    def getID(self):
        return self._id

    def getData(self):
        return self._data

    def getType(self):
        return self._data.get('type', 0)

    def getStartTime(self):
        if 'startTime' in self._data:
            return time_utils.makeLocalServerTime(self._data['startTime'])
        return time.time()

    def getFinishTime(self):
        if 'finishTime' in self._data:
            return time_utils.makeLocalServerTime(self._data['finishTime'])
        return time.time()

    def getCreationTime(self):
        if 'gStartTime' in self._data:
            return time_utils.makeLocalServerTime(self._data['gStartTime'])
        return time.time()

    def getDestroyingTime(self):
        if 'gFinishTime' in self._data:
            return time_utils.makeLocalServerTime(self._data['gFinishTime'])
        return time.time()

    def getCreationTimeLeft(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.getCreationTime())

    def getDestroyingTimeLeft(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.getDestroyingTime())

    def getUserName(self):
        return getLocalizedData(self._data, 'name')

    def getDescription(self):
        return getLocalizedData(self._data, 'description')

    def getStartTimeLeft(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.getStartTime())

    def getFinishTimeLeft(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.getFinishTime())

    def isOutOfDate(self):
        return self.getFinishTimeLeft() <= 0

    def getUserType(self):
        return ''

    def isIGR(self):
        return self._data.get('isIGR', False)

    def isCompleted(self, progress = None):
        return False

    def getNearestActivityTimeLeft(self):
        timeLeft = None
        if self.getStartTimeLeft() > 0:
            timeLeft = (self.getStartTimeLeft(), (0, time_utils.ONE_DAY))
        else:
            weekDays, timeIntervals = self.getWeekDays(), self.getActiveTimeIntervals()
            if len(weekDays) or len(timeIntervals):
                timeLeft = next(time_utils.ActivityIntervalsIterator(time_utils.getServerTimeCurrentDay(), time_utils.getServerRegionalWeekDay(), weekDays, timeIntervals))
        return timeLeft

    def hasPremIGRVehBonus(self):
        return False

    def isAvailable(self):
        if self.getStartTimeLeft() > 0:
            return (False, 'in_future')
        if self.isOutOfDate():
            return (False, 'out_of_date')
        if len(self.getWeekDays()) and time_utils.getServerRegionalWeekDay() not in self.getWeekDays():
            return (False, 'invalid_weekday')
        intervals = self.getActiveTimeIntervals()
        serverTime = time_utils.getServerTimeCurrentDay()
        if len(intervals):
            for low, high in intervals:
                if low <= serverTime <= high:
                    break
            else:
                return (False, 'invalid_time_interval')

        if not self._checkConditions():
            return (False, 'requirements')
        return (True, '')

    def getBonuses(self, bonusName = None):
        return []

    def _checkConditions(self):
        return True


class Quest(ServerEventAbstract):

    def __init__(self, qID, data, progress = None):
        import copy
        tmpData = copy.deepcopy(data)
        super(Quest, self).__init__(qID, data)
        self._progress = progress
        self._children, self._parents = {}, {}
        conds = dict(tmpData['conditions'])
        preBattle = dict(conds['preBattle'])
        self.accountReqs = AccountRequirements(preBattle['account'])
        self.vehicleReqs = VehicleRequirements(preBattle['vehicle'])
        self.preBattleCond = PreBattleConditions(preBattle['battle'])
        self.bonusCond = BonusConditions(conds['bonus'], self.getProgressData(), self.preBattleCond)
        self.postBattleCond = PostBattleConditions(conds['postBattle'], self.preBattleCond)

    def getUserType(self):
        if self.getType() == constants.EVENT_TYPE.FORT_QUEST:
            return i18n.makeString(QUESTS.ITEM_TYPE_SPECIALMISSION)
        return i18n.makeString(QUESTS.ITEM_TYPE_QUEST)

    def getProgressExpiryTime(self):
        return self._data.get('progressExpiryTime', time.time())

    def isCompletedByGroup(self, groupByKey):
        bonusLimit = self.bonusCond.getBonusLimit()
        if bonusLimit is not None:
            if self.bonusCond.getGroupByValue() is None:
                return self.isCompleted()
            if self._progress is not None:
                return bonusLimit <= self.getBonusCount(groupByKey)
        return False

    def isCompleted(self, progress = None):
        progress = progress or self._progress
        bonusLimit = self.bonusCond.getBonusLimit()
        if bonusLimit is not None:
            groupBy = self.bonusCond.getGroupByValue()
            if groupBy is None:
                return self.getBonusCount(progress=progress) >= bonusLimit
            if progress is not None:
                if groupBy == 'nation':
                    return self.__checkGroupedCompletion(nations.AVAILABLE_NAMES, progress, bonusLimit)
                if groupBy == 'level':
                    return self.__checkGroupedCompletion(xrange(1, constants.MAX_VEHICLE_LEVEL + 1), progress, bonusLimit, keyMaker=lambda lvl: 'level %d' % lvl)
                if groupBy == 'class':
                    return self.__checkGroupedCompletion(constants.VEHICLE_CLASSES, progress, bonusLimit)
                if groupBy == 'vehicle':
                    pass
        return super(Quest, self).isCompleted()

    def setChildren(self, children):
        self._children = children

    def getChildren(self):
        return self._children

    def setParents(self, parents):
        self._parents = parents

    def getParents(self):
        return self._parents

    def getBonusCount(self, groupByKey = None, progress = None):
        progress = progress or self._progress
        if progress is not None:
            groupBy = self.bonusCond.getGroupByValue()
            if groupBy is None:
                return progress.get(None, {}).get('bonusCount', 0)
            if groupByKey is not None:
                return progress.get(groupByKey, {}).get('bonusCount', 0)
            return sum((p.get('bonusCount', 0) for p in progress.itervalues()))
        else:
            return 0

    def getProgressData(self):
        return self._progress or {}

    def getBonuses(self, bonusName = None):
        result = []
        for n, v in self._data.get('bonus', {}).iteritems():
            if bonusName is not None and n != bonusName:
                continue
            b = getBonusObj(self, n, v)
            if b is not None:
                result.append(b)

        return result

    def hasPremIGRVehBonus(self):
        vehBonuses = self.getBonuses('vehicles')
        for vehBonus in vehBonuses:
            vehicles = vehBonus.getValue()
            for intCD, data in vehicles.iteritems():
                item = g_itemsCache.items.getItemByCD(intCD)
                if item.isPremiumIGR and data.get('rent', None) is not None:
                    return True

        return False

    def __checkGroupedCompletion(self, values, progress, bonusLimit = None, keyMaker = lambda v: v):
        bonusLimit = bonusLimit or self.bonusCond.getBonusLimit()
        for value in values:
            if bonusLimit > self.getBonusCount(groupByKey=keyMaker(value), progress=progress):
                return False

        return True

    def _checkConditions(self):
        isAccAvailable = self.accountReqs.isAvailable()
        isVehAvailable = self.vehicleReqs.isAnyVehicleAcceptable() or len(self.vehicleReqs.getSuitableVehicles()) > 0
        return isAccAvailable and isVehAvailable


class PersonalQuest(Quest):

    def __init__(self, qID, data, progress = None, expiryTime = None):
        super(PersonalQuest, self).__init__(qID, data, progress)
        self.expiryTime = expiryTime

    def getFinishTime(self):
        if self.expiryTime is not None:
            return min(super(PersonalQuest, self).getFinishTime(), self.expiryTime)
        else:
            return super(PersonalQuest, self).getFinishTime()


class Action(ServerEventAbstract):

    def getUserType(self):
        return i18n.makeString(QUESTS.ITEM_TYPE_ACTION)

    def getModifiers(self):
        result = {}
        for stepData in self._data.get('steps'):
            mName = stepData.get('name')
            m = getModifierObj(mName, stepData.get('params'))
            if m is None:
                continue
            if mName in result:
                result[mName].update(m)
            else:
                result[mName] = m

        return sorted(result.itervalues(), key=operator.methodcaller('getName'), cmp=compareModifiers)


class HistoricalBattle(ServerEventAbstract):
    ICONS_FOLDER = 'gui/maps/icons/historicalBattles/'
    ICONS_FORMAT = '%s.png'
    ICONS_MASK = '../maps/icons/historicalBattles/%s.png'
    MAP_ICONS_MASK = '../maps/icons/map/stats/%(prefix)s%(geometryName)s.png'

    class SIDES(CONST_CONTAINER):
        A = 'A'
        B = 'B'

    def getUserName(self):
        return getLocalizedData(self._data['localized_data'], 'title')

    def getDescription(self):
        return getLocalizedData(self._data['localized_data'], 'shortDescr')

    def getLongDescription(self):
        return getLocalizedData(self._data['localized_data'], 'longDescr')

    def getSideUserName(self, side):
        return getLocalizedData(self._data['localized_data'], 'sideNames').get(side)

    def getDescriptionUrl(self):
        histNote = self._data.get('urls', {}).get('histNote')
        if histNote is not None:
            return histNote % {'langID': getClientLanguage()}
        else:
            return

    def getIcon(self):
        iconID = self._data.get('backgroundName', 'default')
        icon = self.ICONS_MASK % iconID
        if self.ICONS_FORMAT % iconID not in ResMgr.openSection(self.ICONS_FOLDER).keys():
            icon = self.ICONS_MASK % 'default'
        return icon

    def isFuture(self):
        return self.getStartTimeLeft() > 0

    def getDatesInfo(self):
        return '%(startDate)s - %(endDate)s' % {'startDate': self.getStartDate(),
         'endDate': self.getFinishDate()}

    def getStartDate(self):
        return BigWorld.wg_getShortDateFormat(self.getStartTime())

    def getFinishDate(self):
        return BigWorld.wg_getShortDateFormat(self.getFinishTime())

    def getArenaTypeID(self):
        return self._data['arenaTypeID']

    def getArenaType(self):
        return ArenaType.g_cache[self.getArenaTypeID()]

    def getMapName(self):
        return i18n.makeString('#arenas:%s/name' % self.getArenaType().geometryName)

    def getMapInfo(self):
        arenaType = self.getArenaType()
        battleType = i18n.makeString('#arenas:type/%s/name' % arenaType.gameplayName)
        defTeam = self.SIDES.A
        assaultTeam = self.SIDES.B
        additionalInfo = ''
        if arenaType.gameplayName == 'assault':
            if self._data['arenaTeam1'] == self.SIDES.B:
                defTeam, assaultTeam = assaultTeam, defTeam
            additionalInfo = i18n.makeString('#historical_battles:map/assaultInfo', defTeam=self.getSideUserName(defTeam), assaultTeam=self.getSideUserName(assaultTeam))
        return '<b>%s</b>\n%s' % (battleType, additionalInfo)

    def getMapIcon(self):
        return self.MAP_ICONS_MASK % {'geometryName': self.getArenaType().geometryName,
         'prefix': ''}

    def getTeamRoster(self, side):
        result = []
        for intCD, team in self._data['vehSides'].iteritems():
            if team == side:
                result.append(intCD)

        return result

    def getVehiclesData(self):
        return self._data['vehicles']

    def getVehicleData(self, intCD):
        return self._data['vehicles'].get(intCD)

    def canParticipateWith(self, vehicleCompDescr):
        return vehicleCompDescr in self._data['vehicles']

    def getShellsLayout(self, intCD):
        vehicleData = self._data['vehicles'].get(intCD)
        if vehicleData is None:
            return tuple()
        else:
            return map(lambda data: (g_itemsCache.items.getItemByCD(data[0]), data[1]), AmmoIterator(vehicleData['ammoList']))

    def getShellsLayoutPrice(self, intCD):
        vehicleData = self._data['vehicles'].get(intCD)
        if vehicleData is None:
            return tuple()
        else:
            shellsLayout = vehicleData['ammoList']

            def calculateLayout(isBoughtForCredits):
                goldPrice = 0
                creditsPrice = 0
                for shellCompDescr, count in AmmoIterator(shellsLayout):
                    if not shellCompDescr or not count:
                        continue
                    shell = g_itemsCache.items.getItemByCD(shellCompDescr)
                    if shell.buyPrice[1] and not isBoughtForCredits:
                        goldPrice += shell.buyPrice[1] * count
                    elif shell.buyPrice[1] and isBoughtForCredits:
                        creditsPrice += shell.buyPrice[1] * count * g_itemsCache.items.shop.exchangeRateForShellsAndEqs
                    elif shell.buyPrice[0]:
                        creditsPrice += shell.buyPrice[0] * count

                return (creditsPrice, goldPrice)

            forCredits = calculateLayout(True)
            forGold = calculateLayout(False)
            if forCredits != forGold:
                return [calculateLayout(False), calculateLayout(True)]
            return [calculateLayout(True)]
            return

    def getShellsLayoutPriceStatus(self, intCD):
        userCredits = g_itemsCache.items.stats.credits
        userGold = g_itemsCache.items.stats.gold
        result = []
        for c, g in self.getShellsLayoutPrice(intCD):
            result.append((userGold >= g, userCredits >= c))

        return result

    def getShellsLayoutFormatedPrice(self, intCD, colorManager, checkMoney = True, joinString = False):
        userCredits = g_itemsCache.items.stats.credits
        userGold = g_itemsCache.items.stats.gold
        creditsColor = colorManager.getColorScheme('textColorCredits').get('rgb')
        goldColor = colorManager.getColorScheme('textColorGold').get('rgb')
        errorColor = colorManager.getColorScheme('textColorError').get('rgb')
        result = []
        for c, g in self.getShellsLayoutPrice(intCD):
            priceLabel = ''
            if g:
                params = {'value': BigWorld.wg_getGoldFormat(g),
                 'color': goldColor if not checkMoney or userGold >= g else errorColor,
                 'icon': getAbsoluteUrl(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2)}
                priceLabel += makeHtmlString('html_templates:lobby/historicalBattles/ammoStatus', 'priceLabel', params)
            if c:
                params = {'value': BigWorld.wg_getIntegralFormat(c),
                 'color': creditsColor if not checkMoney or userCredits >= c else errorColor,
                 'icon': getAbsoluteUrl(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2)}
                priceLabel += makeHtmlString('html_templates:lobby/historicalBattles/ammoStatus', 'priceLabel', params)
            result.append(priceLabel)

        if joinString:
            return i18n.makeString('#historical_battles:ammoPreset/priceConcat').join(result)
        return result

    def getModules(self, vehicle):
        vehicleData = self._data['vehicles'].get(vehicle.intCD)
        if vehicleData is None:
            return
        else:
            vDescr = self.getVehicleModifiedDescr(vehicle)
            result = OrderedDict()
            for guiItemType in GUI_ITEM_TYPE.VEHICLE_MODULES:
                if guiItemType == GUI_ITEM_TYPE.TURRET and not vehicle.hasTurrets:
                    continue
                itemDescr, _ = vDescr.getComponentsByType(GUI_ITEM_TYPE_NAMES[guiItemType])
                result[guiItemType] = g_itemsCache.items.getItemByCD(itemDescr['compactDescr'])

            return result

    def getVehicleModifiedDescr(self, vehicle):
        updatedVehDescr = vehicle.descriptor
        if self.canParticipateWith(vehicle.intCD):
            from gui import game_control
            igrRoomType = game_control.g_instance.igr.getRoomType()
            igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
            updatedVehDescr = getHistoricalCustomizedVehCompDescr(igrLayout, vehicle.invID, igrRoomType, updatedVehDescr.makeCompactDescr(), self._data)
        return updatedVehDescr

    def __cmp__(self, other):
        return cmp(self.getStartTime(), other.getStartTime())


class PQSeason(object):

    def __init__(self, seasonID, info):
        self.__id = seasonID
        self.__info = info
        self.__tiles = {}
        self.__isUnlocked = False

    def getID(self):
        return self.__id

    def getName(self):
        return self.__info['name']

    def getUserName(self):
        return self.__info['userString']

    def getUserDescription(self):
        return self.__info['description']

    def getTiles(self):
        return self.__tiles

    def isUnlocked(self):
        return self.__isUnlocked

    def updateProgress(self, eventsCache):
        for tile in self.__tiles.itervalues():
            if tile.isUnlocked():
                self.__isUnlocked = True
                break

    def _addTile(self, tile):
        if tile.getID() not in self.__tiles:
            self.__tiles[tile.getID()] = tile


class PQTile(object):

    def __init__(self, tileID, info):
        self.__id = tileID
        self.__info = info
        self.__quests = {}
        self.__initialQuests = {}
        self.__finalQuests = {}
        self.__isUnlocked = False
        self.__achievements = dict(((chID, (ACHIEVEMENT_BLOCK.TOTAL, aName)) for chID, aName in self.__info['achievements'].iteritems()))
        self.__tokens = {}
        self.__bonuses = {}
        self.__isAwardAchieved = False

    def getID(self):
        return self.__id

    def getNextTileID(self):
        return self.__info['nextTileID']

    def getName(self):
        return self.__info['name']

    def getUserName(self):
        return self.__info['userString']

    def getUserDescription(self):
        return self.__info['description']

    def getChainVehicleClass(self, chainID):
        firstQuest = findFirst(None, self.__quests.get(chainID, {}).itervalues())
        if firstQuest is not None:
            return findFirst(None, firstQuest.getVehicleClasses())
        else:
            return

    def getChainTotalTokensCount(self, chainID, isMainBonuses = None):
        result = 0
        for q in self.__quests[chainID].itervalues():
            for tokenBonus in q.getBonuses('tokens', isMainBonuses):
                for token in tokenBonus.getTokens().itervalues():
                    result += token.count

        return result

    def getIconID(self):
        return self.__info['iconID']

    def getSeasonID(self):
        return self.__info['seasonID']

    def getChainSize(self):
        return self.__info['questsInChain']

    def getQuestsCount(self):
        return self.__info['chainsCount'] * self.getChainSize()

    def getPrice(self):
        return self.__info['price']

    def getQuests(self):
        return self.__quests

    def getQuestsInChainByFilter(self, chainID, filterFunc = lambda v: True):
        result = {}
        for qID, q in self.__quests[chainID].iteritems():
            if filterFunc(q):
                result[qID] = q

        return result

    def getQuestsByFilter(self, filterFunc = lambda v: True):
        result = {}
        for _, quests in self.__quests.iteritems():
            for qID, q in quests.iteritems():
                if filterFunc(q):
                    result[qID] = q

        return result

    def getInProgressQuests(self):
        return self.getQuestsByFilter(lambda quest: quest.isInProgress())

    def getCompletedQuests(self, isRewardReceived = None):
        return self.getQuestsByFilter(lambda quest: quest.isCompleted(isRewardReceived=isRewardReceived))

    def getFullCompletedQuests(self, isRewardReceived = None):
        return self.getQuestsByFilter(lambda quest: quest.isFullCompleted(isRewardReceived=isRewardReceived))

    def isCompleted(self, isRewardReceived = None):
        return len(self.getCompletedQuests(isRewardReceived)) == self.getQuestsCount()

    def isInProgress(self):
        return len(self.getInProgressQuests()) > 0

    def isFullCompleted(self, isRewardReceived = None):
        return len(self.getFullCompletedQuests(isRewardReceived)) == self.getQuestsCount()

    def isAwardAchieved(self):
        return self.__isAwardAchieved

    def getCompletedFinalQuests(self, isRewardReceived = None):
        return self.getQuestsByFilter(lambda quest: quest.isCompleted(isRewardReceived=isRewardReceived) and quest.isFinal())

    def getInitialQuests(self):
        return self.__initialQuests

    def getFinalQuests(self):
        return self.__finalQuests

    def isUnlocked(self):
        return self.__isUnlocked

    def getAchievements(self):
        return self.__achievements

    def getTokens(self):
        return self.__tokens

    def getTokensCount(self):
        return tuple((sum(map(operator.itemgetter(i), self.__tokens.values())) for i in xrange(2)))

    def getTotalTokensCount(self):
        result = 0
        for chainID in self.__quests.iterkeys():
            result += self.getChainTotalTokensCount(chainID)

        return result

    def getBonuses(self):
        return self.__bonuses

    def getVehicleBonus(self):
        for bonuses in self.getBonuses().itervalues():
            for bonus in bonuses:
                if bonus.getName() == 'vehicles':
                    for vehicle, _ in bonus.getVehicles():
                        return vehicle

        return None

    def updateProgress(self, eventsCache):
        qp = eventsCache.questsProgress
        self.__isUnlocked = False
        for quest in self.__initialQuests.itervalues():
            if quest.isUnlocked():
                self.__isUnlocked = True
                break

        self.__tokens, self.__bonuses = {}, {}
        for quest in eventsCache.getHiddenQuests().itervalues():
            for token in quest.accountReqs.getTokens():
                if token.getID() in self.__info['tokens']:
                    self.__tokens[token.getID()] = (qp.getTokenCount(token.getID()), token.getNeededCount())
                    self.__bonuses.setdefault(token.getID(), []).extend(quest.getBonuses())

        def _getTokensFromBonuses(bonuses):
            result = 0
            for tokenBonus in bonuses:
                for t in tokenBonus.getTokens().itervalues():
                    result += t.count

            return result

        gottenTokensCount = 0
        for quests in self.__quests.itervalues():
            for q in quests.itervalues():
                if q.isMainCompleted(isRewardReceived=True):
                    gottenTokensCount += _getTokensFromBonuses(q.getBonuses('tokens', isMain=True))
                if q.isFullCompleted(isRewardReceived=True):
                    gottenTokensCount += _getTokensFromBonuses(q.getBonuses('tokens', isMain=False))

        _, neededTokensCount = self.getTokensCount()
        self.__isAwardAchieved = gottenTokensCount >= neededTokensCount

    def _addQuest(self, quest):
        questID = quest.getID()
        chain = self.__quests.setdefault(quest.getChainID(), {})
        if questID not in chain:
            chain[questID] = quest
            if quest.isInitial():
                self.__initialQuests[questID] = quest
            elif quest.isFinal():
                self.__finalQuests[questID] = quest


class PotapovQuest(Quest):

    def __init__(self, qID, pqType, pqProgress = None, seasonID = None):
        super(PotapovQuest, self).__init__(qID, pqType.mainQuestInfo)
        self.__pqType = pqType
        self.__pqProgress = pqProgress
        self.__seasonID = seasonID

    def getPQType(self):
        return self.__pqType

    def getMainQuestID(self):
        return self.__pqType.mainQuestInfo['id']

    def getAddQuestID(self):
        return self.__pqType.addQuestInfo['id']

    def getChainID(self):
        return self.__pqType.chainID

    def getTileID(self):
        return self.__pqType.tileID

    def setSeasonID(self, seasonID):
        self.__seasonID = seasonID

    def getSeasonID(self):
        return self.__seasonID

    def getUserType(self):
        return i18n.makeString('#quests:item/type/potapov')

    def getUserName(self):
        return self.__pqType.userString

    def getUserDescription(self):
        return self.__pqType.description

    def getUserAdvice(self):
        return self.__pqType.advice

    def getUserMainCondition(self):
        return self.__pqType.conditionMain

    def getUserAddCondition(self):
        return self.__pqType.conditionAdd

    def getVehMinLevel(self):
        return self.__pqType.minLevel

    def isUnlocked(self):
        return self.__pqProgress is not None and self.__pqProgress.unlocked

    def isInProgress(self):
        return self.__pqProgress is not None and self.__pqProgress.selected and not self.needToGetReward()

    def hasProgress(self):
        return self.__pqProgress.state > _PQS.NONE

    def isInitial(self):
        return self.__pqType.isInitial

    def isFinal(self):
        return self.__pqType.isFinal

    def getVehicleClasses(self):
        return set(self.__pqType.vehClasses)

    def isMainCompleted(self, isRewardReceived = None):
        if isRewardReceived is True:
            states = (_PQS.MAIN_REWARD_GOTTEN, _PQS.ALL_REWARDS_GOTTEN)
        elif isRewardReceived is False:
            states = (_PQS.NEED_GET_MAIN_REWARD, _PQS.NEED_GET_ALL_REWARDS)
        else:
            states = (_PQS.MAIN_REWARD_GOTTEN,
             _PQS.ALL_REWARDS_GOTTEN,
             _PQS.NEED_GET_MAIN_REWARD,
             _PQS.NEED_GET_ALL_REWARDS)
        return self.__checkForStates(*states)

    def isFullCompleted(self, isRewardReceived = None):
        if isRewardReceived is True:
            states = (_PQS.ALL_REWARDS_GOTTEN,)
        elif isRewardReceived is False:
            states = (_PQS.NEED_GET_ALL_REWARDS,)
        else:
            states = _PQS.COMPLETED
        return self.__checkForStates(*states)

    def isCompleted(self, progress = None, isRewardReceived = None):
        return self.isMainCompleted(isRewardReceived) or self.isFullCompleted(isRewardReceived)

    def canBeSelected(self):
        return self.isUnlocked() and not self.isFullCompleted() and not self.isInProgress()

    def isDone(self):
        return self.__checkForStates(_PQS.ALL_REWARDS_GOTTEN)

    def needToGetMainReward(self):
        return self.__checkForStates(_PQS.NEED_GET_ALL_REWARDS, _PQS.NEED_GET_MAIN_REWARD)

    def needToGetAddReward(self):
        return self.__checkForStates(_PQS.NEED_GET_ALL_REWARDS, _PQS.NEED_GET_ADD_REWARD)

    def needToGetAllReward(self):
        return self.__checkForStates(_PQS.NEED_GET_ALL_REWARDS)

    def needToGetReward(self):
        return self.__checkForStates(*_PQS.NEED_GET_REWARD)

    def updateProgress(self, eventsCache):
        self.__pqProgress = eventsCache.questsProgress.getPotapovQuestProgress(self.__pqType, self._id)

    def getBonuses(self, bonusName = None, isMain = None):
        if isMain is None:
            data = (self.__pqType.mainQuestInfo, self.__pqType.addQuestInfo)
        elif isMain:
            data = (self.__pqType.mainQuestInfo,)
        else:
            data = (self.__pqType.addQuestInfo,)
        result = []
        for d in data:
            for n, v in d.get('bonus', {}).iteritems():
                if bonusName is not None and n != bonusName:
                    continue
                b = getBonusObj(self, n, v)
                if b is not None:
                    result.append(b)

        return result

    def getTankmanBonus(self):
        for isMainBonus in (True, False):
            for bonus in self.getBonuses(isMain=isMainBonus):
                if bonus.getName() == 'tankmen':
                    return (bonus, isMainBonus)

        return (None, None)

    def __checkForStates(self, *statesToCheck):
        return self.__pqProgress is not None and self.__pqProgress.state in statesToCheck

    def __repr__(self):
        return 'PQuest<id=%d; state=%s; unlocked=%s>' % (self._id, self.__pqProgress.state, self.isUnlocked())


def _getTileIconPath(tileIconID, prefix, state):
    return '../maps/icons/quests/tiles/%s_%s_%s.png' % (tileIconID, prefix, state)


def getTileNormalUpIconPath(tileIconID):
    return _getTileIconPath(tileIconID, 'color', 'up')


def getTileNormalOverIconPath(tileIconID):
    return _getTileIconPath(tileIconID, 'color', 'over')


def getTileGrayUpIconPath(tileIconID):
    return _getTileIconPath(tileIconID, 'gray', 'up')


def getTileGrayOverIconPath(tileIconID):
    return _getTileIconPath(tileIconID, 'gray', 'over')


def getTileAnimationPath(tileIconID):
    return '../flash/animations/questTiles/%s.swf' % tileIconID


def createQuest(questType, qID, data, progress = None, expiryTime = None):
    if questType == constants.EVENT_TYPE.PERSONAL_QUEST:
        return PersonalQuest(qID, data, progress, expiryTime)
    return Quest(qID, data, progress)

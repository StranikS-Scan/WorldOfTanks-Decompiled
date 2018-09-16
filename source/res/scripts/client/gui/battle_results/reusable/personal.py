# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/personal.py
from collections import namedtuple
import itertools
from ValueReplay import ValueReplay, ValueReplayConnector
from battle_results_shared import VEH_FULL_RESULTS
from debug_utils import LOG_ERROR
from dossiers2.custom.records import RECORD_DB_IDS
from gui.battle_results.reusable import records
from gui.battle_results.reusable import shared
from gui.battle_results.reusable import sort_keys
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.battle_results.settings import FACTOR_VALUE
from gui.ranked_battles.ranked_models import PostBattleRankInfo
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.shared.money import Currency
_LifeTimeInfo = namedtuple('_LifeTimeInfo', ('isKilled', 'lifeTime'))

class _SquadBonusInfo(object):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__vehicles', '__joinedOnArena', '__size')

    def __init__(self, vehicles=None, joinedOnArena=None, size=0, **kwargs):
        super(_SquadBonusInfo, self).__init__()
        self.__vehicles = vehicles or set()
        self.__joinedOnArena = joinedOnArena or []
        self.__size = size

    def getVehiclesLevelsDistance(self):
        getter = self.itemsCache.items.getItemByCD
        levels = [ getter(typeCompDescr).level for typeCompDescr in self.__vehicles ]
        levels.sort()
        return levels[-1] - levels[0] if levels else -1

    def getSquadFlags(self, vehicleID, intCD):
        showSquadLabels = True
        squadHasBonus = False
        if self.eventsCache.isSquadXpFactorsEnabled() and self.__size > 1:
            if vehicleID in self.__joinedOnArena:
                showSquadLabels = False
            else:
                distance = self.getVehiclesLevelsDistance()
                if intCD:
                    level = self.itemsCache.items.getItemByCD(intCD).level
                    key = (distance, level)
                    showSquadLabels = key not in self.eventsCache.getSquadZeroBonuses()
                squadHasBonus = distance in self.eventsCache.getSquadBonusLevelDistance()
        else:
            showSquadLabels = False
        return (showSquadLabels, squadHasBonus)


class _PersonalAvatarInfo(object):
    __slots__ = ('__accountDBID', '__clanDBID', '__team', '__isPrematureLeave', '__fairplayViolations', '__squadBonusInfo', '__winnerIfDraw', '__eligibleForCrystalRewards', '__extInfo')

    def __init__(self, accountDBID=0, clanDBID=0, team=0, isPrematureLeave=False, fairplayViolations=None, squadBonusInfo=None, winnerIfDraw=0, eligibleForCrystalRewards=False, **kwargs):
        super(_PersonalAvatarInfo, self).__init__()
        self.__accountDBID = accountDBID
        self.__clanDBID = clanDBID
        self.__team = team
        self.__isPrematureLeave = isPrematureLeave
        self.__eligibleForCrystalRewards = eligibleForCrystalRewards
        self.__fairplayViolations = shared.FairplayViolationsInfo(*(fairplayViolations or ()))
        self.__squadBonusInfo = _SquadBonusInfo(**(squadBonusInfo or {}))
        self.__winnerIfDraw = winnerIfDraw
        self.__extInfo = kwargs.get('ext', None)
        return

    @property
    def accountDBID(self):
        return self.__accountDBID

    @property
    def clanDBID(self):
        return self.__clanDBID

    @property
    def team(self):
        return self.__team

    @property
    def isPrematureLeave(self):
        return self.__isPrematureLeave

    @property
    def winnerIfDraw(self):
        return self.__winnerIfDraw

    @property
    def eligibleForCrystalRewards(self):
        return self.__eligibleForCrystalRewards

    @property
    def extensionInfo(self):
        return self.__extInfo

    def getPersonalSquadFlags(self, vehicles):
        vehicleID = vehicles.getVehicleID(self.__accountDBID)
        return self.__squadBonusInfo.getSquadFlags(vehicleID, vehicles.getVehicleInfo(vehicleID).intCD)

    def hasPenalties(self):
        return self.__fairplayViolations.hasPenalties()

    def getPenaltyDetails(self):
        return self.__fairplayViolations.getPenaltyDetails()


class _AutoCompletionRecords(records.RawRecords):
    __slots__ = ()

    def __init__(self, results):
        rawRecords = {}
        if 'autoRepairCost' in results:
            cost = results['autoRepairCost']
            if cost is not None:
                rawRecords['autoRepairCost'] = -cost
        if 'autoLoadCost' in results:
            cost = results['autoLoadCost']
            if cost is not None:
                rawRecords['autoLoadCredits'] = -cost[0]
                rawRecords['autoLoadGold'] = -cost[1]
        if 'autoEquipCost' in results:
            cost = results['autoEquipCost']
            if cost is not None:
                rawRecords['autoEquipCredits'] = -cost[0]
                rawRecords['autoEquipGold'] = -cost[1]
        super(_AutoCompletionRecords, self).__init__(rawRecords)
        return


class _CreditsReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, originalCreditsToDraw, achievementCredits):
        super(_CreditsReplayRecords, self).__init__(replay, 'credits')
        self._addRecord(ValueReplay.SUB, 'originalCreditsToDraw', originalCreditsToDraw, 0)
        self._addRecord(ValueReplay.SET, 'achievementCredits', achievementCredits, 0)

    def _getRecord(self, name):
        value = super(_CreditsReplayRecords, self)._getRecord(name)
        if name in ('originalCreditsToDraw', 'achievementCredits'):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumCreditsFactor10'))
        return value


class _XPReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, isHighScope, achievementXP):
        super(_XPReplayRecords, self).__init__(replay, 'xp')
        if isHighScope:
            self._addRecord(ValueReplay.SET, 'isHighScope', 1, 0)
        self._addRecord(ValueReplay.SET, 'achievementXP', achievementXP, 0)
        self._addRecord(ValueReplay.SET, 'xpToShow', max(0, self.getRecord('xp') - self.getRecord('premiumVehicleXPFactor100')), 0)

    def _getRecord(self, name):
        value = super(_XPReplayRecords, self)._getRecord(name)
        if name in ('achievementXP',):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumXPFactor10'))
        return value


class _FreeXPReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, achievementFreeXP):
        super(_FreeXPReplayRecords, self).__init__(replay, 'freeXP')
        self._addRecord(ValueReplay.SET, 'achievementFreeXP', achievementFreeXP, 0)

    def _getRecord(self, name):
        value = super(_FreeXPReplayRecords, self)._getRecord(name)
        if name in ('achievementFreeXP',):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumXPFactor10'))
        return value


class _EconomicsRecordsChains(object):
    __slots__ = ('_baseCredits', '_premiumCredits', '_goldRecords', '_autoRecords', '_baseXP', '_premiumXP', '_baseFreeXP', '_premiumFreeXP', '_fortResource', '_crystal', '_crystalDetails', '_zeroEarnings')

    def __init__(self):
        super(_EconomicsRecordsChains, self).__init__()
        self._baseCredits = records.RecordsIterator()
        self._premiumCredits = records.RecordsIterator()
        self._goldRecords = records.RecordsIterator()
        self._autoRecords = records.RecordsIterator()
        self._baseXP = records.RecordsIterator()
        self._premiumXP = records.RecordsIterator()
        self._baseFreeXP = records.RecordsIterator()
        self._premiumFreeXP = records.RecordsIterator()
        self._crystal = records.RecordsIterator()
        self._crystalDetails = []
        self._zeroEarnings = False

    def getBaseCreditsRecords(self):
        return self._baseCredits

    def isZeroEarnings(self):
        return self._zeroEarnings

    def getPremiumCreditsRecords(self):
        return self._premiumCredits

    def getCreditsDiff(self):
        return self._premiumCredits.getRecord('credits', 'originalCreditsToDraw') - self._baseCredits.getRecord('credits', 'originalCreditsToDraw')

    def getBaseXPRecords(self):
        return self._baseXP

    def getPremiumXPRecords(self):
        return self._premiumXP

    def getMoneyRecords(self):
        return itertools.izip(self._baseCredits, self._premiumCredits, self._goldRecords, self._autoRecords)

    def getCrystalRecords(self):
        return itertools.izip(self._crystal, self._crystal)

    def getCrystalDetails(self):
        return self._crystalDetails

    def getXPRecords(self):
        return itertools.izip(self._baseXP, self._premiumXP, self._baseFreeXP, self._premiumFreeXP)

    def getXPDiff(self):
        return self._premiumXP.getRecord('xp') - self._baseXP.getRecord('xp')

    def addResults(self, _, results):
        connector = ValueReplayConnector(VEH_FULL_RESULTS, results)
        self._zeroEarnings = not any((results.get('credits'),
         results.get('gold'),
         results.get('freeXP'),
         results.get('crystal')))
        self._addMoneyResults(connector, results)
        self._addXPResults(connector, results)
        self._addCrystalResults(connector, results)

    def _addMoneyResults(self, connector, results):
        if 'creditsReplay' in results and results['creditsReplay'] is not None:
            replay = ValueReplay(connector, recordName='credits', replay=results['creditsReplay'])
            if 'appliedPremiumCreditsFactor10' in replay:
                replay['appliedPremiumCreditsFactor10'] = FACTOR_VALUE.BASE_CREDITS_FACTOR
            self._baseCredits.addRecords(_CreditsReplayRecords(replay, results['originalCreditsToDraw'], results['achievementCredits']))
            if 'appliedPremiumCreditsFactor10' in replay:
                replay['appliedPremiumCreditsFactor10'] = FACTOR_VALUE.PREMUIM_CREDITS_FACTOR
            self._premiumCredits.addRecords(_CreditsReplayRecords(replay, results['originalCreditsToDraw'], results['achievementCredits']))
        else:
            LOG_ERROR('Credits replay is not found', results)
        if 'goldReplay' in results and results['goldReplay'] is not None:
            replay = ValueReplay(connector, recordName='gold', replay=results['goldReplay'])
            self._goldRecords.addRecords(records.ReplayRecords(replay, 'gold'))
        else:
            LOG_ERROR('Gold replay is not found', results)
        self._autoRecords.addRecords(_AutoCompletionRecords(results))
        return

    def _addXPResults(self, connector, results):
        if 'xpReplay' in results and results['xpReplay'] is not None:
            replay = ValueReplay(connector, recordName='xp', replay=results['xpReplay'])
            isHighScope = RECORD_DB_IDS[('max15x15', 'maxXP')] in [ recordID for recordID, _ in results.get('dossierPopUps', []) ]
            if 'appliedPremiumXPFactor10' in replay:
                replay['appliedPremiumXPFactor10'] = FACTOR_VALUE.BASE_XP_FACTOR
            self._baseXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            if 'appliedPremiumXPFactor10' in replay:
                replay['appliedPremiumXPFactor10'] = FACTOR_VALUE.PREMUIM_XP_FACTOR
            self._premiumXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
        else:
            LOG_ERROR('XP replay is not found', results)
        if 'freeXPReplay' in results and results['freeXPReplay'] is not None:
            replay = ValueReplay(connector, recordName='freeXP', replay=results['freeXPReplay'])
            if 'appliedPremiumXPFactor10' in replay:
                replay['appliedPremiumXPFactor10'] = FACTOR_VALUE.BASE_XP_FACTOR
            self._baseFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            if 'appliedPremiumXPFactor10' in replay:
                replay['appliedPremiumXPFactor10'] = FACTOR_VALUE.PREMUIM_XP_FACTOR
            self._premiumFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
        else:
            LOG_ERROR('Free XP replay is not found', results)
        return

    def _addCrystalResults(self, connector, results):
        if 'crystalReplay' in results and results['crystalReplay'] is not None:
            replay = ValueReplay(connector, recordName=Currency.CRYSTAL, replay=results['crystalReplay'])
            self._crystal.addRecords(records.ReplayRecords(replay, Currency.CRYSTAL))
            self._addCrystalDetails(replay)
        else:
            LOG_ERROR('crystal replay is not found', results)
        return

    def _addCrystalDetails(self, replay):
        medalToken = 'eventCrystalList_'
        for _, (appliedName, appliedValue), (_, _) in replay:
            if appliedName == 'originalCrystal' and appliedValue:
                self._crystalDetails.insert(0, (appliedName, appliedValue))
            if appliedName.startswith(medalToken):
                achievementName = appliedName.split(medalToken)[1]
                self._crystalDetails.append((achievementName, appliedValue))


class PersonalInfo(shared.UnpackedInfo):
    __slots__ = ('__avatar', '__vehicles', '__lifeTimeInfo', '__isObserver', '__economicsRecords', '__isPremium', '__questsProgress', '__PM2Progress', '__rankInfo')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, personal):
        super(PersonalInfo, self).__init__()
        if _RECORD.PERSONAL_AVATAR in personal and personal[_RECORD.PERSONAL_AVATAR] is not None:
            self.__avatar = _PersonalAvatarInfo(**personal[_RECORD.PERSONAL_AVATAR])
        else:
            self.__avatar = _PersonalAvatarInfo()
            self._addUnpackedItemID(_RECORD.PERSONAL_AVATAR)
        self.__vehicles = []
        self.__isObserver = False
        self.__isPremium = False
        self.__economicsRecords = _EconomicsRecordsChains()
        self.__lifeTimeInfo = _LifeTimeInfo(False, 0)
        self.__questsProgress = {}
        self.__PM2Progress = {}
        self.__rankInfo = PostBattleRankInfo(0, 0, 0, 0, 0, 0, 0, 0, 0, {}, {})
        if not self.hasUnpackedItems():
            self.__collectRequiredData(personal)
        return

    @property
    def avatar(self):
        return self.__avatar

    @property
    def isObserver(self):
        return self.__isObserver

    @property
    def isPremium(self):
        return self.__isPremium

    def getVehicleCDsIterator(self, result):
        for intCD in self.__vehicles:
            if intCD not in result:
                continue
            yield (intCD, result[intCD])

    def getVehicleItemsIterator(self):
        getItemByCD = self.itemsCache.items.getItemByCD
        for intCD in self.__vehicles:
            yield (intCD, getItemByCD(intCD))

    def getAchievements(self, result):
        left = []
        right = []
        for intCD in self.__vehicles:
            if intCD not in result:
                continue
            data = result[intCD]
            achievements = shared.makeAchievementFromPersonal(data)
            for direction, achievement in achievements:
                if direction == 1:
                    right.append((achievement, True))
                left.append((achievement, True))

            achievement = shared.makeMarkOfMasteryFromPersonal(data)
            if achievement is not None:
                left.append((achievement, False))

        return (left, sorted(right, key=sort_keys.AchievementSortKey))

    def getLifeTimeInfo(self):
        return self.__lifeTimeInfo

    def getQuestsProgress(self):
        return self.__questsProgress

    def getPM2Progress(self):
        return self.__PM2Progress

    def getRankInfo(self):
        return self.__rankInfo

    def getBaseCreditsRecords(self):
        return self.__economicsRecords.getBaseCreditsRecords()

    def isWGMoneyRelatedZeroEarnings(self):
        return self.__economicsRecords.isZeroEarnings()

    def getPremiumCreditsRecords(self):
        return self.__economicsRecords.getPremiumCreditsRecords()

    def getCreditsDiff(self):
        return self.__economicsRecords.getCreditsDiff()

    def getMoneyRecords(self):
        return self.__economicsRecords.getMoneyRecords()

    def getCrystalRecords(self):
        return self.__economicsRecords.getCrystalRecords()

    def getBaseXPRecords(self):
        return self.__economicsRecords.getBaseXPRecords()

    def getPremiumXPRecords(self):
        return self.__economicsRecords.getPremiumXPRecords()

    def getXPRecords(self):
        return self.__economicsRecords.getXPRecords()

    def getXPDiff(self):
        return self.__economicsRecords.getXPDiff()

    def getCrystalDetails(self):
        return self.__economicsRecords.getCrystalDetails()

    def __collectRequiredData(self, info):
        getItemByCD = self.itemsCache.items.getItemByCD
        itemCDs = [ key for key in info.keys() if isinstance(key, (int, long, float)) ]
        items = sorted((getItemByCD(itemCD) for itemCD in itemCDs))
        lifeTimes = []
        infoAvatar = info['avatar']
        if infoAvatar:
            self.__questsProgress.update(infoAvatar.get('questsProgress', {}))
            self.__PM2Progress.update(infoAvatar.get('PM2Progress', {}))
            self.__rankInfo = PostBattleRankInfo.fromDict(infoAvatar)
        for item in items:
            intCD = item.intCD
            data = info[intCD]
            if data is None:
                self._addUnpackedItemID(intCD)
                continue
            self.__vehicles.append(intCD)
            self.__economicsRecords.addResults(intCD, data)
            if not self.__isObserver:
                self.__isObserver = item.isObserver
            killerID = data['killerID'] if 'killerID' in data else 0
            lifeTime = data['lifeTime'] if 'lifeTime' in data else 0
            if killerID and lifeTime:
                lifeTimes.append(lifeTime)
            if not self.__isPremium and data.get('isPremium', False):
                self.__isPremium = True
            self.__questsProgress.update(data.get('questsProgress', {}))
            self.__PM2Progress.update(data.get('PM2Progress', {}))

        if lifeTimes:
            self.__lifeTimeInfo = _LifeTimeInfo(True, min(lifeTimes))
        return

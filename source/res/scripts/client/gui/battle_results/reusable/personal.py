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
        if levels:
            return levels[-1] - levels[0]
        else:
            return -1

    def getSquadFlags(self, vehicleID, intCD):
        """Gets flags to resolve wherever showing squad bonus and squad labels.
        :param vehicleID: long containing player's vehicle ID
        :param intCD: int containing int-type compact descriptor for player's vehicle.
        :return: tuple(showSquadLabels, squadHasBonus).
        """
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
    """Class contains information about personal avatar."""
    __slots__ = ('__accountDBID', '__clanDBID', '__team', '__isPrematureLeave', '__fairplayViolations', '__squadBonusInfo', '__winnerIfDraw', '__eligibleForCrystalRewards')

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

    @property
    def accountDBID(self):
        """Gets personal account's database ID."""
        return self.__accountDBID

    @property
    def clanDBID(self):
        """Gets personal clan database ID."""
        return self.__clanDBID

    @property
    def team(self):
        """Gets number of personal team."""
        return self.__team

    @property
    def isPrematureLeave(self):
        """Does player leave the battle while his vehicle is alive?"""
        return self.__isPrematureLeave

    @property
    def winnerIfDraw(self):
        """Get winner id if draw."""
        return self.__winnerIfDraw

    @property
    def eligibleForCrystalRewards(self):
        """Gets if crystals are awarded in this battle."""
        return self.__eligibleForCrystalRewards

    def getPersonalSquadFlags(self, vehicles):
        """Gets flags to resolve wherever showing squad bonus and squad labels.
        :param vehicles: instance of VehiclesInfo.
        :return: tuple(showSquadLabels, squadHasBonus).
        """
        vehicleID = vehicles.getVehicleID(self.__accountDBID)
        return self.__squadBonusInfo.getSquadFlags(vehicleID, vehicles.getVehicleInfo(vehicleID).intCD)

    def hasPenalties(self):
        """Have fairplay penalties?
        :return: bool.
        """
        return self.__fairplayViolations.hasPenalties()

    def getPenaltyDetails(self):
        """Gets penalty details if they have.
        :return: tuple(name of penalty, value in percent).
        """
        return self.__fairplayViolations.getPenaltyDetails()


class _AutoCompletionRecords(records.RawRecords):
    __slots__ = ()

    def __init__(self, results):
        records = {}
        if 'autoRepairCost' in results:
            cost = results['autoRepairCost']
            if cost is not None:
                records['autoRepairCost'] = -cost
        if 'autoLoadCost' in results:
            cost = results['autoLoadCost']
            if cost is not None:
                records['autoLoadCredits'] = -cost[0]
                records['autoLoadGold'] = -cost[1]
        if 'autoEquipCost' in results:
            cost = results['autoEquipCost']
            if cost is not None:
                records['autoEquipCredits'] = -cost[0]
                records['autoEquipGold'] = -cost[1]
        super(_AutoCompletionRecords, self).__init__(records)
        return


class _CreditsReplayRecords(records.ReplayRecords):
    """Class contains values of credits from replay."""
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
    """Class contains values of XPs from replay."""
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
    """Class contains values of free XPs from replay."""
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
    __slots__ = ('_baseCredits', '_premiumCredits', '_goldRecords', '_autoRecords', '_baseXP', '_premiumXP', '_baseFreeXP', '_premiumFreeXP', '_fortResource', '_crystal')

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

    def getBaseCreditsRecords(self):
        return self._baseCredits

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

    def getXPRecords(self):
        return itertools.izip(self._baseXP, self._premiumXP, self._baseFreeXP, self._premiumFreeXP)

    def getXPDiff(self):
        return self._premiumXP.getRecord('xp') - self._baseXP.getRecord('xp')

    def addResults(self, _, results):
        connector = ValueReplayConnector(VEH_FULL_RESULTS, results)
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
            isHighScope = RECORD_DB_IDS[('max15x15', 'maxXP')] in map(lambda (recordID, value): recordID, results.get('dossierPopUps', []))
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
        if Currency.CRYSTAL in results and results[Currency.CRYSTAL] is not None:
            replay = ValueReplay(connector, recordName=Currency.CRYSTAL, replay=results['crystalReplay'])
            self._crystal.addRecords(records.ReplayRecords(replay, Currency.CRYSTAL))
        else:
            LOG_ERROR('crystal replay is not found', results)
        return


class PersonalInfo(shared.UnpackedInfo):
    """Class contains reusable personal information about player.
    This information is fetched from battle_results['personal']"""
    __slots__ = ('__avatar', '__vehicles', '__lifeTimeInfo', '__isObserver', '__economicsRecords', '__isPremium', '__questsProgress', '__rankInfo')
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
        self.__rankInfo = PostBattleRankInfo(0, 0, 0, 0, 0)
        if not self.hasUnpackedItems():
            self.__collectRequiredData(personal)
        return

    @property
    def avatar(self):
        """Gets extended information about avatar.
        :return: instance of _PersonalAvatarInfo.
        """
        return self.__avatar

    @property
    def isObserver(self):
        """Was player observer in the battle."""
        return self.__isObserver

    @property
    def isPremium(self):
        """Were premium factors applied in the battle results"""
        return self.__isPremium

    def getVehicleCDsIterator(self, result):
        """Gets generator to iterate information about personal vehicles from the battle results.
        :param result: dict containing results['personal'].
        :return: generator containing all personal vehicles that are fetched from specified result.
        """
        for intCD in self.__vehicles:
            if intCD not in result:
                continue
            yield (intCD, result[intCD])

    def getVehicleItemsIterator(self):
        """Gets generator to iterate GUI wrappers of vehicles that player used in the battle.
        :return: generator containing all GUI wrappers of vehicles.
        """
        getItemByCD = self.itemsCache.items.getItemByCD
        for intCD in self.__vehicles:
            yield (intCD, getItemByCD(intCD))

    def getAchievements(self, result):
        """Gets sequence of personal achievements that was received in the battle.
        :param result: dict containing results['personal'].
        :return: tuple(achievements that are shown on the left side in the UI,
            achievements that are shown on the right side in the UI).
        """
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
        """Gets personal information: was player killed,
        how long player's vehicle spent in the battle alive."""
        return self.__lifeTimeInfo

    def getQuestsProgress(self):
        """Gets union information about quests from avatar and personal vehicles
        :return: dictionary containing information about quests.
        """
        return self.__questsProgress

    def getRankInfo(self):
        """Gets union information about rank changing from personal['avatar']
        """
        return self.__rankInfo

    def getBaseCreditsRecords(self):
        """Gets credits records without premium factor."""
        return self.__economicsRecords.getBaseCreditsRecords()

    def getPremiumCreditsRecords(self):
        """Gets credits records with premium factor."""
        return self.__economicsRecords.getPremiumCreditsRecords()

    def getCreditsDiff(self):
        """Gets difference between record "credits" with premium factor and
        record "credits" without premium factor."""
        return self.__economicsRecords.getCreditsDiff()

    def getMoneyRecords(self):
        """Gets money (credits and gold) records without/with premium factor."""
        return self.__economicsRecords.getMoneyRecords()

    def getCrystalRecords(self):
        """Gets crystal records without premium factor."""
        return self.__economicsRecords.getCrystalRecords()

    def getBaseXPRecords(self):
        """Gets XPs records without premium factor."""
        return self.__economicsRecords.getBaseXPRecords()

    def getPremiumXPRecords(self):
        """Gets XPs records with premium factor."""
        return self.__economicsRecords.getPremiumXPRecords()

    def getXPRecords(self):
        """Gets XPs (vehicle's XP and free XP) records without/with premium factor."""
        return self.__economicsRecords.getXPRecords()

    def getXPDiff(self):
        """Gets difference between record "xp" with premium factor and
        record "xp" without premium factor."""
        return self.__economicsRecords.getXPDiff()

    def __collectRequiredData(self, info):
        getItemByCD = self.itemsCache.items.getItemByCD
        items = sorted(map(getItemByCD, filter(lambda key: isinstance(key, (int, long, float)), info.keys())))
        lifeTimes = []
        team = self.__avatar.team
        infoAvatar = info['avatar']
        if infoAvatar:
            self.__questsProgress.update(infoAvatar.get('questsProgress', {}))
            self.__rankInfo = PostBattleRankInfo.fromDict(infoAvatar)
        for item in items:
            intCD = item.intCD
            assert intCD in info
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

        if lifeTimes:
            self.__lifeTimeInfo = _LifeTimeInfo(True, min(lifeTimes))
        return

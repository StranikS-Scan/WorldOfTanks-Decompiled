# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/personal.py
import itertools
from collections import namedtuple
from ValueReplay import ValueReplay, ValueReplayConnector
from battle_results_shared import VEH_FULL_RESULTS
from constants import PREMIUM_TYPE
from debug_utils import LOG_ERROR
from dossiers2.custom.records import RECORD_DB_IDS
from gui.battle_results.reusable import records
from gui.battle_results.reusable import shared
from gui.battle_results.reusable import sort_keys
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.battle_results.settings import FACTOR_VALUE
from gui.ranked_battles.ranked_models import PostBattleRankInfo
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
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


class _AdditionalRecords(records.RawRecords):
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
        if 'piggyBank' in results:
            cost = results['piggyBank']
            if cost is not None:
                rawRecords['piggyBank'] = cost
        super(_AdditionalRecords, self).__init__(rawRecords)
        return


class _CreditsReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, results, squadCreditsFactor=0):
        super(_CreditsReplayRecords, self).__init__(replay, 'credits')
        self._addRecord(ValueReplay.SUB, 'originalCreditsToDraw', results['originalCreditsToDraw'], 0)
        self._addRecord(ValueReplay.SET, 'achievementCredits', results['achievementCredits'], 0)
        self._addRecord(ValueReplay.FACTOR, 'premSquadCreditsFactor100', squadCreditsFactor, 0)
        self._addRecord(ValueReplay.SUBCOEFF, 'originalCreditsToDrawSquad', results['originalCreditsToDrawSquad'], results['originalCreditsToDrawSquad'] * self.getFactor('premSquadCreditsFactor100') * -1)

    def _getRecord(self, name):
        value = super(_CreditsReplayRecords, self)._getRecord(name)
        if name in ('originalCreditsToDraw', 'achievementCredits'):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumCreditsFactor100'))
        return value


class _XPReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, isHighScope, achievementXP):
        super(_XPReplayRecords, self).__init__(replay, 'xp')
        if isHighScope:
            self._addRecord(ValueReplay.SET, 'isHighScope', 1, 0)
        self._addRecord(ValueReplay.SET, 'achievementXP', achievementXP, 0)
        self._addRecord(ValueReplay.SET, 'xpToShow', max(0, self.getRecord('xp')), 0)

    def _getRecord(self, name):
        value = super(_XPReplayRecords, self)._getRecord(name)
        if name in ('achievementXP',):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumXPFactor100'))
        return value


class _FreeXPReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, achievementFreeXP):
        super(_FreeXPReplayRecords, self).__init__(replay, 'freeXP')
        self._addRecord(ValueReplay.SET, 'achievementFreeXP', achievementFreeXP, 0)

    def _getRecord(self, name):
        value = super(_FreeXPReplayRecords, self)._getRecord(name)
        if name in ('achievementFreeXP',):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumXPFactor100'))
        return value


class _EconomicsRecordsChains(object):
    __slots__ = ('_baseCredits', '_premiumCredits', '_premiumPlusCredits', '_goldRecords', '_additionalRecords', '_baseXP', '_premiumXP', '_premiumPlusXP', '_baseXPAdd', '_premiumXPAdd', '_premiumPlusXPAdd', '_baseFreeXP', '_premiumFreeXP', '_premiumPlusFreeXP', '_baseFreeXPAdd', '_premiumFreeXPAdd', '_premiumPlusFreeXPAdd', '_crystal', '_crystalDetails')

    def __init__(self):
        super(_EconomicsRecordsChains, self).__init__()
        self._baseCredits = records.RecordsIterator()
        self._premiumCredits = records.RecordsIterator()
        self._premiumPlusCredits = records.RecordsIterator()
        self._goldRecords = records.RecordsIterator()
        self._additionalRecords = records.RecordsIterator()
        self._baseXP = records.RecordsIterator()
        self._premiumXP = records.RecordsIterator()
        self._premiumPlusXP = records.RecordsIterator()
        self._baseXPAdd = records.RecordsIterator()
        self._premiumXPAdd = records.RecordsIterator()
        self._premiumPlusXPAdd = records.RecordsIterator()
        self._baseFreeXP = records.RecordsIterator()
        self._premiumFreeXP = records.RecordsIterator()
        self._premiumPlusFreeXP = records.RecordsIterator()
        self._baseFreeXPAdd = records.RecordsIterator()
        self._premiumFreeXPAdd = records.RecordsIterator()
        self._premiumPlusFreeXPAdd = records.RecordsIterator()
        self._crystal = records.RecordsIterator()
        self._crystalDetails = []

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

    def getPremiumXPAddRecords(self):
        return self._premiumXPAdd

    def getMoneyRecords(self, premiumType=PREMIUM_TYPE.NONE):
        if premiumType == PREMIUM_TYPE.NONE or premiumType & (PREMIUM_TYPE.VIP | PREMIUM_TYPE.PLUS):
            resultPremiumData = self._premiumPlusCredits
        else:
            resultPremiumData = self._premiumCredits
        return itertools.izip(self._baseCredits, resultPremiumData, self._goldRecords, self._additionalRecords)

    def getCrystalRecords(self):
        return itertools.izip(self._crystal, self._crystal)

    def getCrystalDetails(self):
        return self._crystalDetails

    def getXPRecords(self, premiumType=PREMIUM_TYPE.NONE, addBonusApplied=False):
        if premiumType == PREMIUM_TYPE.NONE or premiumType & (PREMIUM_TYPE.VIP | PREMIUM_TYPE.PLUS):
            if addBonusApplied:
                secondXPData = self._premiumPlusXPAdd
                secondFreeXPData = self._premiumPlusFreeXPAdd
            else:
                secondXPData = self._premiumPlusXP
                secondFreeXPData = self._premiumPlusFreeXP
        elif addBonusApplied:
            secondXPData = self._premiumXPAdd
            secondFreeXPData = self._premiumFreeXPAdd
        else:
            secondXPData = self._premiumXP
            secondFreeXPData = self._premiumFreeXP
        if addBonusApplied:
            firstXPData = self._baseXPAdd
            firstFreeXPData = self._baseFreeXPAdd
        else:
            firstXPData = self._baseXP
            firstFreeXPData = self._baseFreeXP
        return itertools.izip(firstXPData, secondXPData, firstFreeXPData, secondFreeXPData)

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
            appliedPremiumCreditsFactor100Exists = 'appliedPremiumCreditsFactor100' in replay
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = FACTOR_VALUE.BASE_CREDITS_FACTOR
            self._baseCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.NONE, results, replay))
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = results['premiumCreditsFactor100']
            self._premiumCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.BASIC, results, replay))
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = results['premiumPlusCreditsFactor100']
            self._premiumPlusCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.PLUS, results, replay))
        else:
            LOG_ERROR('Credits replay is not found', results)
        if 'goldReplay' in results and results['goldReplay'] is not None:
            replay = ValueReplay(connector, recordName='gold', replay=results['goldReplay'])
            self._goldRecords.addRecords(records.ReplayRecords(replay, 'gold'))
        else:
            LOG_ERROR('Gold replay is not found', results)
        self._additionalRecords.addRecords(_AdditionalRecords(results))
        return

    def _addXPResults(self, connector, results):
        if 'xpReplay' in results and results['xpReplay'] is not None:
            replay = ValueReplay(connector, recordName='xp', replay=results['xpReplay'])
            self.__updateAdditionalFactorFromReplay(replay, results, setDefault=True)
            isHighScope = RECORD_DB_IDS[('max15x15', 'maxXP')] in [ recordID for recordID, _ in results.get('dossierPopUps', []) ]
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updateAdditionalFactorFromReplay(replay, results, setDefault=False)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
        else:
            LOG_ERROR('XP replay is not found', results)
        if 'freeXPReplay' in results and results['freeXPReplay'] is not None:
            replay = ValueReplay(connector, recordName='freeXP', replay=results['freeXPReplay'])
            self.__updateAdditionalFactorFromReplay(replay, results, setDefault=True)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updateAdditionalFactorFromReplay(replay, results, setDefault=False)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
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

    def __buildCreditsReplayForPremType(self, targetPremiumType, results, replay):
        initialSquadFactor = results['premSquadCreditsFactor100']
        squadCreditsFactor = self.__getPremiumSquadCreditsFactor(results, targetPremiumType)
        results['premSquadCreditsFactor100'] = squadCreditsFactor
        creditsReplayToUse = _CreditsReplayRecords(replay, results, squadCreditsFactor)
        results['premSquadCreditsFactor100'] = initialSquadFactor
        return creditsReplayToUse

    @staticmethod
    def __updateAdditionalFactorFromReplay(replay, results, setDefault=False):
        if 'additionalXPFactor10' not in replay:
            return
        if setDefault:
            if 'dailyXPFactor10' in replay:
                replay['additionalXPFactor10'] = FACTOR_VALUE.ADDITIONAL_BONUS_ZERO_FACTOR
            else:
                replay['additionalXPFactor10'] = FACTOR_VALUE.ADDITIONAL_BONUS_ONE_FACTOR
        else:
            replay['additionalXPFactor10'] = results['additionalXPFactor10']

    @staticmethod
    def __updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE):
        if 'appliedPremiumXPFactor100' not in replay:
            return
        if premType == PREMIUM_TYPE.PLUS:
            replay['appliedPremiumXPFactor100'] = results['premiumPlusXPFactor100']
        elif premType == PREMIUM_TYPE.BASIC:
            replay['appliedPremiumXPFactor100'] = results['premiumXPFactor100']
        else:
            replay['appliedPremiumXPFactor100'] = FACTOR_VALUE.BASE_XP_FACTOR

    @staticmethod
    @dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
    def __getPremiumSquadCreditsFactor(results, targetPremiumType, lobbyContext=None):
        premiumType = PREMIUM_TYPE.activePremium(results.get('premMask', PREMIUM_TYPE.NONE))
        if targetPremiumType > premiumType:
            return lobbyContext.getServerSettings().squadPremiumBonus.ownCredits * 100
        return 0 if targetPremiumType < premiumType else results.get('premSquadCreditsFactor100', 0)


class PersonalInfo(shared.UnpackedInfo):
    __slots__ = ('__avatar', '__vehicles', '__lifeTimeInfo', '__isObserver', '_economicsRecords', '__questsProgress', '__PM2Progress', '__rankInfo', '__isTeamKiller', '__progressiveReward', '__premiumMask', '__isAddXPBonusApplied')
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
        self.__isTeamKiller = False
        self.__premiumMask = 0
        self.__isAddXPBonusApplied = False
        self._economicsRecords = _EconomicsRecordsChains()
        self.__lifeTimeInfo = _LifeTimeInfo(False, 0)
        self.__questsProgress = {}
        self.__PM2Progress = {}
        self.__rankInfo = PostBattleRankInfo(0, 0, 0, 0, 0, 0, {}, {}, False, 0)
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
    def hasAnyPremium(self):
        return bool(self.__premiumMask & PREMIUM_TYPE.ANY)

    @property
    def isPremium(self):
        return bool(PREMIUM_TYPE.activePremium(self.__premiumMask) & PREMIUM_TYPE.BASIC)

    @property
    def isPremiumPlus(self):
        return bool(PREMIUM_TYPE.activePremium(self.__premiumMask) & PREMIUM_TYPE.PLUS)

    @property
    def isPremiumVIP(self):
        return bool(PREMIUM_TYPE.activePremium(self.__premiumMask) & PREMIUM_TYPE.VIP)

    @property
    def isAddXPBonusApplied(self):
        return self.__isAddXPBonusApplied

    @isAddXPBonusApplied.setter
    def isAddXPBonusApplied(self, state):
        self.__isAddXPBonusApplied = state

    @property
    def isTeamKiller(self):
        return self.__isTeamKiller

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

    def getProgressiveReward(self):
        return self.__progressiveReward

    def getBaseCreditsRecords(self):
        return self._economicsRecords.getBaseCreditsRecords()

    def getPremiumCreditsRecords(self):
        return self._economicsRecords.getPremiumCreditsRecords()

    def getCreditsDiff(self):
        return self._economicsRecords.getCreditsDiff()

    def getMoneyRecords(self):
        return self._economicsRecords.getMoneyRecords(self.__premiumMask)

    def getCrystalRecords(self):
        return self._economicsRecords.getCrystalRecords()

    def getBaseXPRecords(self):
        return self._economicsRecords.getBaseXPRecords()

    def getPremiumXPRecords(self):
        return self._economicsRecords.getPremiumXPRecords()

    def getPremiumXPAddRecords(self):
        return self._economicsRecords.getPremiumXPAddRecords()

    def getXPRecords(self):
        return self._economicsRecords.getXPRecords(self.__premiumMask, self.__isAddXPBonusApplied)

    def getXPDiff(self):
        return self._economicsRecords.getXPDiff()

    def getCrystalDetails(self):
        return self._economicsRecords.getCrystalDetails()

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
            self.__progressiveReward = infoAvatar.get('progressiveReward')
        for item in items:
            intCD = item.intCD
            data = info[intCD]
            if data is None:
                self._addUnpackedItemID(intCD)
                continue
            self.__vehicles.append(intCD)
            self._economicsRecords.addResults(intCD, data)
            if not self.__isObserver:
                self.__isObserver = item.isObserver
            killerID = data['killerID'] if 'killerID' in data else 0
            lifeTime = data['lifeTime'] if 'lifeTime' in data else 0
            if killerID and lifeTime:
                lifeTimes.append(lifeTime)
            self.__isTeamKiller = data['isTeamKiller'] if 'isTeamKiller' in data else False
            self.__premiumMask = data.get('premMask', PREMIUM_TYPE.NONE)
            self.__questsProgress.update(data.get('questsProgress', {}))
            self.__PM2Progress.update(data.get('PM2Progress', {}))

        if lifeTimes:
            self.__lifeTimeInfo = _LifeTimeInfo(True, min(lifeTimes))
        return

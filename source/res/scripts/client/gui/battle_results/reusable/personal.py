# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/personal.py
from collections import namedtuple
import typing
from constants import PREMIUM_TYPE
from gui.battle_results.reusable import records, ReusableInfoFactory
from gui.battle_results.reusable import shared
from gui.battle_results.reusable import sort_keys
from gui.battle_results.reusable.economics_records import EconomicsRecordsChains
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.ranked_battles.ranked_models import PostBattleRankInfo
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable.vehicles import VehiclesInfo
    from gui.shared.utils.requesters.StatsRequester import _ControllableXPData
_LifeTimeInfo = namedtuple('_LifeTimeInfo', ('isKilled', 'lifeTime'))

class SquadBonusInfo(object):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__vehicles', '__joinedOnArena', '__size')

    def __init__(self, vehicles=None, joinedOnArena=None, size=0, **kwargs):
        super(SquadBonusInfo, self).__init__()
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


class PersonalAvatarInfo(object):
    __slots__ = ('__accountDBID', '__clanDBID', '__team', '__isPrematureLeave', '__fairplayViolations', '__squadBonusInfo', '__winnerIfDraw', '__eligibleForCrystalRewards', '__extInfo')

    def __init__(self, bonusType, accountDBID=0, clanDBID=0, team=0, isPrematureLeave=False, fairplayViolations=None, squadBonusInfo=None, winnerIfDraw=0, eligibleForCrystalRewards=False, **kwargs):
        super(PersonalAvatarInfo, self).__init__()
        self.__accountDBID = accountDBID
        self.__clanDBID = clanDBID
        self.__team = team
        self.__isPrematureLeave = isPrematureLeave
        self.__eligibleForCrystalRewards = eligibleForCrystalRewards
        fairplayViolationsCls = ReusableInfoFactory.fairplayViolationForBonusType(bonusType)
        self.__fairplayViolations = fairplayViolationsCls(*(fairplayViolations or ()))
        squadBonusInfoCls = ReusableInfoFactory.squadBonusInfoForBonusType(bonusType)
        self.__squadBonusInfo = squadBonusInfoCls(**(squadBonusInfo or {}))
        self.__winnerIfDraw = winnerIfDraw
        self.__extInfo = kwargs

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


class PersonalInfo(shared.UnpackedInfo):
    __slots__ = ('__avatar', '__vehicles', '__lifeTimeInfo', '__isObserver', '_economicsRecords', '__questsProgress', '__PM2Progress', '__rankInfo', '__isTeamKiller', '__progressiveReward', '__premiumMask', '__isWotPlus', '__isAddXPBonusApplied', '__c11nProgress', '__dogTags', '__goldBankGain', '__xpProgress', '__prestigeResults', '__questTokensCount')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, bonusType, personal, bonusCapsOverrides=None):
        super(PersonalInfo, self).__init__()
        if _RECORD.PERSONAL_AVATAR in personal and personal[_RECORD.PERSONAL_AVATAR] is not None:
            self.__avatar = PersonalAvatarInfo(bonusType, **personal[_RECORD.PERSONAL_AVATAR])
        else:
            self.__avatar = PersonalAvatarInfo(bonusType)
            self._addUnpackedItemID(_RECORD.PERSONAL_AVATAR)
        self.__vehicles = []
        self.__isObserver = False
        self.__isTeamKiller = False
        self.__premiumMask = 0
        self.__isWotPlus = False
        self.__isAddXPBonusApplied = False
        self._economicsRecords = EconomicsRecordsChains(bonusType, bonusCapsOverrides)
        self.__lifeTimeInfo = _LifeTimeInfo(False, 0)
        self.__questsProgress = {}
        self.__PM2Progress = {}
        self.__c11nProgress = {}
        self.__xpProgress = {}
        self.__rankInfo = PostBattleRankInfo(0, 0, 0, 0, 0, 0, 0, 0, {}, {}, False, 0, 0)
        self.__dogTags = {}
        self.__prestigeResults = {}
        self.__questTokensCount = {}
        self.__goldBankGain = 0
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
    def isWotPlus(self):
        return self.__isWotPlus

    @property
    def isAddXPBonusApplied(self):
        return self.__isAddXPBonusApplied

    @isAddXPBonusApplied.setter
    def isAddXPBonusApplied(self, state):
        self.__isAddXPBonusApplied = state

    @property
    def isTeamKiller(self):
        return self.__isTeamKiller

    @property
    def xpProgress(self):
        return self.__xpProgress

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
            for direction, achievement, achievementID in achievements:
                if direction == 1:
                    right.append((achievement, True, achievementID))
                left.append((achievement, True, achievementID))

            achievement = shared.makeMarkOfMasteryFromPersonal(data)
            if achievement is not None:
                left.append((achievement, False, 0))

        return (left, sorted(right, key=sort_keys.AchievementSortKey))

    def getLifeTimeInfo(self):
        return self.__lifeTimeInfo

    def getQuestsProgress(self):
        return self.__questsProgress

    def getDogTagsProgress(self):
        return self.__dogTags

    def getGoldBankGain(self):
        return self.__goldBankGain

    def getPM2Progress(self):
        return self.__PM2Progress

    def getC11nProgress(self):
        return self.__c11nProgress

    def getQuestTokensCount(self):
        return self.__questTokensCount

    def getRankInfo(self):
        return self.__rankInfo

    def getProgressiveReward(self):
        return self.__progressiveReward

    def getPrestigeResults(self):
        return self.__prestigeResults

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

    def getUnpackedCrystalRecords(self):
        return self._economicsRecords.getUnpackedCrystalRecords()

    def haveCrystalsChanged(self):
        return self._economicsRecords.haveCrystalsChanged()

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

    def getTmenXPRecords(self):
        return self._economicsRecords.getTmenXPRecords(self.__premiumMask, self.__isAddXPBonusApplied)

    def getXPToShow(self, isDiffShow=False):
        return self._economicsRecords.getXPToShow(isDiffShow)

    def getCreditsToShow(self, isDiffShow=False):
        return self._economicsRecords.getCreditsToShow(isDiffShow)

    def getCrystalDetailsRecords(self):
        return self._economicsRecords.getCrystalDetails()

    def updateXPEarnings(self, extraXPData):
        vehProgress = self.__xpProgress[extraXPData.vehicleID]
        vehProgress['xp'] += extraXPData.extraXP
        newTankmenXp = []
        for (oldID, oldValue), (newID, newValue) in zip(vehProgress['xpByTmen'], extraXPData.extraTmenXP):
            newTankmenXp.append((newID, oldValue + newValue))

        vehProgress['xpByTmen'] = newTankmenXp

    def __collectRequiredData(self, info):
        getItemByCD = self.itemsCache.items.getItemByCD
        itemCDs = [ key for key in info.keys() if isinstance(key, (int, long, float)) ]
        items = sorted((getItemByCD(itemCD) for itemCD in itemCDs))
        lifeTimes = []
        infoAvatar = info['avatar']
        if infoAvatar:
            self.__questsProgress.update(infoAvatar.get('questsProgress', {}))
            self.__PM2Progress.update(infoAvatar.get('PM2Progress', {}))
            self.__questTokensCount.update(infoAvatar.get('questTokensCount', {}))
            self.__rankInfo = PostBattleRankInfo.fromDict(infoAvatar)
            self.__progressiveReward = infoAvatar.get('progressiveReward')
            self.__dogTags.update(infoAvatar.get('dogTags', {}))
            self.__goldBankGain = infoAvatar.get('goldBankGain', 0)
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
            self.__isWotPlus = data.get('isWoTPlus', False)
            self.__questsProgress.update(data.get('questsProgress', {}))
            self.__PM2Progress.update(data.get('PM2Progress', {}))
            self.__c11nProgress[intCD] = data.get('c11nProgress', {})
            self.__xpProgress[intCD] = {'xp': data.get('xp', 0),
             'xpByTmen': data.get('xpByTmen', [])}
            self.__prestigeResults[intCD] = data.get('prestigeResults', {})

        if lifeTimes:
            self.__lifeTimeInfo = _LifeTimeInfo(True, min(lifeTimes))
        return

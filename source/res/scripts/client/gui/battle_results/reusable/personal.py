# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/personal.py
from collections import namedtuple
import typing
from gui.battle_results.reusable import shared
from gui.battle_results.reusable import sort_keys
from gui.battle_results.br_constants import BattleResultsRecord as _RECORD
from gui.battle_results.br_constants import UNKNOWN_ACHIEVEMENT_ID
from gui.ranked_battles.ranked_models import PostBattleRankInfo
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable.vehicles import VehiclesInfo
    from gui.shared.utils.requesters.StatsRequester import _ControllableXPData
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
    __slots__ = ('__avatar', '__vehicles', '__lifeTimeInfo', '__isObserver', '__rankInfo', '__isTeamKiller', '__c11nProgress', '__dogTags', '__goldBankGain', '__xpProgress', '__replayURL')
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
        self.__lifeTimeInfo = _LifeTimeInfo(False, 0)
        self.__c11nProgress = {}
        self.__xpProgress = {}
        self.__rankInfo = PostBattleRankInfo(0, 0, 0, 0, 0, 0, 0, 0, {}, {}, False, 0, 0)
        self.__dogTags = {}
        self.__goldBankGain = 0
        self.__replayURL = ''
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
            achievements = shared.makeAchievementsFromPersonal(data)
            for direction, achievement, achievementID in achievements:
                if direction == 1:
                    right.append(shared.AchievementSimpleData(achievementID=achievementID, achievement=achievement, isUnique=True, isPersonal=True))
                left.append(shared.AchievementSimpleData(achievementID, achievement, True, True))

            left.sort(key=sort_keys.leftAchievementSort)
            achievement = shared.makeMarkOfMasteryFromPersonal(data)
            if achievement is not None:
                left.append(shared.AchievementSimpleData(achievementID=UNKNOWN_ACHIEVEMENT_ID, achievement=achievement, isUnique=False, isPersonal=True))

        return (left, sorted(right, key=sort_keys.AchievementSortKey))

    def getLifeTimeInfo(self):
        return self.__lifeTimeInfo

    def getDogTagsProgress(self):
        return self.__dogTags

    def getGoldBankGain(self):
        return self.__goldBankGain

    def getReplayURL(self):
        return self.__replayURL

    def getPM2Progress(self):
        return self.__PM2Progress

    def getC11nProgress(self):
        return self.__c11nProgress

    def getRankInfo(self):
        return self.__rankInfo

    def getProgressiveReward(self):
        return self.__progressiveReward

    def updateXPEarnings(self, extraXPData):
        vehProgress = self.__xpProgress[extraXPData.vehicleID]
        vehProgress['xp'] += extraXPData.extraXP
        newTankmenXp = []
        for (oldID, oldValue), (newID, newValue) in zip(vehProgress['xpByTmen'], extraXPData.extraTmenXP):
            newTankmenXp.append((newID, oldValue + newValue))

        vehProgress['xpByTmen'] = newTankmenXp

    def __collectRequiredData(self, info):
        getItemByCD = self.itemsCache.items.getItemByCD
        itemCDs = [ key for key in info.keys() if isinstance(key, int) ]
        items = sorted((getItemByCD(itemCD) for itemCD in itemCDs))
        lifeTimes = []
        infoAvatar = info['avatar']
        if infoAvatar:
            self.__rankInfo = PostBattleRankInfo.fromDict(infoAvatar)
            self.__dogTags.update(infoAvatar.get('dogTags', {}))
            self.__goldBankGain = infoAvatar.get('goldBankGain', 0)
            self.__replayURL = infoAvatar.get('replayURL', '')
        for item in items:
            intCD = item.intCD
            data = info[intCD]
            if data is None:
                self._addUnpackedItemID(intCD)
                continue
            self.__vehicles.append(intCD)
            if not self.__isObserver:
                self.__isObserver = item.isObserver
            killerID = data['killerID'] if 'killerID' in data else 0
            lifeTime = data['lifeTime'] if 'lifeTime' in data else 0
            if killerID and lifeTime:
                lifeTimes.append(lifeTime)
            self.__isTeamKiller = data['isTeamKiller'] if 'isTeamKiller' in data else False
            self.__c11nProgress[intCD] = data.get('c11nProgress', {})
            self.__xpProgress[intCD] = {'xp': data.get('xp', 0),
             'xpByTmen': data.get('xpByTmen', [])}

        if lifeTimes:
            self.__lifeTimeInfo = _LifeTimeInfo(True, min(lifeTimes))
        return

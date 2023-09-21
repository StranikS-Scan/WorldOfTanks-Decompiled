# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/progress.py
import logging
from collections import namedtuple
import math
import operator
import typing
import personal_missions
from gui.battle_results.reusable import shared
from gui.server_events.event_items import PersonalMission
from gui.server_events.events_constants import BATTLE_MATTERS_QUEST_ID
from gui.server_events.events_helpers import isC11nQuest, getDataByC11nQuest
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import getEventPostBattleInfo, get2dProgressionStylePostBattleInfo
from gui.shared.gui_items import GUI_ITEM_TYPE, getVehicleComponentsByType
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
ProgressiveRewardData = namedtuple('ProgressiveRewardData', ('currentStep', 'probability', 'maxSteps', 'hasCompleted'))
ItemWithProgress = namedtuple('ItemWithProgress', ('item', 'unlockProps', 'price'))
TankmanWithProgress = namedtuple('TankmanWithProgress', ('tankman', 'isCompleted'))
_PMComplete = namedtuple('_PMComplete', ('isMainComplete', 'isAddComplete'))

class VehicleProgressHelper(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehTypeCompDescr):
        self.__unlocks = self.__itemsCache.items.stats.unlocks
        self.__vehTypeCompDescr = vehTypeCompDescr
        self.__vehicle = self.__itemsCache.items.getItemByCD(vehTypeCompDescr)
        self.__vehicleXp = self.__itemsCache.items.stats.vehiclesXPs.get(self.__vehTypeCompDescr, 0)
        self.__avgVehicleXp = self.__getAvgVehicleXp(self.__vehTypeCompDescr)

    def clear(self):
        self.__unlocks = None
        self.__vehicle = None
        self.__vehicleXp = None
        self.__avgVehicleXp = None
        self.__vehTypeCompDescr = None
        return

    def getReady2UnlockItems(self, vehicleBattleXp):
        ready2UnlockModules = []
        ready2UnlockVehicles = []
        possible2UnlockItems = g_techTreeDP.getAllPossibleItems2Unlock(self.__vehicle, self.__unlocks)
        getter = self.__itemsCache.items.getItemByCD
        for itemTypeCD, unlockProps in possible2UnlockItems.iteritems():
            item = getter(itemTypeCD)
            if self.__vehicleXp - unlockProps.xpCost <= vehicleBattleXp:
                if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                    if self.__vehicleXp > unlockProps.xpCost:
                        ready2UnlockVehicles.append(ItemWithProgress(item, unlockProps, price=None))
                elif self.__vehicleXp > unlockProps.xpCost:
                    ready2UnlockModules.append(ItemWithProgress(item, unlockProps, price=None))

        return (ready2UnlockVehicles, ready2UnlockModules)

    def getReady2BuyItems(self, pureCreditsReceived):
        ready2BuyModules = []
        ready2BuyVehicles = []
        creditsValue = self.__itemsCache.items.stats.credits
        unlockedVehicleItems = g_techTreeDP.getUnlockedVehicleItems(self.__vehicle, self.__unlocks)
        getter = self.__itemsCache.items.getItemByCD
        for itemTypeCD, unlockProps in unlockedVehicleItems.iteritems():
            item = getter(itemTypeCD)
            price = item.getBuyPrice(preferred=False).price
            if price.isCurrencyDefined(Currency.CREDITS) and not item.isInInventory:
                priceCredits = price.credits
                if creditsValue - priceCredits <= pureCreditsReceived and creditsValue > priceCredits:
                    if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                        ready2BuyVehicles.append(ItemWithProgress(item, unlockProps, price))
                    elif not item.isInstalled(self.__vehicle):
                        items = getVehicleComponentsByType(self.__vehicle, item.itemTypeID).values()
                        if items:
                            installedModule = max(items, key=lambda module: module.level)
                            if item.level > installedModule.level:
                                ready2BuyModules.append(ItemWithProgress(item, unlockProps, price))

        return (ready2BuyVehicles, ready2BuyModules)

    def getNewSkilledTankmen(self, tankmenXps):
        skilledTankmans = []
        for _, tman in self.__vehicle.crew:
            if tman is not None and tman.hasSkillToLearn():
                if not tman.isMaxRoleLevel:
                    continue
                tmanBattleXp = tankmenXps.get(tman.invID, 0)
                if tman.hasNewSkill(useCombinedRoles=True):
                    if tmanBattleXp - tman.descriptor.freeXP > 0:
                        skilledTankmans.append(TankmanWithProgress(tman, True))
                else:
                    skilledTankmans.append(TankmanWithProgress(tman, False))

        return skilledTankmans

    def isEnoughXPToUnlock(self, unlockProps):
        return self.__vehicleXp > unlockProps.xpCost

    def getAvgBattles2Unlock(self, unlockProps):
        return int(math.ceil((unlockProps.xpCost - self.__vehicleXp) / float(self.__avgVehicleXp))) if self.__avgVehicleXp > 0 else 0

    def getAvgBattles2NewSkill(self, tman):
        avgTmanXp = self.__itemsCache.items.getTankmanDossier(tman.invID).getAvgXP()
        return max(1, math.ceil(tman.getNextSkillXpCost() / avgTmanXp)) if avgTmanXp > 0 else 0

    def __getAvgVehicleXp(self, vehTypeCompDescr):
        vehiclesStats = self.__itemsCache.items.getAccountDossier().getRandomStats().getVehicles()
        vehicleStats = vehiclesStats.get(vehTypeCompDescr, None)
        if vehicleStats is not None:
            battlesCount, _, xp = vehicleStats
            if battlesCount:
                return xp / battlesCount
            return 0
        else:
            return 0


class ProgressInfo(shared.UnpackedInfo):
    __slots__ = ('__questsProgress', '__PM2Progress', '__progressiveReward')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, personal):
        super(ProgressInfo, self).__init__()
        self.__questsProgress = {}
        self.__PM2Progress = {}
        self.__progressiveReward = ()
        if not self.hasUnpackedItems():
            self.__collectRequiredData(personal)

    def getQuestsProgress(self):
        return self.__questsProgress

    def getPM2Progress(self):
        return self.__PM2Progress

    def getProgressiveReward(self):
        return self.__progressiveReward

    def processProgressiveRewardData(self):
        if self.__progressiveReward is None:
            return
        else:
            config = self.__lobbyContext.getServerSettings().getProgressiveRewardConfig()
            maxSteps = config.maxLevel
            hasCompleted, currentStep, probability = self.__progressiveReward
            if currentStep >= maxSteps:
                _logger.warning('Current step more than max step in progressive reward')
                return
            if hasCompleted:
                currentStep = currentStep - 1 if currentStep else maxSteps - 1
            return ProgressiveRewardData(currentStep=currentStep, probability=probability, maxSteps=maxSteps, hasCompleted=hasCompleted)

    def getPlayerQuestProgress(self):
        commonQuests = []
        allCommonQuests = self.__eventsCache.getQuests()
        allCommonQuests.update(self.__eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
        if self.__questsProgress:
            for qID, qProgress in self.__questsProgress.iteritems():
                pGroupBy, pPrev, pCur = qProgress
                isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
                if qID in allCommonQuests:
                    quest = allCommonQuests[qID]
                    isProgressReset = not isCompleted and quest.bonusCond.isInRow() and pCur.get('battlesCount', 0) == 0
                    if pPrev or max(pCur.itervalues()) != 0:
                        commonQuests.append((quest,
                         {pGroupBy: pCur},
                         {pGroupBy: pPrev},
                         isProgressReset,
                         isCompleted))

        return commonQuests

    def getC11nProgress(self):
        c11nQuests = []
        allCommonQuests = self.__eventsCache.getQuests()
        allCommonQuests.update(self.__eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
        if self.__questsProgress:
            for qID, qProgress in self.__questsProgress.iteritems():
                pGroupBy, pPrev, pCur = qProgress
                isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
                if isC11nQuest(qID):
                    quest = allCommonQuests.get(qID)
                    if quest is not None:
                        c11nQuests.append((quest,
                         {pGroupBy: pCur},
                         {pGroupBy: pPrev},
                         isCompleted))

        return c11nQuests

    def getBattleMattersProgress(self):
        battleMattersProgressData = []
        allCommonQuests = self.__eventsCache.getQuests()
        allCommonQuests.update(self.__eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
        if self.__questsProgress:
            for qID, qProgress in self.__questsProgress.iteritems():
                pGroupBy, pPrev, pCur = qProgress
                isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
                if qID.startswith(BATTLE_MATTERS_QUEST_ID):
                    if qID in allCommonQuests:
                        quest = allCommonQuests[qID]
                        isProgressReset = not isCompleted and quest.bonusCond.isInRow() and pCur.get('battlesCount', 0) == 0
                        if pPrev or max(pCur.itervalues()) != 0:
                            battleMattersProgressData.append((quest,
                             {pGroupBy: pCur},
                             {pGroupBy: pPrev},
                             isProgressReset,
                             isCompleted))

        return battleMattersProgressData

    def getPlayerPersonalMissionProgress(self):
        personalMissions = {}
        if self.__questsProgress:
            for qID, qProgress in self.__questsProgress.iteritems():
                _, pPrev, pCur = qProgress
                isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
                if personal_missions.g_cache.isPersonalMission(qID):
                    pqID = personal_missions.g_cache.getPersonalMissionIDByUniqueID(qID)
                    questsCache = self.__eventsCache.getPersonalMissions()
                    quest = questsCache.getAllQuests()[pqID]
                    progress = personalMissions.setdefault(quest, {})
                    progress.update({qID: isCompleted})

        if self.__PM2Progress:
            quests = self.__eventsCache.getPersonalMissions().getAllQuests()
            for qID, data in self.__PM2Progress.iteritems():
                quest = quests[qID]
                if quest in personalMissions:
                    personalMissions[quest].update(data)
                progress = personalMissions.setdefault(quest, {})
                progress.update(data)

        return personalMissions

    def packPersonalMissions(self, personalMissions):
        result = []
        for quest, data in sorted(personalMissions.items(), key=operator.itemgetter(0), cmp=self.__sortPersonalMissions):
            if data.get(quest.getAddQuestID(), False):
                complete = _PMComplete(True, True)
            elif data.get(quest.getMainQuestID(), False):
                complete = _PMComplete(True, False)
            else:
                complete = _PMComplete(False, False)
            info = getEventPostBattleInfo(quest, None, None, None, False, complete, progressData=data)
            if info is not None:
                result.append(info)

        return result

    def packQuests(self, commonQuests):
        result = []
        if commonQuests is None:
            return result
        else:
            allCommonQuests = self.__eventsCache.getQuests()
            allCommonQuests.update(self.__eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
            for e, pCur, pPrev, reset, complete in sorted(commonQuests, cmp=self.__sortCommonQuestsFunc):
                info = getEventPostBattleInfo(e, allCommonQuests, pCur, pPrev, reset, complete)
                if info is not None:
                    result.append(info)

            return result

    def packC11nQuests(self, c11nQuests):
        result = []
        if c11nQuests is None:
            return result
        else:
            questsByStyle = {}
            for e, pCur, pPrev, complete in c11nQuests:
                progressData = getDataByC11nQuest(e)
                styleID = progressData.styleID
                if styleID <= 0:
                    continue
                quests = questsByStyle.setdefault(styleID, list())
                quests.append((e,
                 pCur,
                 pPrev,
                 complete))

            for styleID, quests in questsByStyle.items():
                info = get2dProgressionStylePostBattleInfo(styleID, quests)
                if info is not None:
                    result.append(info)

            return result

    def __collectRequiredData(self, info):
        getItemByCD = self.__itemsCache.items.getItemByCD
        itemCDs = [ key for key in info.keys() if isinstance(key, int) ]
        items = sorted((getItemByCD(itemCD) for itemCD in itemCDs))
        infoAvatar = info['avatar']
        if infoAvatar:
            self.__questsProgress.update(infoAvatar.get('questsProgress', {}))
            self.__PM2Progress.update(infoAvatar.get('PM2Progress', {}))
            self.__progressiveReward = infoAvatar.get('progressiveReward')
        for item in items:
            intCD = item.intCD
            data = info[intCD]
            if data is None:
                self._addUnpackedItemID(intCD)
                continue
            self.__questsProgress.update(data.get('questsProgress', {}))
            self.__PM2Progress.update(data.get('PM2Progress', {}))

        return

    @staticmethod
    def __sortPersonalMissions(a, b):
        aFullCompleted, bFullCompleted = a.isFullCompleted(), b.isFullCompleted()
        if aFullCompleted != bFullCompleted:
            return bFullCompleted - aFullCompleted
        aCompleted, bCompleted = a.isCompleted(), b.isCompleted()
        return bCompleted - aCompleted if aCompleted != bCompleted else b.getCampaignID() - a.getCampaignID()

    @staticmethod
    def __sortCommonQuestsFunc(aData, bData):
        aQuest, aCurProg, aPrevProg, _, _ = aData
        bQuest, bCurProg, bPrevProg, _, _ = bData
        res = cmp(aQuest.isCompleted(aCurProg), bQuest.isCompleted(bCurProg))
        if res:
            return -res
        if aQuest.isCompleted() and bQuest.isCompleted(bCurProg):
            res = aQuest.getBonusCount(aCurProg) - aPrevProg.get('bonusCount', 0) - (bQuest.getBonusCount(bCurProg) - bPrevProg.get('bonusCount', 0))
            if not res:
                return res
        return cmp(aQuest.getID(), bQuest.getID())

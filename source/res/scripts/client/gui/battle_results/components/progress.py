# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/progress.py
import operator
import BigWorld
import math
from constants import EVENT_TYPE
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.battle_results.components import base
from gui.battle_results.settings import PROGRESS_ACTION
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman, getVehicleComponentsByType
from gui.shared.gui_items.Vehicle import getLevelIconPath
from gui.shared.money import Currency
from helpers import dependency
from helpers.i18n import makeString as _ms
import potapov_quests
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
MIN_BATTLES_TO_SHOW_PROGRESS = 5

class VehicleProgressHelper(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehTypeCompDescr):
        items = self.itemsCache.items
        stats = items.stats
        self.__unlocks = stats.unlocks
        self.__vehTypeCompDescr = vehTypeCompDescr
        self.__vehicle = items.getItemByCD(vehTypeCompDescr)
        self.__vehicleXp = stats.vehiclesXPs.get(self.__vehTypeCompDescr, 0)
        self.__avgVehicleXp = self.__getAvgVehicleXp(self.__vehTypeCompDescr)

    def clear(self):
        self.__unlocks = None
        self.__vehicle = None
        self.__vehicleXp = None
        self.__avgVehicleXp = None
        self.__vehTypeCompDescr = None
        return

    def getProgressList(self, vehicleBattleXp, pureCreditsReceived, tankmenXps):
        result = []
        ready2UnlockVehicles, ready2UnlockModules = self.__getReady2UnlockItems(vehicleBattleXp)
        ready2BuyVehicles, ready2BuyModules = self.__getReady2BuyItems(pureCreditsReceived)
        result.extend(ready2UnlockModules)
        result.extend(ready2BuyModules)
        result.extend(self.__getNewSkilledTankmen(tankmenXps))
        result.extend(ready2UnlockVehicles)
        result.extend(ready2BuyVehicles)
        return result

    def __getAvgVehicleXp(self, vehTypeCompDescr):
        vehiclesStats = self.itemsCache.items.getAccountDossier().getRandomStats().getVehicles()
        vehicleStats = vehiclesStats.get(vehTypeCompDescr, None)
        if vehicleStats is not None:
            battlesCount, wins, xp = vehicleStats
            if battlesCount:
                return xp / battlesCount
            return 0
        else:
            return 0

    def __getReady2UnlockItems(self, vehicleBattleXp):
        ready2UnlockModules = []
        ready2UnlockVehicles = []
        possible2UnlockItems = g_techTreeDP.getAllPossibleItems2Unlock(self.__vehicle, self.__unlocks)
        getter = self.itemsCache.items.getItemByCD
        for itemTypeCD, unlockProps in possible2UnlockItems.iteritems():
            item = getter(itemTypeCD)
            if self.__vehicleXp - unlockProps.xpCost <= vehicleBattleXp and item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                avgBattles2Unlock = self.__getAvgBattles2Unlock(unlockProps)
                if not self.__vehicleXp > unlockProps.xpCost:
                    if 0 < avgBattles2Unlock <= MIN_BATTLES_TO_SHOW_PROGRESS:
                        ready2UnlockVehicles.append(self.__makeUnlockVehicleVO(item, unlockProps, avgBattles2Unlock))
                elif self.__vehicleXp > unlockProps.xpCost:
                    ready2UnlockModules.append(self.__makeUnlockModuleVO(item, unlockProps))

        return (ready2UnlockVehicles, ready2UnlockModules)

    def __getReady2BuyItems(self, pureCreditsReceived):
        ready2BuyModules = []
        ready2BuyVehicles = []
        creditsValue = self.itemsCache.items.stats.credits
        unlockedVehicleItems = g_techTreeDP.getUnlockedVehicleItems(self.__vehicle, self.__unlocks)
        getter = self.itemsCache.items.getItemByCD
        for itemTypeCD, unlockProps in unlockedVehicleItems.iteritems():
            item = getter(itemTypeCD)
            price = item.getBuyPrice(preferred=False).price
            if price.isCurrencyDefined(Currency.CREDITS) and not item.isInInventory:
                priceCredits = price.credits
                if creditsValue - priceCredits <= pureCreditsReceived and creditsValue > priceCredits:
                    if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                        ready2BuyVehicles.append(self.__makeVehiclePurchaseVO(item, unlockProps, price.credits))
                    elif not item.isInstalled(self.__vehicle):
                        items = getVehicleComponentsByType(self.__vehicle, item.itemTypeID).values()
                        if len(items) > 0:
                            installedModule = max(items, key=operator.itemgetter('level'))
                            if item.level > installedModule.level:
                                ready2BuyModules.append(self.__makeModulePurchaseVO(item, unlockProps, price.credits))

        return (ready2BuyVehicles, ready2BuyModules)

    def __getNewSkilledTankmen(self, tankmenXps):
        skilledTankmans = []
        for slotIdx, tman in self.__vehicle.crew:
            if tman is not None and tman.hasSkillToLearn():
                if not tman.isMaxRoleLevel:
                    continue
                tmanBattleXp = tankmenXps.get(tman.invID, 0)
                avgBattles2NewSkill = 0
                if tman.hasNewSkill(useCombinedRoles=True):
                    if tmanBattleXp - tman.descriptor.freeXP > 0:
                        skilledTankmans.append(self.__makeTankmanVO(tman, avgBattles2NewSkill))
                else:
                    tmanDossier = self.itemsCache.items.getTankmanDossier(tman.invID)
                    avgBattles2NewSkill = self.__getAvgBattles2NewSkill(tmanDossier.getAvgXP(), tman)
                    if 0 < avgBattles2NewSkill <= MIN_BATTLES_TO_SHOW_PROGRESS:
                        skilledTankmans.append(self.__makeTankmanVO(tman, avgBattles2NewSkill))

        return skilledTankmans

    def __getAvgBattles2Unlock(self, unlockProps):
        return int(math.ceil((unlockProps.xpCost - self.__vehicleXp) / float(self.__avgVehicleXp))) if self.__avgVehicleXp > 0 else 0

    def __getAvgBattles2NewSkill(self, avgTmanXp, tman):
        return max(1, math.ceil(tman.getNextSkillXpCost() / avgTmanXp)) if avgTmanXp > 0 else 0

    def __makeTankmanDescription(self, tankman):
        role = text_styles.main(tankman.roleUserName)
        name = text_styles.standard(tankman.fullUserName)
        return _ms(BATTLE_RESULTS.COMMON_CREWMEMBER_DESCRIPTION, name=name, role=role)

    def __makeVehicleDescription(self, vehicle):
        vehicleType = text_styles.standard(vehicle.typeUserName)
        vehicleName = text_styles.main(vehicle.userName)
        return _ms(BATTLE_RESULTS.COMMON_VEHICLE_DETAILS, vehicle=vehicleName, type=vehicleType)

    def __makeTankmanVO(self, tman, avgBattles2NewSkill):
        prediction = ''
        if avgBattles2NewSkill > 0:
            prediction = _ms(BATTLE_RESULTS.COMMON_NEWSKILLPREDICTION, battles=BigWorld.wg_getIntegralFormat(avgBattles2NewSkill))
        return {'title': _ms(BATTLE_RESULTS.COMMON_CREWMEMBER_NEWSKILL),
         'description': self.__makeTankmanDescription(tman),
         'tankmenIcon': Tankman.getSmallIconPath(tman.nationID, tman.descriptor.iconID),
         'prediction': prediction,
         'linkEvent': PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE,
         'linkId': tman.invID}

    def __makeUnlockModuleVO(self, item, unlockProps):
        isEnoughXp = self.__vehicleXp - unlockProps.xpCost >= 0
        unlockXp = unlockProps.xpCost
        formatter = text_styles.expText if isEnoughXp else text_styles.error
        formattedPrice = BigWorld.wg_getIntegralFormat(unlockXp) + icons.xp()
        return {'title': _ms(BATTLE_RESULTS.COMMON_FITTING_RESEARCH),
         'description': text_styles.main(item.userName),
         'fittingType': item.itemTypeName,
         'lvlIcon': getLevelIconPath(item.level),
         'price': formatter(formattedPrice),
         'linkEvent': PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE,
         'linkId': unlockProps.parentID}

    def __makeUnlockVehicleVO(self, item, unlockProps, avgBattlesTillUnlock):
        prediction = ''
        if avgBattlesTillUnlock > 0:
            prediction = _ms(BATTLE_RESULTS.COMMON_RESEARCHPREDICTION, battles=avgBattlesTillUnlock)
        isEnoughXp = self.__vehicleXp - unlockProps.xpCost >= 0
        unlockXp = unlockProps.xpCost
        formatter = text_styles.expText if isEnoughXp else text_styles.error
        formattedPrice = BigWorld.wg_getIntegralFormat(unlockXp) + icons.xp()
        return {'title': _ms(BATTLE_RESULTS.COMMON_VEHICLE_RESEARCH),
         'description': self.__makeVehicleDescription(item),
         'vehicleIcon': item.iconSmall,
         'lvlIcon': getLevelIconPath(item.level),
         'prediction': prediction,
         'price': formatter(formattedPrice),
         'linkEvent': PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE,
         'linkId': unlockProps.parentID}

    def __makeVehiclePurchaseVO(self, item, unlockProps, creditPrice):
        formattedPrice = BigWorld.wg_getIntegralFormat(creditPrice) + icons.credits()
        return {'title': _ms(BATTLE_RESULTS.COMMON_VEHICLE_PURCHASE),
         'description': self.__makeVehicleDescription(item),
         'vehicleIcon': item.iconSmall,
         'lvlIcon': getLevelIconPath(item.level),
         'price': text_styles.credits(formattedPrice),
         'linkEvent': PROGRESS_ACTION.PURCHASE_UNLOCK_TYPE,
         'linkId': unlockProps.parentID}

    def __makeModulePurchaseVO(self, item, unlockProps, creditPrice):
        formattedPrice = BigWorld.wg_getIntegralFormat(creditPrice) + icons.credits()
        return {'title': _ms(BATTLE_RESULTS.COMMON_FITTING_PURCHASE),
         'description': text_styles.main(item.userName),
         'fittingType': item.itemTypeName,
         'lvlIcon': getLevelIconPath(item.level),
         'price': text_styles.credits(formattedPrice),
         'linkEvent': PROGRESS_ACTION.PURCHASE_UNLOCK_TYPE,
         'linkId': unlockProps.parentID}


class VehicleProgressBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        for intCD, data in reusable.personal.getVehicleCDsIterator(result):
            vehicleBattleXp = data.get('xp', 0)
            pureCreditsReceived = data.get('pureCreditsReceived', 0)
            tmenXps = dict(data.get('xpByTmen', []))
            helper = VehicleProgressHelper(intCD)
            progress = helper.getProgressList(vehicleBattleXp, pureCreditsReceived, tmenXps)
            for item in progress:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', item))

            helper.clear()


class QuestsProgressBlock(base.StatsBlock):
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def getVO(self):
        vo = super(QuestsProgressBlock, self).getVO()
        return vo

    def setRecord(self, result, reusable):
        questsProgress = reusable.personal.getQuestsProgress()
        if not questsProgress:
            return
        else:

            def _sortCommonQuestsFunc(aData, bData):
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

            from gui.Scaleform.daapi.view.lobby.server_events import old_events_helpers
            quests = self.eventsCache.getQuests()
            isFallout = reusable.common.arenaVisitor.gui.isFalloutBattle()
            commonQuests, potapovQuests = [], {}
            for qID, qProgress in questsProgress.iteritems():
                pGroupBy, pPrev, pCur = qProgress
                isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
                if qID in quests:
                    quest = quests[qID]
                    isProgressReset = not isCompleted and quest.bonusCond.isInRow() and pCur.get('battlesCount', 0) == 0
                    if pPrev or max(pCur.itervalues()) != 0:
                        commonQuests.append((quest,
                         {pGroupBy: pCur},
                         {pGroupBy: pPrev},
                         isProgressReset,
                         isCompleted))
                if potapov_quests.g_cache.isPotapovQuest(qID):
                    pqID = potapov_quests.g_cache.getPotapovQuestIDByUniqueID(qID)
                    if isFallout:
                        questsCache = self.eventsCache.fallout
                    else:
                        questsCache = self.eventsCache.random
                    quest = questsCache.getQuests()[pqID]
                    progress = potapovQuests.setdefault(quest, {})
                    progress.update({qID: isCompleted})

            for e, data in sorted(potapovQuests.items(), key=operator.itemgetter(0)):
                if data.get(e.getAddQuestID(), False):
                    complete = (True, True)
                elif data.get(e.getMainQuestID(), False):
                    complete = (True, False)
                else:
                    complete = (False, False)
                info = old_events_helpers.getEventPostBattleInfo(e, quests, None, None, False, complete)
                if info is not None:
                    self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

            for e, pCur, pPrev, reset, complete in sorted(commonQuests, cmp=_sortCommonQuestsFunc):
                info = old_events_helpers.getEventPostBattleInfo(e, quests, pCur, pPrev, reset, complete)
                if info is not None:
                    self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

            return

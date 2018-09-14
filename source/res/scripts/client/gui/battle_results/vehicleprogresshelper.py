# Embedded file name: scripts/client/gui/battle_results/VehicleProgressHelper.py
import BigWorld
import math
from operator import attrgetter
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman, getVehicleComponentsByType
from gui.shared.gui_items.Vehicle import getLevelIconPath
from helpers.i18n import makeString as _ms

class PROGRESS_ACTION(object):
    RESEARCH_UNLOCK_TYPE = 'UNLOCK_LINK_TYPE'
    PURCHASE_UNLOCK_TYPE = 'PURCHASE_LINK_TYPE'
    NEW_SKILL_UNLOCK_TYPE = 'NEW_SKILL_LINK_TYPE'


MIN_BATTLES_TO_SHOW_PROGRESS = 5

class VehicleProgressHelper(object):

    def __init__(self, vehTypeCompDescr):
        self._items = g_itemsCache.items
        self._stats = self._items.stats
        self._unlocks = self._stats.unlocks
        self.__vehTypeCompDescr = vehTypeCompDescr
        self.__vehicle = self._items.getItemByCD(vehTypeCompDescr)
        self.__vehicleXp = self._stats.vehiclesXPs.get(self.__vehTypeCompDescr, 0)
        self.__avgVehicleXp = self.__getAvgVehicleXp(self.__vehTypeCompDescr)

    def clear(self):
        self._items = None
        self._stats = None
        self._unlocks = None
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
        vehiclesStats = self._items.getAccountDossier().getRandomStats().getVehicles()
        vehicleStats = vehiclesStats.get(vehTypeCompDescr, None)
        if vehicleStats is not None:
            battlesCount, wins, markOfMastery, xp = vehicleStats
            if battlesCount:
                return xp / battlesCount
            return 0
        else:
            return 0

    def __getReady2UnlockItems(self, vehicleBattleXp):
        ready2UnlockModules = []
        ready2UnlockVehicles = []
        possible2UnlockItems = g_techTreeDP.getAllPossibleItems2Unlock(self.__vehicle, self._unlocks)
        getter = self._items.getItemByCD
        for itemTypeCD, unlockProps in possible2UnlockItems.iteritems():
            item = getter(itemTypeCD)
            if self.__vehicleXp - unlockProps.xpCost <= vehicleBattleXp:
                if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                    avgBattles2Unlock = self.__getAvgBattles2Unlock(unlockProps)
                    if self.__vehicleXp > unlockProps.xpCost or 0 < avgBattles2Unlock <= MIN_BATTLES_TO_SHOW_PROGRESS:
                        ready2UnlockVehicles.append(self.__makeUnlockVehicleVO(item, unlockProps, avgBattles2Unlock))
                elif self.__vehicleXp > unlockProps.xpCost:
                    ready2UnlockModules.append(self.__makeUnlockModuleVO(item, unlockProps))

        return (ready2UnlockVehicles, ready2UnlockModules)

    def __getReady2BuyItems(self, pureCreditsReceived):
        ready2BuyModules = []
        ready2BuyVehicles = []
        creditsValue = self._stats.credits
        unlockedVehicleItems = g_techTreeDP.getUnlockedVehicleItems(self.__vehicle, self._unlocks)
        getter = self._items.getItemByCD
        for itemTypeCD, unlockProps in unlockedVehicleItems.iteritems():
            item = getter(itemTypeCD)
            price = item.altPrice or item.buyPrice
            if price and not item.isInInventory and creditsValue - price[0] <= pureCreditsReceived and creditsValue > price[0]:
                if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                    ready2BuyVehicles.append(self.__makeVehiclePurchaseVO(item, unlockProps, price[0]))
                elif not item.isInstalled(self.__vehicle):
                    items = getVehicleComponentsByType(self.__vehicle, item.itemTypeID).values()
                    if len(items) > 0:
                        installedModule = max(items, key=attrgetter('level'))
                        if item.level > installedModule.level:
                            ready2BuyModules.append(self.__makeModulePurchaseVO(item, unlockProps, price[0]))

        return (ready2BuyVehicles, ready2BuyModules)

    def __getNewSkilledTankmen(self, tankmenXps):
        skilledTankmans = []
        for slotIdx, tman in self.__vehicle.crew:
            if tman is not None:
                tmanBattleXp = tankmenXps.get(tman.invID, 0)
                avgBattles2NewSkill = 0
                if tman.hasNewSkill:
                    if tmanBattleXp - tman.descriptor.freeXP > 0:
                        skilledTankmans.append(self.__makeTankmanVO(tman, avgBattles2NewSkill))
                else:
                    tmanDossier = self._items.getTankmanDossier(tman.invID)
                    avgBattles2NewSkill = self.__getAvgBattles2NewSkill(tmanDossier.getAvgXP(), tman)
                    if 0 < avgBattles2NewSkill <= MIN_BATTLES_TO_SHOW_PROGRESS:
                        skilledTankmans.append(self.__makeTankmanVO(tman, avgBattles2NewSkill))

        return skilledTankmans

    def __getAvgBattles2Unlock(self, unlockProps):
        if self.__avgVehicleXp > 0:
            return int(math.ceil((unlockProps.xpCost - self.__vehicleXp) / float(self.__avgVehicleXp)))
        return 0

    def __getAvgBattles2NewSkill(self, avgTmanXp, tman):
        if avgTmanXp > 0:
            return max(1, math.ceil(tman.getNextSkillXpCost() / avgTmanXp))
        return 0

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

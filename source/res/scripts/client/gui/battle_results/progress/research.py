# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/progress/research.py
import math
from collections import namedtuple
from constants import NEW_PERK_SYSTEM as NPS
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from items import tankmen
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
MIN_BATTLES_TO_SHOW_PROGRESS = 5
TankmanProgress = namedtuple('TankmanProgress', ('tman', 'newSkillEarned', 'bonusSkillsAmount', 'avgBattles2NewSkill', 'skin'))
VehicleProgress = namedtuple('VehicleProgress', ('item', 'unlockProps', 'avgBattles2Unlock'))
ModuleProgress = namedtuple('ModuleProgress', ('item', 'unlockProps'))

class VehicleProgressHelper(object):
    __slots__ = ('__unlocks', '__vehTypeCompDescr', '__vehicle', '__vehicleXp', '__avgVehicleXp')
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehTypeCompDescr):
        items = self._itemsCache.items
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

    def __getAvgVehicleXp(self, vehTypeCompDescr):
        vehiclesStats = self._itemsCache.items.getAccountDossier().getRandomStats().getVehicles()
        vehicleStats = vehiclesStats.get(vehTypeCompDescr, None)
        if vehicleStats is not None:
            battlesCount, _, xp = vehicleStats
            if battlesCount:
                return xp / battlesCount
            return 0
        else:
            return 0

    def getReady2UnlockItems(self, vehicleBattleXp):
        ready2UnlockModules = []
        ready2UnlockVehicles = []
        possible2UnlockItems = g_techTreeDP.getAllPossibleItems2Unlock(self.__vehicle, self.__unlocks)
        getter = self._itemsCache.items.getItemByCD
        for itemTypeCD, unlockProps in possible2UnlockItems.iteritems():
            item = getter(itemTypeCD)
            if self.__vehicleXp - unlockProps.xpCost <= vehicleBattleXp and item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                avgBattles2Unlock = self.__getAvgBattles2Unlock(unlockProps)
                if not self.__vehicleXp > unlockProps.xpCost:
                    if 0 < avgBattles2Unlock <= MIN_BATTLES_TO_SHOW_PROGRESS:
                        ready2UnlockVehicles.append(VehicleProgress(item, unlockProps, avgBattles2Unlock))
                elif self.__vehicleXp > unlockProps.xpCost:
                    ready2UnlockModules.append(ModuleProgress(item, unlockProps))

        return (ready2UnlockVehicles, ready2UnlockModules)

    def getNewSkilledTankmen(self, tankmenXps):
        skilledTankmen = []
        for _, tman in self.__vehicle.crew:
            if tman is not None and tman.hasSkillToLearn():
                if not tman.isMaxRoleLevel:
                    continue
                tmanBattleXp = tankmenXps.get(tman.invID, 0)
                avgBattles2NewSkill = 0
                newSkillEarned = False
                bonusSkillsAmount = 0
                if tman.hasNewSkill(useCombinedRoles=True):
                    tmanDescr = tman.descriptor
                    lastSkillNumber = tmanDescr.lastSkillSeqNumber
                    wallet = tmanDescr.freeXP + tankmen.TankmanDescr.getXpCostForSkillsLevels(tmanDescr.lastSkillLevel if lastSkillNumber else 0, lastSkillNumber)
                    skillsCountBefore = min(tmanDescr.getSkillsCountFromXp(wallet - tmanBattleXp), NPS.MAX_MAJOR_PERKS)
                    skillsCount = min(tmanDescr.getSkillsCountFromXp(wallet), NPS.MAX_MAJOR_PERKS)
                    newSkillEarned, bonusSkillsAmount = self.__getBonusSkillsAmount(tman, skillsCountBefore, skillsCount)
                else:
                    tmanDossier = self._itemsCache.items.getTankmanDossier(tman.invID)
                    avgBattles2NewSkill = self.__getAvgBattles2NewSkill(tmanDossier.getAvgXP(), tman)
                    if 0 < avgBattles2NewSkill <= MIN_BATTLES_TO_SHOW_PROGRESS:
                        newSkillEarned, bonusSkillsAmount = self.__getBonusSkillsAmount(tman, 1, 0)
                if newSkillEarned:
                    skin = self._itemsCache.items.getCrewSkin(tman.skinID) if tman.skinID != NO_CREW_SKIN_ID else None
                    skilledTankmen.append(TankmanProgress(tman, newSkillEarned, bonusSkillsAmount, avgBattles2NewSkill, skin))

        return skilledTankmen

    @staticmethod
    def __getBonusSkillsAmount(tmanToCheck, skillsCountBefore, skillsCountAfter):
        newSkillsCount = skillsCountAfter - skillsCountBefore
        if newSkillsCount > 0:
            bonusSkillsAmount = 0
            if (skillsCountBefore + tmanToCheck.freeSkillsCount) % 2 == 0:
                bonusSkillsAmount = newSkillsCount * (len(tmanToCheck.combinedRoles) - 1)
            return (True, bonusSkillsAmount)
        return (False, 0)

    def __getAvgBattles2Unlock(self, unlockProps):
        return int(math.ceil((unlockProps.xpCost - self.__vehicleXp) / float(self.__avgVehicleXp))) if self.__avgVehicleXp > 0 else 0

    def __getAvgBattles2NewSkill(self, avgTmanXp, tman):
        return max(1, math.ceil(tman.getNextSkillXpCost() / avgTmanXp)) if avgTmanXp > 0 else 0

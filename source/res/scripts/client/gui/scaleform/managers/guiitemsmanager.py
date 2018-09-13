# Embedded file name: scripts/client/gui/Scaleform/managers/GuiItemsManager.py
import weakref
import cPickle as pickle
from debug_utils import LOG_WARNING
from gui import GUI_NATIONS_ORDER_INDEX
from gui.shared import g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import TankmanSkill
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
from gui.shared.gui_items.dossier.achievements.abstract import isRareAchievement
from gui.Scaleform.framework.entities.abstract.GuiItemsManagerMeta import GuiItemsManagerMeta
from nations import NAMES

class ItemWrapper(object):

    def __init__(self, items, itemTypeIdx, itemID):
        self._items = weakref.proxy(items)
        self.itemTypeIdx = itemTypeIdx
        self.itemID = itemID
        self.item = self._getItem(items, itemID)

    def getattr(self, attrName):
        if hasattr(self, attrName):
            return getattr(self, attrName)
        elif hasattr(self.item, attrName):
            return getattr(self.item, attrName)
        else:
            LOG_WARNING('Unknown item attribute', attrName, self.itemTypeIdx, self.itemID, self.item)
            return None

    def call(self, methodName, *args):
        if hasattr(self, methodName):
            return getattr(self, methodName)(*args)
        elif hasattr(self.item, methodName):
            return getattr(self.item, methodName)(*args)
        else:
            LOG_WARNING('Unknown item method', methodName, self.itemTypeIdx, self.itemID, self.item)
            return None

    def toString(self):
        return str(self.item)

    def _getItem(self, items, itemID):
        return items.getItemByCD(int(itemID))


class TankmanWrapper(ItemWrapper):

    def __init__(self, items, invID):
        super(TankmanWrapper, self).__init__(items, GUI_ITEM_TYPE.TANKMAN, int(invID))

    @property
    def nativeVehicle(self):
        return self.item.vehicleNativeDescr.type.compDescr

    @property
    def currentVehicle(self):
        if self.item.isIntTank:
            return self.item.vehicleDescr.type.compactDescr
        else:
            return None

    @property
    def skills(self):
        return [ skill.name for skill in self.item.skills ]

    def _getItem(self, items, invID):
        return items.getTankman(invID)


class TankmanSkillWrapper(ItemWrapper):

    def __init__(self, items, itemID):
        super(TankmanSkillWrapper, self).__init__(items, GUI_ITEM_TYPE.SKILL, itemID)

    def _getItem(self, items, itemID):
        skillName, tankmanID = itemID
        if tankmanID > 0:
            tankman = items.getTankman(tankmanID)
            if tankman is None:
                LOG_WARNING('Empty tankman for skill', skillName, tankmanID)
            for s in tankman.skills:
                if s.name == skillName:
                    return s

        return TankmanSkill(skillName)


class VehicleWrapper(ItemWrapper):

    def __init__(self, items, intCD):
        super(VehicleWrapper, self).__init__(items, GUI_ITEM_TYPE.VEHICLE, int(intCD))

    @property
    def gun(self):
        return self.item.gun.intCD

    @property
    def turret(self):
        return self.item.turret.intCD

    @property
    def engine(self):
        return self.item.engine.intCD

    @property
    def chassis(self):
        return self.item.chassis.intCD

    @property
    def radio(self):
        return self.item.radio.intCD

    @property
    def optDevs(self):
        return [ (item.intCD if item else None) for item in self.item.optDevices ]

    @property
    def eqs(self):
        return [ (item.intCD if item else None) for item in self.item.eqs ]

    @property
    def shells(self):
        return [ (item.intCD if item else None) for item in self.item.shells ]

    @property
    def crew(self):
        return [ (slotIdx, t.invID if t else None) for slotIdx, t in self.item.crew ]

    @property
    def typeIndex(self):
        return VEHICLE_TYPES_ORDER_INDICES[self.item.type]

    @property
    def nationIndex(self):
        return GUI_NATIONS_ORDER_INDEX[NAMES[self.item.nationID]]


class _Dossier(ItemWrapper):

    def getattr(self, attrName):
        stats = self.item.getTotalStats()
        if hasattr(stats, attrName):
            return getattr(self, attrName)
        return super(_Dossier, self).getattr(attrName)

    def call(self, methodName, *args):
        stats = self.item.getTotalStats()
        if hasattr(stats, methodName):
            return getattr(stats, methodName)(*args)
        return super(_Dossier, self).call(methodName, *args)

    def getAchievements(self, isInDossier = True):
        dcd = pickle.dumps(self.item.getDossierDescr().makeCompDescr())
        result = []
        for section in self.item.getTotalStats().getAchievements(isInDossier):
            result.append([])
            for a in section:
                result[-1].append(self._packAchievement(a, dcd))

        return result

    def getNearestAchievements(self):
        dcd = pickle.dumps(self.item.getDossierDescr().makeCompDescr())
        return [ self._packAchievement(a, dcd) for a in self.item.getTotalStats().getNearestAchievements() ]

    def getSignificantAchievements(self):
        dcd = pickle.dumps(self.item.getDossierDescr().makeCompDescr())
        return [ self._packAchievement(a, dcd) for a in self.item.getTotalStats().getSignificantAchievements() ]

    def _getDossierType(self):
        return None

    def _packAchievement(self, achieve, dossierCompDescr):
        isRare = isRareAchievement(achieve)
        rareID = None
        name = achieve.name
        if isRare:
            rareID = achieve.requestImageID()
            name = 'rare%d' % achieve.rareID
        return {'name': name,
         'value': achieve.getValue(),
         'section': achieve.getSection(),
         'type': achieve.getType(),
         'dossierCompDescr': dossierCompDescr,
         'rareIconId': rareID,
         'isRare': isRare,
         'isDone': achieve.isDone,
         'lvlUpTotalValue': achieve.getLevelUpTotalValue(),
         'lvlUpValue': achieve.lvlUpValue,
         'isDossierForCurrentUser': self.itemID is None,
         'description': achieve.description,
         'userName': achieve.userName,
         'icon': achieve.icon,
         'dossierType': self._getDossierType(),
         'isInDossier': achieve.isInDossier()}


class AccountDossierWrapper(_Dossier):

    def __init__(self, items, itemID):
        super(AccountDossierWrapper, self).__init__(items, GUI_ITEM_TYPE.ACCOUNT_DOSSIER, itemID)

    def _getItem(self, items, itemID):
        return items.getAccountDossier(itemID)

    def getTechniqueListVehicles(self):
        result = []
        for intCD, (battlesCount, wins, markOfMastery, xp) in self.item.getTotalStats().getVehicles().iteritems():
            avgXP = xp / battlesCount if battlesCount else 0
            vehicle = g_itemsCache.items.getItemByCD(intCD)
            if vehicle is not None:
                result.append({'id': intCD,
                 'inventoryID': vehicle.invID,
                 'shortUserName': vehicle.shortUserName,
                 'battlesCount': battlesCount,
                 'winsEfficiency': round(100.0 * wins / battlesCount) if battlesCount else 0,
                 'avgExperience': avgXP,
                 'userName': vehicle.userName,
                 'typeIndex': VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
                 'nationIndex': GUI_NATIONS_ORDER_INDEX[NAMES[vehicle.nationID]],
                 'nationID': vehicle.nationID,
                 'level': vehicle.level,
                 'markOfMastery': markOfMastery,
                 'tankIconPath': vehicle.iconSmall,
                 'typeIconPath': '../maps/icons/filters/tanks/%s.png' % vehicle.type,
                 'isInHangar': vehicle.invID > 0})

        return result

    def getMaxFrags(self):
        stats = self.item.getTotalStats()
        return (stats.getMaxFrags(), stats.getMaxFragsVehicle())

    def getMaxXP(self):
        stats = self.item.getTotalStats()
        return (stats.getMaxXP(), stats.getMaxXpVehicle())

    def getVehicles(self):
        return dict(((str(k), v) for k, v in self.item.getTotalStats().getVehicles().iteritems()))

    def getMarksOfMastery(self):
        return self.item.getTotalStats().getMarkOfMastery()

    def _getDossierType(self):
        return GUI_ITEM_TYPE.ACCOUNT_DOSSIER


class VehicleDossierWrapper(_Dossier):

    def __init__(self, items, itemID):
        super(VehicleDossierWrapper, self).__init__(items, GUI_ITEM_TYPE.VEHICLE_DOSSIER, itemID)

    def getMaxVehicleFrags(self):
        return self.item.getTotalStats().getMaxFrags()

    def getMaxVehicleXP(self):
        return self.item.getTotalStats().getMaxXP()

    def _getItem(self, items, itemID):
        return items.getVehicleDossier(*itemID)

    def _getDossierType(self):
        return GUI_ITEM_TYPE.VEHICLE_DOSSIER


class AchievementWrapper(ItemWrapper):

    def __init__(self, items, itemID):
        achieveName, dossierID = itemID
        self.__rareID = None
        if achieveName.startswith('rare'):
            self.__rareID = int(achieveName.replace('rare', ''))
        super(AchievementWrapper, self).__init__(items, GUI_ITEM_TYPE.ACHIEVEMENT, itemID)
        self.__isInDossier = False
        d = self.__getDossier(items, *dossierID)
        if d is not None:
            self.__isInDossier = self.item.isInDossier()
        return

    def isInDossier(self):
        return self.__isInDossier

    def isRare(self):
        return self.__rareID is not None

    def getDossierCompDescr(self):
        achieveName, dossierID = self.itemID
        d = self.__getDossier(g_itemsCache.items, *dossierID)
        if d is not None:
            return pickle.dumps(d.getDossierDescr().makeCompDescr())
        else:
            return

    def _getItem(self, items, itemID):
        achieveName, dossierID = itemID
        dossier = self.__getDossier(items, *dossierID)
        if dossier is not None:
            if self.__rareID is not None:
                return dossier.getTotalStats().getAchievement('rareAchievements').get(self.__rareID)
            return dossier.getTotalStats().getAchievement(achieveName)
        else:
            LOG_WARNING('Unknown dossier type', itemID)
            return

    def __getDossier(self, items, dossierType, dossierID):
        if dossierType == GUI_ITEM_TYPE.ACCOUNT_DOSSIER:
            return items.getAccountDossier(dossierID)
        elif dossierType == GUI_ITEM_TYPE.VEHICLE_DOSSIER:
            return items.getVehicleDossier(*dossierID)
        elif dossierType == GUI_ITEM_TYPE.TANKMAN_DOSSIER:
            return items.getTankmanDossier(dossierID)
        else:
            return None


class GuiItemsManager(GuiItemsManagerMeta):

    def __init__(self):
        super(GuiItemsManager, self).__init__()
        self.__wrappers = {GUI_ITEM_TYPE.VEHICLE: lambda itemTypeIdx, itemID: VehicleWrapper(g_itemsCache.items, itemID),
         GUI_ITEM_TYPE.SKILL: lambda itemTypeIdx, itemID: TankmanSkillWrapper(g_itemsCache.items, itemID),
         GUI_ITEM_TYPE.TANKMAN: lambda itemTypeIdx, itemID: TankmanWrapper(g_itemsCache.items, itemID),
         GUI_ITEM_TYPE.ACCOUNT_DOSSIER: lambda itemTypeIdx, itemID: AccountDossierWrapper(g_itemsCache.items, itemID),
         GUI_ITEM_TYPE.VEHICLE_DOSSIER: lambda itemTypeIdx, itemID: VehicleDossierWrapper(g_itemsCache.items, itemID),
         GUI_ITEM_TYPE.ACHIEVEMENT: lambda itemTypeIdx, itemID: AchievementWrapper(g_itemsCache.items, itemID)}

    def __getWrapper(self, itemTypeIdx, itemID):
        if itemTypeIdx in self.__wrappers:
            return self.__wrappers[itemTypeIdx](itemTypeIdx, itemID)
        return ItemWrapper(g_itemsCache.items, itemTypeIdx, itemID)

    def _getItemAttribute(self, itemTypeIdx, itemID, attrName):
        return self.__getWrapper(itemTypeIdx, itemID).getattr(attrName)

    def _callItemMethod(self, itemTypeIdx, itemID, methodName, kargs):
        return self.__getWrapper(itemTypeIdx, itemID).call(methodName, *kargs)

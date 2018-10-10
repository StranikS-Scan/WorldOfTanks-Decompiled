# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/contexts.py
from collections import namedtuple
import constants
from constants import ARENA_GUI_TYPE
import gui
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import recruit_helper
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getTankmanSkill
from gui.shared.gui_items.dossier import factories, loadDossier
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters.formatters import NO_BONUS_SIMPLIFIED_SCHEME
from gui.shared.tooltips import TOOLTIP_COMPONENT
from helpers import dependency
from helpers.i18n import makeString
from shared_utils import findFirst
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

def _getCmpVehicle():
    return cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicle()


def _getCmpInitialVehicle():
    return cmp_helpers.getCmpConfiguratorMainView().getInitialVehicleData()


class StatsConfiguration(object):
    __slots__ = ('vehicle', 'sellPrice', 'buyPrice', 'unlockPrice', 'inventoryCount', 'vehiclesCount', 'node', 'xp', 'dailyXP', 'minRentPrice', 'restorePrice', 'rentals', 'slotIdx', 'futureRentals', 'isAwardWindow')

    def __init__(self):
        self.vehicle = None
        self.sellPrice = False
        self.buyPrice = True
        self.minRentPrice = True
        self.restorePrice = True
        self.rentals = True
        self.futureRentals = False
        self.unlockPrice = True
        self.inventoryCount = True
        self.vehiclesCount = True
        self.node = None
        self.xp = True
        self.dailyXP = True
        self.slotIdx = 0
        self.isAwardWindow = False
        return


class StatusConfiguration(object):
    __slots__ = ('vehicle', 'slotIdx', 'eqs', 'checkBuying', 'node', 'isAwardWindow', 'isResearchPage', 'checkNotSuitable', 'showCustomStates')

    def __init__(self):
        self.vehicle = None
        self.slotIdx = 0
        self.eqs = tuple()
        self.checkBuying = False
        self.node = None
        self.isResearchPage = False
        self.isAwardWindow = False
        self.checkNotSuitable = False
        self.showCustomStates = False
        return


class ParamsConfiguration(object):
    __slots__ = ('vehicle', 'params', 'crew', 'eqs', 'devices', 'dossier', 'dossierType', 'isCurrentUserDossier', 'historicalBattleID', 'checkAchievementExistence', 'simplifiedOnly', 'externalCrewParam', 'vehicleLevel', 'arenaType')

    def __init__(self):
        self.vehicle = None
        self.params = True
        self.crew = True
        self.eqs = True
        self.devices = True
        self.dossier = None
        self.dossierType = None
        self.isCurrentUserDossier = True
        self.historicalBattleID = -1
        self.simplifiedOnly = False
        self.externalCrewParam = False
        self.vehicleLevel = 0
        self.arenaType = ARENA_GUI_TYPE.RANDOM
        self.checkAchievementExistence = True
        return


class ToolTipContext(object):

    def __init__(self, component, fieldsToExclude=None):
        self._component = component
        self._fieldsToExclude = fieldsToExclude or tuple()

    @property
    def fieldsToExclude(self):
        return self._fieldsToExclude

    def buildItem(self, *args, **kwargs):
        return None

    def getStatusConfiguration(self, item):
        return StatusConfiguration()

    def getStatsConfiguration(self, item):
        return StatsConfiguration()

    def getParamsConfiguration(self, item):
        return ParamsConfiguration()

    def getComponent(self):
        return self._component

    def getParams(self):
        return {}


class ShopContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(ShopContext, self).__init__(TOOLTIP_COMPONENT.SHOP, fieldsToExclude)

    def buildItem(self, intCD):
        return self.itemsCache.items.getItemByCD(int(intCD))

    def getStatusConfiguration(self, item):
        value = super(ShopContext, self).getStatusConfiguration(item)
        value.checkBuying = True
        value.showCustomStates = True
        return value

    def getStatsConfiguration(self, item):
        value = super(ShopContext, self).getStatsConfiguration(item)
        value.xp = False
        value.dailyXP = False
        return value

    def getParamsConfiguration(self, item):
        value = super(ShopContext, self).getParamsConfiguration(item)
        value.params = gui.GUI_SETTINGS.technicalInfo
        value.eqs = False
        value.devices = False
        return value


class AwardContext(ShopContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(AwardContext, self).__init__(fieldsToExclude)
        self._tmanRoleLevel = None
        self._rentExpiryTime = None
        self._rentBattlesLeft = None
        self._rentWinsLeft = None
        return

    def buildItem(self, intCD, tmanCrewLevel=None, rentExpiryTime=None, rentBattles=None, rentWins=None):
        self._tmanRoleLevel = tmanCrewLevel
        self._rentExpiryTime = rentExpiryTime
        self._rentBattlesLeft = rentBattles
        self._rentWinsLeft = rentWins
        return self.itemsCache.items.getItemByCD(int(intCD))

    def getStatsConfiguration(self, item):
        value = super(AwardContext, self).getStatsConfiguration(item)
        value.sellPrice = False
        value.buyPrice = False
        value.unlockPrice = False
        value.inventoryCount = False
        value.vehiclesCount = False
        value.futureRentals = True
        value.isAwardWindow = True
        return value

    def getStatusConfiguration(self, item):
        value = super(AwardContext, self).getStatusConfiguration(item)
        value.isAwardWindow = True
        return value

    def getParamsConfiguration(self, item):
        value = super(AwardContext, self).getParamsConfiguration(item)
        value.simplifiedOnly = True
        value.externalCrewParam = True
        return value

    def getParams(self):
        return {'tmanRoleLevel': self._tmanRoleLevel,
         'rentExpiryTime': self._rentExpiryTime,
         'rentBattlesLeft': self._rentBattlesLeft,
         'rentWinsLeft': self._rentWinsLeft}


class RankedRankContext(ToolTipContext):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, fieldsToExclude=None):
        super(RankedRankContext, self).__init__(TOOLTIP_COMPONENT.RANK, fieldsToExclude)

    def buildItem(self, rankID):
        return self.rankedController.getRank(int(rankID), g_currentVehicle.item)


class InventoryContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(InventoryContext, self).__init__(TOOLTIP_COMPONENT.INVENTORY, fieldsToExclude)

    def buildItem(self, intCD):
        return self.itemsCache.items.getItemByCD(int(intCD))

    def getStatsConfiguration(self, item):
        value = super(InventoryContext, self).getStatsConfiguration(item)
        value.buyPrice = False
        value.minRentPrice = False
        value.unlockPrice = False
        value.sellPrice = True
        value.xp = getattr(item, 'xp', 0) > 0
        value.dailyXP = True
        return value

    def getParamsConfiguration(self, item):
        value = super(InventoryContext, self).getParamsConfiguration(item)
        value.params = gui.GUI_SETTINGS.technicalInfo
        return value


class CarouselContext(InventoryContext):

    def __init__(self, fieldsToExclude=None):
        super(InventoryContext, self).__init__(fieldsToExclude)
        self._component = TOOLTIP_COMPONENT.CAROUSEL

    def getStatusConfiguration(self, item):
        value = super(CarouselContext, self).getStatusConfiguration(item)
        value.checkNotSuitable = True
        return value

    def getStatsConfiguration(self, item):
        value = super(CarouselContext, self).getStatsConfiguration(item)
        value.rentals = True
        return value

    def buildItem(self, intCD):
        return self.itemsCache.items.getItemByCD(int(intCD))


class PotapovQuestsChainContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(PotapovQuestsChainContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)

    def buildItem(self, tileID, chainID):
        return (tileID, chainID)


class PersonalMissionOperationContext(ToolTipContext):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, fieldsToExclude=None):
        super(PersonalMissionOperationContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)

    def buildItem(self, tileID):
        return self._eventsCache.getPersonalMissions().getAllOperations().get(tileID)


class PersonalMissionCampaignContext(ToolTipContext):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, fieldsToExclude=None):
        super(PersonalMissionCampaignContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)

    def buildItem(self, campaignID):
        return self._eventsCache.getPersonalMissions().getAllCampaigns().get(campaignID)


class QuestContext(ToolTipContext):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, fieldsToExclude=None):
        super(QuestContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)

    def buildItem(self, eventID):
        return self.eventsCache.getEvents().get(eventID, None)


class PersonalMissionContext(QuestContext):

    def buildItem(self, eventID, *args, **kwargs):
        quests = self.eventsCache.getPersonalMissions().getAllQuests()
        return quests[eventID] if eventID in quests else None


class BaseHangarParamContext(ToolTipContext):

    def __init__(self, showTitleValue=False):
        super(BaseHangarParamContext, self).__init__(TOOLTIP_COMPONENT.HANGAR)
        self.showTitleValue = showTitleValue

    def getComparator(self):
        return params_helper.idealCrewComparator(g_currentVehicle.item)

    def buildItem(self, *args, **kwargs):
        return g_currentVehicle.item


class HangarParamContext(BaseHangarParamContext):

    def __init__(self):
        super(HangarParamContext, self).__init__(True)
        self.formatters = NO_BONUS_SIMPLIFIED_SCHEME


class PreviewParamContext(HangarParamContext):

    def __init__(self):
        super(PreviewParamContext, self).__init__()
        self.formatters = NO_BONUS_SIMPLIFIED_SCHEME

    def getComparator(self):
        return params_helper.vehiclesComparator(g_currentPreviewVehicle.item, g_currentPreviewVehicle.defaultItem)

    def buildItem(self, *args, **kwargs):
        return g_currentPreviewVehicle.item


class CmpParamContext(HangarParamContext):

    def __init__(self):
        super(CmpParamContext, self).__init__()
        self.formatters = NO_BONUS_SIMPLIFIED_SCHEME

    def getComparator(self):
        return params_helper.vehiclesComparator(_getCmpVehicle(), _getCmpInitialVehicle()[0])


class HangarContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(HangarContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)
        self._slotIdx = 0
        self._vehicle = None
        self._historicalBattleID = -1
        return

    def getVehicle(self):
        return g_currentVehicle.item

    def buildItem(self, intCD, slotIdx=0, historicalBattleID=-1):
        self._slotIdx = int(slotIdx)
        self._vehicle = self.getVehicle()
        self._historicalBattleID = historicalBattleID
        return self.itemsCache.items.getItemByCD(int(intCD))

    def getStatusConfiguration(self, item):
        value = super(HangarContext, self).getStatusConfiguration(item)
        inventoryCheck = item.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES
        isInInventory = inventoryCheck and item.isInInventory
        value.checkBuying = not item.isInstalled(self._vehicle, self._slotIdx) and not isInInventory
        value.vehicle = self._vehicle
        value.slotIdx = self._slotIdx
        return value

    def getStatsConfiguration(self, item):
        value = super(HangarContext, self).getStatsConfiguration(item)
        value.unlockPrice = not item.isUnlocked
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            value.buyPrice = not item.isInInventory
        elif item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            value.buyPrice = True
        else:
            value.buyPrice = not item.isInstalled(self._vehicle, self._slotIdx)
        value.xp = True
        value.dailyXP = True
        value.vehicle = self._vehicle
        value.slotIdx = self._slotIdx
        return value

    def getParamsConfiguration(self, item):
        value = super(HangarContext, self).getParamsConfiguration(item)
        value.params = gui.GUI_SETTINGS.technicalInfo
        value.vehicle = self._vehicle
        value.historicalBattleID = self._historicalBattleID
        return value


class PreviewContext(HangarContext):

    def getVehicle(self):
        return g_currentPreviewVehicle.item


class VehCmpConfigurationContext(HangarContext):

    def getVehicle(self):
        return _getCmpVehicle()


class TankmanHangarContext(HangarContext):

    def buildItem(self, invID):
        return self.itemsCache.items.getTankman(int(invID))


class NotRecruitedTankmanContext(HangarContext):

    def buildItem(self, recruitID):
        return recruit_helper.getRecruitInfo(recruitID)


class TechTreeContext(ShopContext):

    def __init__(self, fieldsToExclude=None):
        super(TechTreeContext, self).__init__(fieldsToExclude)
        self._vehicle = None
        self._node = None
        return

    def buildItem(self, node, parentCD):
        self._vehicle = self.itemsCache.items.getItemByCD(int(parentCD))
        self._node = node
        return self.itemsCache.items.getItemByCD(int(node.id))

    def getStatusConfiguration(self, item):
        value = super(TechTreeContext, self).getStatusConfiguration(item)
        value.checkBuying = not item.isInstalled(self._vehicle) and not item.isInInventory
        value.vehicle = self._vehicle
        value.node = self._node
        value.isResearchPage = True
        return value

    def getStatsConfiguration(self, item):
        value = super(TechTreeContext, self).getStatsConfiguration(item)
        value.inventoryCount = False
        value.vehiclesCount = False
        value.vehicle = self._vehicle
        value.node = self._node
        value.xp = True
        return value

    def getParamsConfiguration(self, item):
        value = super(TechTreeContext, self).getParamsConfiguration(item)
        value.vehicle = self._vehicle
        return value


class VehicleAnnouncementContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(VehicleAnnouncementContext, self).__init__(TOOLTIP_COMPONENT.SHOP, fieldsToExclude)

    def buildItem(self, node, *args, **kwargs):
        return g_techTreeDP.getAnnouncementByCD(int(node.id))


class VehCmpModulesContext(TechTreeContext):

    def buildItem(self, node, parentCD):
        self._vehicle = _getCmpVehicle()
        self._node = node
        return self.itemsCache.items.getItemByCD(int(node.id))

    def getStatusConfiguration(self, item):
        value = super(VehCmpModulesContext, self).getStatusConfiguration(item)
        value.isResearchPage = False
        value.showCustomStates = False
        value.checkBuying = False
        return value


class TechMainContext(HangarContext):

    def __init__(self, fieldsToExclude=None):
        super(TechMainContext, self).__init__(fieldsToExclude)
        self._eqs = tuple()

    def buildItem(self, compact, slotIdx=0, eqs=None):
        if eqs is not None:
            self._eqs = eqs
        return super(TechMainContext, self).buildItem(compact, slotIdx=slotIdx)

    def getStatusConfiguration(self, item):
        value = super(TechMainContext, self).getStatusConfiguration(item)
        value.eqs = self._eqs
        value.checkBuying = True
        return value

    def getStatsConfiguration(self, item):
        value = super(TechMainContext, self).getStatsConfiguration(item)
        value.buyPrice = True
        return value


class PersonalCaseContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(PersonalCaseContext, self).__init__(TOOLTIP_COMPONENT.PERSONAL_CASE, fieldsToExclude)

    def buildItem(self, skillID, tankmanID):
        tankman = self.itemsCache.items.getTankman(int(tankmanID))
        skill = findFirst(lambda x: x.name == skillID, tankman.skills)
        if skill is None:
            skill = getTankmanSkill(skillID, tankman=tankman)
        return skill


class NewSkillContext(PersonalCaseContext):
    SKILL_MOCK = namedtuple('SkillMock', ('header', 'userName', 'shortDescription', 'description', 'count', 'level'))

    def buildItem(self, tankmanID):
        tankman = self.itemsCache.items.getTankman(int(tankmanID))
        skillsCount, lastSkillLevel = (0, 0)
        if tankman is not None:
            skillsCount, lastSkillLevel = tankman.newSkillCount
        header = text_styles.main(TOOLTIPS.BUYSKILL_HEADER)
        if skillsCount > 1 or lastSkillLevel > 0:
            header = text_styles.highTitle(TOOLTIPS.BUYSKILL_HEADER)
        return self.SKILL_MOCK(header, makeString('#tooltips:personal_case/skills/new/header'), makeString('#tooltips:personal_case/skills/new/body'), makeString('#tooltips:personal_case/skills/new/body'), skillsCount, lastSkillLevel)


class ProfileContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(ProfileContext, self).__init__(TOOLTIP_COMPONENT.PROFILE, fieldsToExclude)
        self._dossier = None
        self._dossierType = None
        self._isCurrentUserDossier = True
        self._vehicleLevel = 0
        self._arenaType = ARENA_GUI_TYPE.RANDOM
        return

    def buildItem(self, dossierType, dossierCompDescr, block, name, isRare, isUserDossier, vehicleLevel, arenaType):
        dossier = loadDossier(dossierCompDescr)
        if dossierType == constants.DOSSIER_TYPE.VEHICLE:
            self._component = TOOLTIP_COMPONENT.PROFILE_VEHICLE
        self._dossier = dossier
        self._dossierType = dossierType
        self._isCurrentUserDossier = isUserDossier
        self._vehicleLevel = vehicleLevel
        self._arenaType = arenaType
        if block == ACHIEVEMENT_BLOCK.RARE:
            name = int(name)
        return dossier.getTotalStats().getAchievement((block, name))

    def getParamsConfiguration(self, item):
        value = super(ProfileContext, self).getParamsConfiguration(item)
        value.dossier = self._dossier
        value.dossierType = self._dossierType
        value.isCurrentUserDossier = self._isCurrentUserDossier
        value.vehicleLevel = self._vehicleLevel
        value.arenaType = self._arenaType
        return value


class BattleResultContext(ProfileContext):

    def __init__(self, fieldsToExclude=None):
        super(BattleResultContext, self).__init__(fieldsToExclude)
        self._component = TOOLTIP_COMPONENT.PROFILE

    def buildItem(self, block, name, value=0, customData=None, vehicleLevel=0, arenaType=ARENA_GUI_TYPE.RANDOM):
        self._vehicleLevel = vehicleLevel
        self._arenaType = arenaType
        factory = factories.getAchievementFactory((block, name))
        return factory.create(value=value) if factory is not None else None

    def getParamsConfiguration(self, item):
        value = super(BattleResultContext, self).getParamsConfiguration(item)
        value.checkAchievementExistence = False
        value.vehicleLevel = self._vehicleLevel
        value.arenaType = self._arenaType
        return value


class BattleResultMarksOnGunContext(BattleResultContext):

    def buildItem(self, block, name, value=0, customData=None, vehicleLevel=0, arenaType=ARENA_GUI_TYPE.RANDOM):
        self._vehicleLevel = vehicleLevel
        self._arenaType = arenaType
        item = super(BattleResultMarksOnGunContext, self).buildItem(block, name, value, customData, vehicleLevel, arenaType)
        if item is not None and customData is not None:
            damageRating, vehNationID = customData
            item.setVehicleNationID(vehNationID)
            item.setDamageRating(damageRating)
            return item
        else:
            return


class BattleResultMarkOfMasteryContext(BattleResultContext):

    def buildItem(self, block, name, value=0, customData=None, vehicleLevel=0, arenaType=ARENA_GUI_TYPE.RANDOM):
        self._vehicleLevel = vehicleLevel
        self._arenaType = arenaType
        item = super(BattleResultMarkOfMasteryContext, self).buildItem(block, name, value, customData, vehicleLevel, arenaType)
        if item is not None and customData is not None:
            prevMarkOfMastery, compDescr = customData
            item.setPrevMarkOfMastery(prevMarkOfMastery)
            item.setCompDescr(compDescr)
        return item


class VehicleEliteBonusContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(VehicleEliteBonusContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)

    def buildItem(self, bonusId):
        return bonusId


class VehicleHistoricalReferenceContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(VehicleHistoricalReferenceContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)

    def buildItem(self, *args, **kwargs):
        return g_currentPreviewVehicle.item


class FinalStatisticContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(FinalStatisticContext, self).__init__(TOOLTIP_COMPONENT.FINAL_STATISTIC, fieldsToExclude)


class CyberSportUnitContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(CyberSportUnitContext, self).__init__(TOOLTIP_COMPONENT.CYBER_SPORT_UNIT, fieldsToExclude)


class FortificationContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(FortificationContext, self).__init__(TOOLTIP_COMPONENT.FORTIFICATIONS, fieldsToExclude)


class ReserveContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(ReserveContext, self).__init__(TOOLTIP_COMPONENT.RESERVE, fieldsToExclude)


class ClanProfileFortBuildingContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(ClanProfileFortBuildingContext, self).__init__(TOOLTIP_COMPONENT.CLAN_PROFILE, fieldsToExclude)


class ContactContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(ContactContext, self).__init__(TOOLTIP_COMPONENT.CONTACT, fieldsToExclude)


class BattleConsumableContext(FortificationContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def buildItem(self, intCD):
        return self.itemsCache.items.getItemByCD(int(intCD))


class HangarTutorialContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(HangarTutorialContext, self).__init__(TOOLTIP_COMPONENT.HANGAR_TUTORIAL, fieldsToExclude)


class FortPopoverDefResProgressContext(FortificationContext):
    pass


class SettingsMinimapContext(ToolTipContext):
    pass


class SquadRestrictionContext(ToolTipContext):
    pass


class TechCustomizationContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(TechCustomizationContext, self).__init__(TOOLTIP_COMPONENT.TECH_CUSTOMIZATION, fieldsToExclude)


class BoosterContext(ToolTipContext):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, fieldsToExclude=None):
        super(BoosterContext, self).__init__(TOOLTIP_COMPONENT.BOOSTER, fieldsToExclude)

    def getStatsConfiguration(self, booster):
        return BoosterStatsConfiguration()

    def buildItem(self, boosterID):
        return self.goodiesCache.getBooster(boosterID)


class ShopBoosterContext(BoosterContext):

    def getStatsConfiguration(self, booster):
        value = super(ShopBoosterContext, self).getStatsConfiguration(booster)
        value.buyPrice = True
        return value


class QuestsBoosterContext(BoosterContext):

    def getStatsConfiguration(self, booster):
        value = super(QuestsBoosterContext, self).getStatsConfiguration(booster)
        value.quests = True
        return value


class BoosterStatsConfiguration(object):
    __slots__ = ('buyPrice', 'quests', 'activeState')

    def __init__(self):
        self.buyPrice = False
        self.quests = False
        self.activeState = True


class HangarServerStatusContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(HangarServerStatusContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)


class ShopBattleBoosterContext(HangarContext):

    def getStatsConfiguration(self, item):
        value = super(ShopBattleBoosterContext, self).getStatsConfiguration(item)
        value.vehicle = None
        return value

    def getStatusConfiguration(self, item):
        value = super(ShopBattleBoosterContext, self).getStatusConfiguration(item)
        value.vehicle = None
        return value


class InventoryBattleBoosterContext(ShopBattleBoosterContext):

    def getStatsConfiguration(self, item):
        value = super(InventoryBattleBoosterContext, self).getStatsConfiguration(item)
        value.buyPrice = False
        return value

    def getStatusConfiguration(self, item):
        value = super(InventoryBattleBoosterContext, self).getStatusConfiguration(item)
        value.checkBuying = False
        return value


class AwardBattleBoosterContext(InventoryBattleBoosterContext):

    def getStatsConfiguration(self, item):
        value = super(AwardBattleBoosterContext, self).getStatsConfiguration(item)
        value.isAwardWindow = True
        value.inventoryCount = False
        value.vehiclesCount = False
        return value

    def getStatusConfiguration(self, item):
        value = super(AwardBattleBoosterContext, self).getStatusConfiguration(item)
        value.isAwardWindow = True
        return value

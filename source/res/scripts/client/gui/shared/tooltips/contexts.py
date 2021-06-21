# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/contexts.py
from collections import namedtuple
import typing
import constants
import gui
import nations
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from constants import ARENA_BONUS_TYPE, ARENA_GUI_TYPE
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui.Scaleform.daapi.view.lobby.tank_setup.ammunition_setup_vehicle import g_tankSetupVehicle
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_vehicle import g_postProgressionVehicle
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift
from gui.server_events import recruit_helper
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getTankmanSkill, SabatonTankmanSkill, TankmanSkill, OffspringTankmanSkill
from gui.shared.gui_items.dossier import factories, loadDossier
from gui.shared.items_parameters import params_helper, bonus_helper
from gui.shared.items_parameters.formatters import NO_BONUS_SIMPLIFIED_SCHEME
from gui.shared.tooltips import TOOLTIP_COMPONENT
from gui.shared.utils.requesters.blueprints_requester import getFragmentNationID
from helpers import dependency
from helpers.i18n import makeString
from shared_utils import findFirst, first
from skeletons.gui.game_control import IRankedBattlesController, IBattlePassController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from account_helpers.offers.events_data import OfferGift, OfferEventData
    from gui.shared.gui_items.dossier.stats import AccountTotalStatsBlock

def _getCmpVehicle():
    return cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicle()


def _getCmpInitialVehicle():
    return cmp_helpers.getCmpConfiguratorMainView().getInitialVehicleData()


class StatsConfiguration(object):
    __slots__ = ('vehicle', 'sellPrice', 'buyPrice', 'unlockPrice', 'inventoryCount', 'vehiclesCount', 'node', 'xp', 'dailyXP', 'minRentPrice', 'restorePrice', 'rentals', 'slotIdx', 'futureRentals', 'isAwardWindow', 'showBonus', 'showRankedBonusBattle', 'showCompatibles', 'withSlots', 'isStaticInfoOnly')

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
        self.showRankedBonusBattle = False
        self.slotIdx = 0
        self.isAwardWindow = False
        self.showBonus = True
        self.showCompatibles = False
        self.withSlots = False
        self.isStaticInfoOnly = False
        return


class StatusConfiguration(object):
    __slots__ = ('vehicle', 'slotIdx', 'eqs', 'checkBuying', 'node', 'isAwardWindow', 'isResearchPage', 'checkNotSuitable', 'showCustomStates', 'useWhiteBg', 'withSlots', 'isCompare')

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
        self.useWhiteBg = True
        self.withSlots = False
        self.isCompare = False
        return


class ParamsConfiguration(object):
    __slots__ = ('vehicle', 'params', 'crew', 'eqs', 'devices', 'dossier', 'dossierType', 'isCurrentUserDossier', 'historicalBattleID', 'checkAchievementExistence', 'simplifiedOnly', 'externalCrewParam', 'vehicleLevel', 'arenaType', 'colorless')

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
        self.colorless = False
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


class EmptyOptDeviceSlotContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(EmptyOptDeviceSlotContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)
        self._slotIdx = None
        self._vehicle = None
        return

    def buildItem(self, slotIdx, vehicle=None):
        self._slotIdx = int(slotIdx)
        if vehicle is None:
            self._vehicle = self.__getVehicle()
        else:
            self._vehicle = vehicle
        return

    def getStatusConfiguration(self, item):
        value = super(EmptyOptDeviceSlotContext, self).getStatusConfiguration(item)
        value.vehicle = self._vehicle
        value.slotIdx = self._slotIdx
        return value

    def __getVehicle(self):
        return g_currentVehicle.item


class DefaultContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(DefaultContext, self).__init__(TOOLTIP_COMPONENT.SHOP, fieldsToExclude)

    def buildItem(self, intCD):
        return self.itemsCache.items.getItemByCD(int(intCD))

    def getStatusConfiguration(self, item):
        value = super(DefaultContext, self).getStatusConfiguration(item)
        value.checkBuying = True
        value.showCustomStates = True
        return value

    def getStatsConfiguration(self, item):
        value = super(DefaultContext, self).getStatsConfiguration(item)
        value.xp = False
        value.dailyXP = False
        return value

    def getParamsConfiguration(self, item):
        value = super(DefaultContext, self).getParamsConfiguration(item)
        value.params = gui.GUI_SETTINGS.technicalInfo
        value.eqs = False
        value.devices = False
        return value


class BadgeContext(ToolTipContext):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(BadgeContext, self).__init__(TOOLTIP_COMPONENT.BADGE, fieldsToExclude)

    def getParamsConfiguration(self, badge):
        return BadgeParamsConfiguration()

    def buildItem(self, badgeID):
        return self.__itemsCache.items.getBadges().get(int(badgeID))


class ReferralProgramBadgeContext(BadgeContext):

    def getParamsConfiguration(self, badge):
        value = super(ReferralProgramBadgeContext, self).getParamsConfiguration(badge)
        value.showVehicle = False
        return value


class AwardContext(DefaultContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(AwardContext, self).__init__(fieldsToExclude)
        self._tmanRoleLevel = None
        self._rentExpiryTime = None
        self._rentBattlesLeft = None
        self._rentWinsLeft = None
        self._rentSeason = None
        self._isSeniority = False
        return

    def buildItem(self, intCD, tmanCrewLevel=None, rentExpiryTime=None, rentBattles=None, rentWins=None, rentSeason=None, isSeniority=False):
        self._tmanRoleLevel = tmanCrewLevel
        self._rentExpiryTime = rentExpiryTime
        self._rentBattlesLeft = rentBattles
        self._rentWinsLeft = rentWins
        self._rentSeason = rentSeason
        self._isSeniority = isSeniority
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
         'rentWinsLeft': self._rentWinsLeft,
         'rentSeason': self._rentSeason,
         'isSeniority': self._isSeniority}


class ShopContext(AwardContext):

    def getStatsConfiguration(self, item):
        value = super(ShopContext, self).getStatsConfiguration(item)
        value.inventoryCount = True
        value.vehiclesCount = True
        return value


class RankedRankContext(ToolTipContext):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, fieldsToExclude=None):
        super(RankedRankContext, self).__init__(TOOLTIP_COMPONENT.RANK, fieldsToExclude)

    def buildItem(self, rankID):
        return self.rankedController.getRank(int(rankID))


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
        value.xp = True
        value.dailyXP = True
        return value

    def getParamsConfiguration(self, item):
        value = super(InventoryContext, self).getParamsConfiguration(item)
        value.params = gui.GUI_SETTINGS.technicalInfo
        return value


class ModuleInfoContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, fieldsToExclude=None):
        super(ModuleInfoContext, self).__init__(TOOLTIP_COMPONENT.MODULE_INFO, fieldsToExclude)
        self.__vehDescr = None
        return

    def buildItem(self, intCD, vehDescr):
        self.__vehDescr = vehDescr
        return self.itemsCache.items.getItemByCD(int(intCD))

    def getStatusConfiguration(self, item):
        value = super(ModuleInfoContext, self).getStatusConfiguration(item)
        value.useWhiteBg = False
        return value

    def getStatsConfiguration(self, item):
        value = super(ModuleInfoContext, self).getStatsConfiguration(item)
        value.vehicle = None
        value.sellPrice = False
        value.buyPrice = False
        value.minRentPrice = False
        value.restorePrice = False
        value.rentals = False
        value.futureRentals = False
        value.unlockPrice = False
        value.inventoryCount = False
        value.vehiclesCount = False
        value.node = None
        value.xp = False
        value.dailyXP = False
        value.showCompatibles = True
        value.isStaticInfoOnly = True
        return value

    def getParamsConfiguration(self, item):
        value = super(ModuleInfoContext, self).getParamsConfiguration(item)
        value.params = gui.GUI_SETTINGS.technicalInfo
        if self.__vehDescr:
            value.vehicle = self.itemsFactory.createVehicle(self.__vehDescr.makeCompactDescr())
        value.colorless = True
        return value


class CarouselContext(InventoryContext):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, fieldsToExclude=None):
        super(InventoryContext, self).__init__(fieldsToExclude)
        self._component = TOOLTIP_COMPONENT.CAROUSEL

    def getStatusConfiguration(self, item):
        value = super(CarouselContext, self).getStatusConfiguration(item)
        value.checkNotSuitable = True
        return value

    def getStatsConfiguration(self, item):
        value = super(CarouselContext, self).getStatsConfiguration(item)
        if self.__rankedController.isRankedPrbActive():
            suitResult = self.__rankedController.isSuitableVehicle(item)
            hasRankedBonus = self.__rankedController.hasVehicleRankedBonus(item.intCD)
            value.showRankedBonusBattle = hasRankedBonus and suitResult is None
        value.rentals = True
        value.buyPrice = True
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
        self.isApproximately = False
        self.showTitleValue = showTitleValue

    def getComparator(self):
        return params_helper.idealCrewComparator(g_currentVehicle.item)

    def buildItem(self, *args, **kwargs):
        return g_currentVehicle.item

    def getBonusExtractor(self, vehicle, bonuses, paramName):
        return bonus_helper.BonusExtractor(vehicle, bonuses, paramName)


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


class TankSetupParamContext(HangarParamContext):

    def __init__(self):
        super(TankSetupParamContext, self).__init__()
        self.formatters = NO_BONUS_SIMPLIFIED_SCHEME

    def getComparator(self):
        return params_helper.idealCrewComparator(g_tankSetupVehicle.item)

    def buildItem(self, *args, **kwargs):
        return g_tankSetupVehicle.item

    def getBonusExtractor(self, vehicle, bonuses, paramName):
        return bonus_helper.TankSetupBonusExtractor(vehicle, bonuses, paramName)


class PostProgressionParamContext(TankSetupParamContext):

    def __init__(self):
        super(PostProgressionParamContext, self).__init__()
        self.isApproximately = True

    def getComparator(self):
        return params_helper.tankSetupVehiclesComparator(g_postProgressionVehicle.item, g_postProgressionVehicle.defaultItem, withBonuses=g_postProgressionVehicle.item.isInInventory)

    def buildItem(self, *args, **kwargs):
        return g_postProgressionVehicle.item

    def getBonusExtractor(self, vehicle, bonuses, paramName):
        return bonus_helper.PostProgressionBonusExtractor(vehicle, bonuses, paramName)


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

    def buildItem(self, intCD, slotIdx=0, historicalBattleID=-1, vehicle=None):
        self._slotIdx = int(slotIdx)
        if vehicle is None:
            self._vehicle = self.getVehicle()
        else:
            self._vehicle = vehicle
        self._historicalBattleID = historicalBattleID
        return self.itemsCache.items.getItemByCD(int(intCD))

    def getStatusConfiguration(self, item):
        value = super(HangarContext, self).getStatusConfiguration(item)
        inventoryCheck = item.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES
        isInInventory = inventoryCheck and item.isInInventory
        value.checkBuying = self._vehicle is not None and not item.isInstalled(self._vehicle, self._slotIdx) and not isInInventory
        value.vehicle = self._vehicle
        value.slotIdx = self._slotIdx
        return value

    def getStatsConfiguration(self, item):
        value = super(HangarContext, self).getStatsConfiguration(item)
        value.unlockPrice = not item.isUnlocked
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            value.buyPrice = not item.isInInventory
        elif item.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            value.buyPrice = True
        elif self._vehicle is not None:
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


class HangarCardContext(HangarContext):

    def getStatusConfiguration(self, item):
        value = super(HangarCardContext, self).getStatusConfiguration(item)
        inventoryCheck = item.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES
        isInInventory = inventoryCheck and item.isInInventory
        value.checkBuying = not isInInventory
        return value

    def getStatsConfiguration(self, item):
        value = super(HangarCardContext, self).getStatsConfiguration(item)
        value.buyPrice = True
        return value


class HangarSlotContext(HangarContext):

    def getStatsConfiguration(self, item):
        value = super(HangarSlotContext, self).getStatsConfiguration(item)
        value.withSlots = True
        return value

    def getStatusConfiguration(self, item):
        value = super(HangarSlotContext, self).getStatusConfiguration(item)
        value.withSlots = True
        return value


class NationChangeHangarContext(HangarContext):

    def buildItem(self, vehCD, intCD):
        self._vehicle = self.itemsCache.items.getItemByCD(int(vehCD))
        return self.itemsCache.items.getItemByCD(int(intCD))


class PreviewContext(HangarContext):

    def getVehicle(self):
        return g_currentPreviewVehicle.item


class VehCmpConfigurationContext(HangarContext):

    def getVehicle(self):
        return _getCmpVehicle()

    def getStatusConfiguration(self, item):
        value = super(VehCmpConfigurationContext, self).getStatusConfiguration(item)
        value.isCompare = True
        return value

    def getStatsConfiguration(self, item):
        value = super(VehCmpConfigurationContext, self).getStatsConfiguration(item)
        value.buyPrice = True
        return value


class VehCmpConfigurationSlotContext(VehCmpConfigurationContext):

    def getStatsConfiguration(self, item):
        value = super(VehCmpConfigurationSlotContext, self).getStatsConfiguration(item)
        value.withSlots = True
        return value

    def getStatusConfiguration(self, item):
        value = super(VehCmpConfigurationSlotContext, self).getStatusConfiguration(item)
        value.withSlots = True
        return value


class TankmanHangarContext(HangarContext):

    def buildItem(self, invID):
        return self.itemsCache.items.getTankman(int(invID))


class NotRecruitedTankmanContext(HangarContext):

    def buildItem(self, recruitID):
        return recruit_helper.getRecruitInfo(recruitID)


class TechTreeContext(DefaultContext):

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
        value.sellPrice = True
        return value

    def getParamsConfiguration(self, item):
        value = super(TechTreeContext, self).getParamsConfiguration(item)
        value.vehicle = self._vehicle
        return value


class ModuleContext(TechTreeContext):

    def getStatsConfiguration(self, item):
        value = super(ModuleContext, self).getStatsConfiguration(item)
        value.sellPrice = False
        return value


class BlueprintContext(ToolTipContext):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(BlueprintContext, self).__init__(TOOLTIP_COMPONENT.BLUEPRINT, fieldsToExclude)
        self.__blueprintCD = None
        return

    def buildItem(self, cd=None):
        self.__blueprintCD = cd
        return self.__blueprintCD

    def getVehicleBlueprintData(self, vehicleCD=None):
        if vehicleCD is None and self.__blueprintCD is None:
            return
        else:
            vehicleCD = int(self.__blueprintCD if vehicleCD is None else vehicleCD)
            vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
            if vehicle is None:
                return
            blueprintData = self.__itemsCache.items.blueprints.getBlueprintData(vehicleCD, vehicle.level)
            convertibleCount = self.__itemsCache.items.blueprints.getConvertibleFragmentCount(vehicleCD, vehicle.level)
            return (vehicle, blueprintData, convertibleCount)

    def getDiscountValues(self, vehicle=None):
        if vehicle is None and self.__blueprintCD is None:
            return
        else:
            if vehicle is None:
                vehicle = self.__itemsCache.items.getItemByCD(int(self.__blueprintCD))
            newCost, discount, fullCost = g_techTreeDP.getOldAndNewCost(vehicle.intCD, vehicle.level)
            xpDiscount = fullCost - newCost
            return (discount, xpDiscount)

    def getFragmentDiscounts(self, vehicle=None):
        if vehicle is None and self.__blueprintCD is None:
            return
        else:
            if vehicle is None:
                vehicle = self.__itemsCache.items.getItemByCD(int(self.__blueprintCD))
            _, _, fullUnlockPrice = g_techTreeDP.getOldAndNewCost(vehicle.intCD, vehicle.level)
            return self.__itemsCache.items.blueprints.getFragmentDiscountAndCost(vehicle.intCD, vehicle.level, fullUnlockPrice)

    def getFragmentConvertData(self, vLevel=None):
        if vLevel is None and self.__blueprintCD is None:
            return
        else:
            if vLevel is None:
                vLevel = self.__itemsCache.items.getItemByCD(int(self.__blueprintCD)).level
            reqNational, reqIntel = self.__itemsCache.items.blueprints.getRequiredIntelligenceAndNational(vLevel)
            return (reqIntel, reqNational)

    def getFragmentData(self, fragmentCD=None):
        if fragmentCD is None and self.__blueprintCD is None:
            return
        else:
            fragmentCD = self.__blueprintCD if fragmentCD is None else fragmentCD
            fragmentType = getFragmentType(fragmentCD)
            nation = None
            alliance = None
            if fragmentType in (BlueprintTypes.NATIONAL, BlueprintTypes.VEHICLE):
                nation = nations.NAMES[getFragmentNationID(fragmentCD)]
                alliance = nations.ALLIANCES_TAGS_ORDER[nations.NATION_TO_ALLIANCE_IDS_MAP[nations.INDICES[nation]]]
            return (fragmentType, nation, alliance)

    def getUniversalCount(self, vehicleCD=None):
        return self.__itemsCache.items.blueprints.getIntelligenceCount() if vehicleCD is None else self.__itemsCache.items.blueprints.getNationalFragments(vehicleCD)

    def getBlueprintLayout(self, vehicle=None):
        if vehicle is None and self.__blueprintCD is None:
            return
        else:
            if vehicle is None:
                vehicle = self.__itemsCache.items.getItemByCD(int(self.__blueprintCD))
            return self.__itemsCache.items.blueprints.getLayout(vehicle.intCD, vehicle.level)

    def getAllianceNationFragmentsData(self, vehicle):
        bpRequester = self.__itemsCache.items.blueprints
        nationalRequiredOptions = bpRequester.getNationalRequiredOptions(vehicle.intCD, vehicle.level)
        nationalAllianceFragments = bpRequester.getNationalAllianceFragments(vehicle.intCD, vehicle.level)
        return (nationalRequiredOptions, nationalAllianceFragments)


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

    def getStatsConfiguration(self, item):
        value = super(VehCmpModulesContext, self).getStatsConfiguration(item)
        value.buyPrice = False
        value.sellPrice = False
        value.unlockPrice = False
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


class PreviewCaseContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(PreviewCaseContext, self).__init__(TOOLTIP_COMPONENT.PERSONAL_CASE, fieldsToExclude)

    def buildItem(self, skillID):
        if skillID == 'sabaton_brotherhood':
            return SabatonTankmanSkill('brotherhood')
        return OffspringTankmanSkill('brotherhood') if skillID == 'offspring_brotherhood' else TankmanSkill(skillID)


class CrewSkinContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(CrewSkinContext, self).__init__(TOOLTIP_COMPONENT.PERSONAL_CASE, fieldsToExclude)

    def buildItem(self, skinID):
        return self.itemsCache.items.getCrewSkin(skinID)


class CrewSkinTankmanContext(ToolTipContext):
    TankmanContext = namedtuple('SkinTankmnaContext', ('tankman', 'crewSkin'))
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(CrewSkinTankmanContext, self).__init__(TOOLTIP_COMPONENT.PERSONAL_CASE, fieldsToExclude)

    def buildItem(self, tankmanID, skinID):
        return self.TankmanContext(self.itemsCache.items.getTankman(tankmanID), self.itemsCache.items.getCrewSkin(skinID))


class CrewBookContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(CrewBookContext, self).__init__(TOOLTIP_COMPONENT.PERSONAL_CASE, fieldsToExclude)

    def buildItem(self, bookCD):
        return self.itemsCache.items.getItemByCD(bookCD)


class CrewBookVehicleContext(ToolTipContext):
    VehicleContext = namedtuple('BookVehicleContext', 'vehicle')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(CrewBookVehicleContext, self).__init__(TOOLTIP_COMPONENT.CREW_BOOK, fieldsToExclude)

    def buildItem(self, vehicleID):
        return self.VehicleContext(self.itemsCache.items.getVehicle(vehicleID))


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

    def buildItem(self, dossierType, dossierCompDescr, block, name, isRare, isUserDossier=True, vehicleLevel=0, arenaType=ARENA_BONUS_TYPE.REGULAR):
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
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, fieldsToExclude=None):
        super(BattleResultContext, self).__init__(fieldsToExclude)
        self._component = TOOLTIP_COMPONENT.PROFILE

    def buildItem(self, block, name, value=0, customData=None, vehicleLevel=0, arenaType=ARENA_GUI_TYPE.RANDOM):
        self._vehicleLevel = vehicleLevel
        self._arenaType = arenaType
        totalStats = self.__itemsCache.items.getAccountDossier().getTotalStats()
        if totalStats.isAchievementInLayout((block, name)):
            item = totalStats.getAchievement((block, name))
            if item is not None:
                return item
        factory = factories.getAchievementFactory((block, name))
        return factory.create(value=value) if factory is not None else None

    def getParamsConfiguration(self, item):
        value = super(BattleResultContext, self).getParamsConfiguration(item)
        value.checkAchievementExistence = False
        value.vehicleLevel = self._vehicleLevel
        value.arenaType = self._arenaType
        return value


class ShopAchievementContext(BattleResultContext):

    def buildItem(self, aID, *args):
        block, achieveName = DB_ID_TO_RECORD[aID]
        return super(ShopAchievementContext, self).buildItem(block, achieveName)


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

    def getStatsConfiguration(self, item):
        value = super(TechCustomizationContext, self).getStatsConfiguration(item)
        value.sellPrice = True
        return value

    def getParams(self):
        return {'showBonus': True}


class SessionStatsContext(ToolTipContext):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(SessionStatsContext, self).__init__(TOOLTIP_COMPONENT.SESSION_STATS)

    def buildItem(self, intCD):
        return self.itemsCache.items.getItemByCD(int(intCD))


class ShopCustomizationContext(TechCustomizationContext):

    def getStatsConfiguration(self, item):
        value = super(ShopCustomizationContext, self).getStatsConfiguration(item)
        value.sellPrice = False
        value.buyPrice = False
        value.inventoryCount = True
        value.showBonus = False
        return value


class BoosterInfoContext(ToolTipContext):
    _goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, fieldsToExclude=None):
        super(BoosterInfoContext, self).__init__(TOOLTIP_COMPONENT.BOOSTER, fieldsToExclude)

    def getStatsConfiguration(self, booster):
        return BoosterStatsConfiguration()

    def buildItem(self, boosterID):
        return self._goodiesCache.getBooster(boosterID)


class DemountKitContext(ToolTipContext):
    _goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, fieldsToExclude=None):
        super(DemountKitContext, self).__init__(TOOLTIP_COMPONENT.DEMOUNT_KIT, fieldsToExclude)

    def buildItem(self, demountKitID):
        return self._goodiesCache.getDemountKit(demountKitID)


class BoosterContext(BoosterInfoContext):

    def getStatsConfiguration(self, booster):
        value = super(BoosterContext, self).getStatsConfiguration(booster)
        value.buyPrice = True
        return value


class QuestsBoosterContext(BoosterInfoContext):

    def getStatsConfiguration(self, booster):
        value = super(QuestsBoosterContext, self).getStatsConfiguration(booster)
        value.quests = True
        return value


class ShopBoosterContext(BoosterInfoContext):

    def getStatsConfiguration(self, booster):
        value = super(ShopBoosterContext, self).getStatsConfiguration(booster)
        value.activateInfo = True
        value.activeState = False
        value.inventoryCount = True
        return value


class ClanReserveContext(BoosterInfoContext):

    def buildItem(self, boosterID):
        return self._goodiesCache.getClanReserves().get(boosterID)

    def getStatsConfiguration(self, booster):
        boosterStatsConfig = super(ClanReserveContext, self).getStatsConfiguration(booster)
        boosterStatsConfig.activeState = False
        return boosterStatsConfig


class BoosterStatsConfiguration(object):
    __slots__ = ('buyPrice', 'inventoryCount', 'quests', 'activeState', 'effectTime', 'activateInfo', 'dueDate')

    def __init__(self):
        self.buyPrice = False
        self.inventoryCount = False
        self.quests = False
        self.activeState = True
        self.effectTime = True
        self.activateInfo = False
        self.dueDate = False


class BadgeParamsConfiguration(object):
    __slots__ = ('showVehicle',)

    def __init__(self):
        self.showVehicle = True


class HangarServerStatusContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(HangarServerStatusContext, self).__init__(TOOLTIP_COMPONENT.HANGAR, fieldsToExclude)


class BattleBoosterContext(HangarContext):

    def getStatsConfiguration(self, item):
        value = super(BattleBoosterContext, self).getStatsConfiguration(item)
        value.vehicle = None
        return value

    def getStatusConfiguration(self, item):
        value = super(BattleBoosterContext, self).getStatusConfiguration(item)
        value.vehicle = None
        return value


class InventoryBattleBoosterContext(BattleBoosterContext):

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


class ShopBattleBoosterContext(AwardBattleBoosterContext):

    def getStatsConfiguration(self, item):
        value = super(ShopBattleBoosterContext, self).getStatsConfiguration(item)
        value.inventoryCount = True
        value.vehiclesCount = True
        return value


class DogTagInfoContext(ToolTipContext):

    def __init__(self, fieldsToExclude=None):
        super(DogTagInfoContext, self).__init__(TOOLTIP_COMPONENT.FINAL_STATISTIC, fieldsToExclude)


class BattlePassGiftTokenContext(ToolTipContext):
    __slots__ = ('__hasOffer',)
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self):
        super(BattlePassGiftTokenContext, self).__init__(TOOLTIP_COMPONENT.BATTLE_PASS)
        self.__hasOffer = True

    def buildItem(self, tokenID, **kwargs):
        self.__hasOffer = True
        result = []
        shortName = tokenID.split(':')[2]
        offerToken = getOfferTokenByGift(tokenID)
        offer = self.__offersProvider.getOfferByToken(offerToken)
        if offer is None:
            self.__hasOffer = False
            return result
        else:
            if shortName in ('brochure_gift', 'guide_gift'):
                gift = first(offer.getAllGifts())
                if gift is not None:
                    result.append(gift.bonus.displayedItem.getXP())
            else:
                for gift in offer.getAllGifts():
                    result.append(gift.title)

            return result

    def getParams(self):
        return {'isOfferEnabled': self.__battlePassController.isOfferEnabled() and self.__hasOffer}

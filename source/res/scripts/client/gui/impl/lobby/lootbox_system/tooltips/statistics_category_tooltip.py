# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/tooltips/statistics_category_tooltip.py
import logging
from typing import TYPE_CHECKING
from frameworks.wulf import ViewSettings
from gui.goodies.goodie_items import Booster, DemountKit, RecertificationForm
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.rewards_categories_model import Type
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.statistics_category_tooltip_bonus_model import StatisticsCategoryTooltipBonusModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.statistics_category_tooltip_view_model import StatisticsCategoryTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.common import LOOTBOX_RANDOM_NATIONAL_BLUEPRINT
from gui.lootbox_system.utils import getSingleVehicleCDForCustomization
from gui.server_events.bonuses import BlueprintsBonusSubtypes, blueprintBonusFactory, LootBoxRandomNationalBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES, getItemTypeID
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Iterable, List, Tuple
    from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
    from gui.goodies.goodie_items import _Goodie
    from gui.server_events.recruit_helper import _TokenRecruitInfo
    from gui.shared.gui_items.artefacts import Equipment
    from gui.shared.gui_items.customization.c11n_items import Customization, Style
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

class StatisticsCategoryTooltipView(ViewImpl):
    __slots__ = ('__bonusesCategory',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __customization = dependency.descriptor(ICustomizationService)
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, bonusesCategory):
        settings = ViewSettings(R.views.lobby.lootbox_system.tooltips.StatisticsCategoryTooltipView())
        settings.model = StatisticsCategoryTooltipViewModel()
        super(StatisticsCategoryTooltipView, self).__init__(settings)
        self.__bonusesCategory = Type(bonusesCategory)

    @property
    def viewModel(self):
        return super(StatisticsCategoryTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(StatisticsCategoryTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vmTX:
            vmTX.setEventName(self.__lootBoxes.eventName)
            vmTX.setBonusesCategory(self.__bonusesCategory.value)
            self.__setBonuses(model=vmTX)

    @replaceNoneKwargsModel
    def __setBonuses(self, model=None):
        model.bonuses.clearItems()
        rewards, _ = self.__lootBoxes.getStatistics()
        _PACK_REWARDS[self.__bonusesCategory](rewards, model)
        model.bonuses.invalidate()


def _packVehicles(rewards, model):
    totalCompensatedCount = 0
    vehicles = []
    for vehicle, compensatedCount in _iterVehicles(rewards):
        if not compensatedCount:
            vehicles.append(vehicle)
        totalCompensatedCount += compensatedCount

    vehicles.sort(key=lambda v: v.level, reverse=True)
    model.setCompensatedCount(totalCompensatedCount)
    for vehicle in vehicles:
        bonusModel = StatisticsCategoryTooltipBonusModel()
        _setVehicleInfoModel(bonusModel.vehicle, vehicle)
        model.bonuses.addViewModel(bonusModel)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _pack3DStyles(rewards, model, itemsCache=None):
    totalCompensatedCount = 0
    suitable = []
    for style, compensatedCount in _iter3DStyles(rewards):
        if not compensatedCount:
            vehicleCD = getSingleVehicleCDForCustomization(style)
            if vehicleCD is not None:
                vehicle = itemsCache.items.getItemByCD(vehicleCD)
                suitable.append((style, vehicle))
        totalCompensatedCount += compensatedCount

    suitable.sort(key=lambda s: s[1].level, reverse=True)
    model.setCompensatedCount(totalCompensatedCount)
    for style, vehicle in suitable:
        bonusModel = StatisticsCategoryTooltipBonusModel()
        bonusModel.setLabel(style.userName)
        _setVehicleInfoModel(bonusModel.vehicle, vehicle)
        model.bonuses.addViewModel(bonusModel)

    return


def _pack2DStyles(rewards, model):
    totalCompensatedCount = 0
    for style, compensatedCount in _iter2DStyles(rewards):
        if not compensatedCount:
            bonusModel = StatisticsCategoryTooltipBonusModel()
            bonusModel.setLabel(style.userName)
            model.bonuses.addViewModel(bonusModel)
        totalCompensatedCount += compensatedCount

    model.setCompensatedCount(totalCompensatedCount)


def _packCrewMembers(rewards, model):
    for recruit, count in _iterRecruits(rewards):
        name = 'tank{}man'.format('wo' if recruit.isFemale() else '')
        bonusModel = StatisticsCategoryTooltipBonusModel()
        bonusModel.setName(name)
        bonusModel.setIcon(name)
        bonusModel.setCount(count)
        bonusModel.setLabel(recruit.getFullUserName())
        model.bonuses.addViewModel(bonusModel)


def _packCustomization(rewards, model):
    for customization, count in _iterNoStyles(rewards):
        bonusModel = StatisticsCategoryTooltipBonusModel()
        bonusModel.setName(model.getBonusesCategory())
        bonusModel.setIcon(customization.itemTypeName)
        bonusModel.setCount(count)
        bonusModel.setLabel(customization.userName)
        model.bonuses.addViewModel(bonusModel)


def _packExperimentalEquipment(rewards, model):
    _packItems(rewards, model, lambda e: _isOptionalDevice(e) and e.isModernized)


def _packImprovedEquipment(rewards, model):
    _packItems(rewards, model, lambda e: _isOptionalDevice(e) and e.isDeluxe)


def _packBountyEquipment(rewards, model):
    _packItems(rewards, model, lambda e: _isOptionalDevice(e) and e.isTrophy)


def _packStandardEquipment(rewards, model):
    _packItems(rewards, model, lambda e: _isOptionalDevice(e) and e.isRegular)
    _packGoodies(rewards, model, _isDemountKit)


def _packDirectives(rewards, model):
    _packItems(rewards, model, _isDirective)


def _packTrainingMaterials(rewards, model):
    _packItems(rewards, model, _isCrewBook)
    _packGoodies(rewards, model, _isRecertificationForm)


def _packConsumables(rewards, model):
    _packItems(rewards, model, lambda e: _isEquipment(e) and not e.isStimulator)


def _packRations(rewards, model):
    _packItems(rewards, model, lambda e: _isEquipment(e) and e.isStimulator)


def _packItems(rewards, model, criteria):
    for item, count in _iterItems(rewards):
        if criteria(item):
            icon, overlay = _getItemIcons(item)
            name = _getItemName(item)
            bonusModel = StatisticsCategoryTooltipBonusModel()
            bonusModel.setIcon(icon)
            bonusModel.setOverlayType(overlay)
            bonusModel.setName(name)
            bonusModel.setLabel(item.userName)
            bonusModel.setCount(count)
            model.bonuses.addViewModel(bonusModel)


def _packGoodies(rewards, model, criteria):
    for goodie, count in _iterGoodies(rewards):
        if criteria(goodie):
            bonusModel = StatisticsCategoryTooltipBonusModel()
            bonusModel.setIcon(goodie.getFullNameForResource())
            bonusModel.setCount(count)
            bonusModel.setLabel(backport.text(R.strings.menu.booster.label.dyn(goodie.boosterGuiType)(), effectValue=goodie.getFormattedValue()) if _isPersonalReserves(goodie) else goodie.userName)
            model.bonuses.addViewModel(bonusModel)


def _packPersonalReserves(rewards, model):
    _packGoodies(rewards, model, lambda g: not _isDemountKit(g) and not _isRecertificationForm(g))


def _packBlueprints(rewards, model):
    blueprints = []
    for blueprint in blueprintBonusFactory(Type.BLUEPRINTS.value, rewards.get(Type.BLUEPRINTS.value)):
        blueprints.append(blueprint)

    for blueprint in _mergeNationalBlueprints(blueprints):
        bonusModel = StatisticsCategoryTooltipBonusModel()
        bonusModel.setName(Type.BLUEPRINTS.value)
        bonusModel.setIcon(blueprint.getImageCategory() if not isinstance(blueprint, LootBoxRandomNationalBonus) else 'randomNational')
        label = ''
        if isinstance(blueprint, LootBoxRandomNationalBonus):
            label = backport.text(R.strings.lootbox_system.statisticsRewards.tooltips.category.nationalBlueprint())
        elif blueprint.getBlueprintName() == BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT:
            label = backport.text(R.strings.lootbox_system.bonuses.label.blueprints.universalFragment())
        bonusModel.setLabel(label if label else blueprint.getBlueprintTooltipName())
        bonusModel.setCount(blueprint.getCount())
        model.bonuses.addViewModel(bonusModel)


_PACK_REWARDS = {Type.VEHICLES: _packVehicles,
 Type.STYLE3D: _pack3DStyles,
 Type.STYLE: _pack2DStyles,
 Type.CREWMEMBER: _packCrewMembers,
 Type.CUSTOMIZATIONS: _packCustomization,
 Type.EXPERIMENTALEQUIPMENT: _packExperimentalEquipment,
 Type.IMPROVEDEQUIPMENT: _packImprovedEquipment,
 Type.BOUNTYEQUIPMENT: _packBountyEquipment,
 Type.STANDARDEQUIPMENT: _packStandardEquipment,
 Type.DIRECTIVES: _packDirectives,
 Type.TRAININGMATERIALS: _packTrainingMaterials,
 Type.BLUEPRINTS: _packBlueprints,
 Type.PERSONALRESERVES: _packPersonalReserves,
 Type.CONSUMABLES: _packConsumables,
 Type.RATIONS: _packRations}

def _mergeNationalBlueprints(blueprints):
    finalBlueprints = []
    nationalBlueprintsCount = 0
    nations = set()
    nationalBlueprintsBonuses = []
    for blueprint in blueprints:
        if blueprint.getBlueprintName() == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            nationalBlueprintsCount += blueprint.getCount()
            nations.add(blueprint.getImageCategory())
            nationalBlueprintsBonuses.append(blueprint)
        finalBlueprints.append(blueprint)

    finalBlueprints += [LootBoxRandomNationalBonus(LOOTBOX_RANDOM_NATIONAL_BLUEPRINT, (nationalBlueprintsCount, None))] if len(nations) > 1 else nationalBlueprintsBonuses
    return finalBlueprints


def _setVehicleInfoModel(model, vehicle):
    model.setVehicleName(vehicle.userName)
    model.setVehicleType(vehicle.type)
    model.setVehicleLvl(vehicle.level)
    model.setIsElite(vehicle.isElite)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _iterVehicles(rewards, itemsCache=None):
    return ((itemsCache.items.getItemByCD(vehicleCD), compensationData.get('compensatedNumber', 0)) for vehiclesData in rewards.get(Type.VEHICLES.value, {}) for vehicleCD, compensationData in vehiclesData.iteritems())


@dependency.replace_none_kwargs(customization=ICustomizationService)
def _iter3DStyles(rewards, customization=None):
    return ((s, data.get('compensatedNumber', 0)) for s, data in _iterStyles(rewards) if s.itemTypeName == Type.STYLE.value and s.is3D and not s.isLockedOnVehicle)


@dependency.replace_none_kwargs(customization=ICustomizationService)
def _iter2DStyles(rewards, customization=None):
    return ((s, data.get('compensatedNumber', 0)) for s, data in _iterStyles(rewards) if s.itemTypeName == Type.STYLE.value and not s.is3D and not s.isLockedOnVehicle)


def _iterNoStyles(rewards):
    return ((s, data['value']) for s, data in _iterCustomizations(rewards) if s.itemTypeName != Type.STYLE.value)


def _iterRecruits(rewards):
    for tokenID, tokenData in rewards.get('tokens').iteritems():
        recruit = getRecruitInfo(tokenID)
        if recruit is not None:
            yield (recruit, tokenData['count'])

    return


@dependency.replace_none_kwargs(customization=ICustomizationService)
def _iterStyles(rewards, customization=None):
    return ((customization.getItemByID(GUI_ITEM_TYPE.STYLE, cData['id']), cData) for cData in (c for c in rewards.get(Type.CUSTOMIZATIONS.value)) if cData['custType'] == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE])


@dependency.replace_none_kwargs(customization=ICustomizationService)
def _iterCustomizations(rewards, customization=None):
    return ((customization.getItemByID(getItemTypeID(cData['custType']), cData['id']), cData) for cData in (c for c in rewards.get(Type.CUSTOMIZATIONS.value, {})) if cData['custType'] != GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE])


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _iterItems(rewards, itemsCache=None):
    return ((itemsCache.items.getItemByCD(itemCD), count) for itemCD, count in rewards.get('items', {}).iteritems())


@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache)
def _iterGoodies(rewards, goodiesCache=None):
    return ((goodiesCache.getGoodie(goodieID), data['count']) for goodieID, data in rewards.get('goodies', {}).iteritems())


def _getItemIcons(item):
    return (item.icon, '') if item.itemTypeID == GUI_ITEM_TYPE.CREW_BOOKS else (item.getGUIEmblemID(), item.getOverlayType())


def _getItemName(item):
    return 'crewBooks' if item.itemTypeID == GUI_ITEM_TYPE.CREW_BOOKS else item.itemTypeName


def _isOptionalDevice(item):
    return item.itemTypeName == 'optionalDevice'


def _isDirective(item):
    return item.itemTypeName == 'battleBooster'


def _isCrewBook(item):
    return item.itemTypeName == 'crewBook'


def _isEquipment(item):
    return item.itemTypeName == 'equipment'


def _isDemountKit(goodie):
    return isinstance(goodie, DemountKit)


def _isRecertificationForm(goodie):
    return isinstance(goodie, RecertificationForm)


def _isPersonalReserves(goodie):
    return isinstance(goodie, Booster)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/submodels/statistics.py
import logging
from typing import TYPE_CHECKING
from gui.goodies.goodie_items import DemountKit, RecertificationForm
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.rewards_categories_model import RewardsCategoriesModel, Type
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Any, Callable, Dict
    from gui.goodies.goodie_items import _Goodie
    from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.statistics_model import StatisticsModel
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)
_REWARD_ORDER = (Type.VEHICLES,
 Type.STYLE3D,
 Type.STYLE,
 Type.CREWMEMBER,
 Type.PREMIUMPLUS,
 Type.GOLD,
 Type.CRYSTAL,
 Type.CREDITS,
 Type.FREEXP,
 Type.CUSTOMIZATIONS,
 Type.EXPERIMENTALEQUIPMENT,
 Type.COMPONENTS,
 Type.IMPROVEDEQUIPMENT,
 Type.BOUNTYEQUIPMENT,
 Type.STANDARDEQUIPMENT,
 Type.DIRECTIVES,
 Type.TRAININGMATERIALS,
 Type.BLUEPRINTS,
 Type.BATTLEBONUSX5,
 Type.CREWBONUSX3,
 Type.PERSONALRESERVES,
 Type.CONSUMABLES,
 Type.RATIONS)
_CUSTOMIZATIONS = (Type.STYLE, Type.STYLE3D, Type.CUSTOMIZATIONS)
_UNCOUNTABLE = (Type.PREMIUMPLUS,
 Type.GOLD,
 Type.CRYSTAL,
 Type.CREDITS,
 Type.FREEXP,
 Type.COMPONENTS)
_ITEMS = (Type.DIRECTIVES,
 Type.IMPROVEDEQUIPMENT,
 Type.EXPERIMENTALEQUIPMENT,
 Type.BOUNTYEQUIPMENT,
 Type.CONSUMABLES,
 Type.RATIONS)
_COMBINED = (Type.STANDARDEQUIPMENT, Type.TRAININGMATERIALS)
_TOKENS = (Type.LOOTBOX,
 Type.CREWMEMBER,
 Type.BATTLEBONUSX5,
 Type.CREWBONUSX3)

class Statistics(object):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def update(self, model, lootBoxID, isResetCompleted):
        rewardsData, boxesCount = self.__lootBoxes.getStatistics(lootBoxID)
        model.setIsResetCompleted(isResetCompleted)
        model.setOpenedCount(boxesCount)
        model.setEventName(self.__lootBoxes.eventName)
        self.__updateRewards(model, rewardsData)

    def reset(self):
        self.__lootBoxes.resetStatistics(list(self.__lootBoxes.getBoxesIDs(self.__lootBoxes.eventName)))

    def __updateRewards(self, model, rewardsData):
        categories = model.getCategories()
        categories.clear()
        for rewardModel in self.__iterLootBoxesRewardModels(rewardsData):
            categories.addViewModel(rewardModel)

        for rewardType in _REWARD_ORDER:
            if rewardType in _CUSTOMIZATIONS:
                rewardData = rewardsData.get('customizations')
            elif rewardType in _ITEMS:
                rewardData = rewardsData.get('items')
            elif rewardType in _COMBINED:
                rewardData = rewardsData
            elif rewardType == Type.PERSONALRESERVES:
                rewardData = rewardsData.get('goodies')
            elif rewardType == Type.BLUEPRINTS:
                rewardData = rewardsData.get('blueprints')
            elif rewardType in _TOKENS:
                rewardData = rewardsData.get('tokens')
            else:
                rewardData = rewardsData.get(rewardType.value)
            rewardModel = _getRewardModel(rewardType, rewardData)
            if rewardModel is not None:
                categories.addViewModel(rewardModel)

        categories.invalidate()
        return

    def __iterLootBoxesRewardModels(self, rewardData):
        lootBoxData = [ (self.__lootBoxes.getBoxInfo(int(tokenName.split(':')[1]))['category'], tokenData['count']) for tokenName, tokenData in rewardData.get('tokens', {}).iteritems() if tokenName.startswith('lootBox') and tokenData['count'] ]
        lootBoxData.sort(key=lambda d: self.__lootBoxes.boxesPriority.get(d[0], len(self.__lootBoxes.boxesPriority)), reverse=True)
        return (_makeRewardModel('lootBox_{}'.format(category), count) for category, count in lootBoxData)


def _getRewardModel(rewardType, rewardData):
    if not rewardData:
        return None
    else:
        count = _COUNT_REWARDS[rewardType](rewardData)
        return None if not count else _makeRewardModel(rewardType.value, count)


def _countVehicles(rewardData):
    return sum((v.get('compensatedNumber', 1) for r in rewardData for v in r.itervalues()))


def _count3DStyles(rewardData):
    return _countStyles(rewardData, lambda s: s.is3D)


def _count2DStyles(rewardData):
    return _countStyles(rewardData, lambda s: not s.is3D)


@dependency.replace_none_kwargs(customization=ICustomizationService)
def _countStyles(rewardData, criteria, customization=None):
    count = 0
    for styleData in (s for s in rewardData if s['custType'] == 'style'):
        style = customization.getItemByID(GUI_ITEM_TYPE.STYLE, styleData['id'])
        if not style.isLockedOnVehicle and criteria(style):
            count += styleData['value'] or styleData.get('compensatedNumber', 0)

    return count


def _countCrew(rewardData):
    return sum((cData['count'] for cID, cData in rewardData.iteritems() if cID.startswith('tman_template')))


def _countCustomizations(rewardData):
    return sum((c['value'] for c in rewardData if c['custType'] != 'style'))


def _countExperimentalEquipment(rewardData):
    return _countItems(rewardData, lambda i: _isOptionalDevice(i) and i.isModernized)


def _countImprovedEquipment(rewardData):
    return _countItems(rewardData, lambda i: _isOptionalDevice(i) and i.isDeluxe)


def _countBountyEquipment(rewardData):
    return _countItems(rewardData, lambda i: _isOptionalDevice(i) and i.isTrophy)


def _countStandardEquipment(rewardData):
    return _countItems(rewardData.get('items', {}), lambda i: _isOptionalDevice(i) and i.isRegular) + _countGoodies(rewardData.get('goodies', {}), _isDemountKit)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _countItems(rewardData, criteria, itemsCache=None):
    return sum((itemsCount for itemCD, itemsCount in rewardData.iteritems() if criteria(itemsCache.items.getItemByCD(itemCD))))


@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache)
def _countGoodies(rewardData, criteria, goodiesCache=None):
    return sum((data.get('count', 0) for goodieID, data in rewardData.iteritems() if criteria(goodiesCache.getGoodie(goodieID))))


def _countDirectives(rewardData):
    return _countItems(rewardData, _isDirective)


def _countTrainingMaterials(rewardData):
    return _countItems(rewardData.get('items', {}), _isCrewBook) + _countGoodies(rewardData.get('goodies', {}), _isRecertificationForm)


def _countBlueprints(rewardData):
    return sum(rewardData.itervalues())


def _countBattleBonusX5(rewardData):
    return _countTokens(rewardData, 'battle_bonus_x5')


def _countCrewBonusX3(rewardData):
    return _countTokens(rewardData, 'crew_bonus_x3')


def _countTokens(rewardData, tokenName):
    return rewardData.get(tokenName, {}).get('count', 0)


def _countPersonalReserves(rewardData):
    return _countGoodies(rewardData, lambda g: not _isDemountKit(g) and not _isRecertificationForm(g))


def _countConsumables(rewardData):
    return _countItems(rewardData, lambda i: _isEquipment(i) and not i.isStimulator)


def _countRations(rewardData):
    return _countItems(rewardData, lambda i: _isEquipment(i) and i.isStimulator)


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


def _makeRewardModel(rewardType, rewardsCount):
    model = RewardsCategoriesModel()
    model.setType(rewardType)
    model.setCount(rewardsCount)
    return model


_COUNT_REWARDS = {Type.VEHICLES: _countVehicles,
 Type.STYLE3D: _count3DStyles,
 Type.STYLE: _count2DStyles,
 Type.CREWMEMBER: _countCrew,
 Type.CUSTOMIZATIONS: _countCustomizations,
 Type.EXPERIMENTALEQUIPMENT: _countExperimentalEquipment,
 Type.IMPROVEDEQUIPMENT: _countImprovedEquipment,
 Type.BOUNTYEQUIPMENT: _countBountyEquipment,
 Type.STANDARDEQUIPMENT: _countStandardEquipment,
 Type.DIRECTIVES: _countDirectives,
 Type.TRAININGMATERIALS: _countTrainingMaterials,
 Type.BLUEPRINTS: _countBlueprints,
 Type.BATTLEBONUSX5: _countBattleBonusX5,
 Type.CREWBONUSX3: _countCrewBonusX3,
 Type.PERSONALRESERVES: _countPersonalReserves,
 Type.CONSUMABLES: _countConsumables,
 Type.RATIONS: _countRations}
_COUNT_REWARDS.update({rewardType:(lambda rewardData: rewardData) for rewardType in _UNCOUNTABLE})

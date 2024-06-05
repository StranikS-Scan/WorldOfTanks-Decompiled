# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/profile_utils.py
import typing
import BigWorld
from adisp import adisp_process
from advanced_achievements_client.items import VirtualStepAchievement, RegularAchievement, SteppedAchievement
from dossiers2.custom.dependencies import VEHICLE_ACHIEVEMENTS_DEPENDENCIES, CUSTOMIZATION_ACHIEVEMENTS_DEPENDENCIES
from dossiers2.ui.achievements import ACHIEVEMENT_SECTION, ACHIEVEMENT_SECTIONS_INDICES
from gui.impl import backport
from gui.impl.backport import getIntegralFormat
from gui.impl.backport.backport_tooltip import TooltipData
from gui.impl.gen.view_models.constants.date_time_formats import DateTimeFormatsEnum
from gui.impl.gen.view_models.views.lobby.achievements.advanced_achievement_model import AdvancedAchievementType, AdvancedAchievementModel, AdvancedAchievementIconPosition, AdvancedAchievementIconSizeMap
from gui.impl.gen.view_models.views.lobby.achievements.subcategory_advanced_achievement_model import SubcategoryAdvancedAchievementModel
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.rewards_model import RewardsModel, DogTagType
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.details_model import DetailsModel, ProgressType
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.achievement_card_model import AchievementCardModel
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.breadcrumb_model import BreadcrumbModel
from gui.impl.gen.view_models.views.lobby.achievements.views.reward_view_rewards_model import RewardViewRewardsModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.dog_tags.catalog_animated_dog_tag_tooltip import CatalogAnimatedDogTagTooltip
from gui.impl.lobby.dog_tags.dog_tag_processors import getCoupledDogTagProgress
from gui.shared.formatters import text_styles
from gui.shared.formatters.date_time import getRegionalDateTime
from gui.shared.gui_items.Vehicle import getNationLessName
from helpers import dependency
from advanced_achievements_client.getters import getAchievementByID
from items import vehicles
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from advanced_achievements_client.constants import AchievementType
from gui.shared.missions.packers.bonus import CustomizationBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap, DogTagComponentsUIPacker, BACKPORT_TOOLTIP_CONTENT_ID
from dog_tags_common.components_config import componentConfigAdapter as componentConfig
from dog_tags_common.config.common import ComponentViewType, ComponentPurpose
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from advanced_achievements_client.items import _BaseGuiAchievement, _Progress
    from dog_tags_common.config.dog_tag_framework import ComponentDefinition
    from typing import Optional, Dict, Tuple, Iterator, List
    from gui.server_events.bonuses import CustomizationsBonus, DogTagComponentBonus
_ACHIEVEMENT_TYPE_MAP = {AchievementType.REGULAR: AdvancedAchievementType.SINGLE,
 AchievementType.STEPPED: AdvancedAchievementType.STAGED,
 AchievementType.CUMULATIVE: AdvancedAchievementType.CUMULATIVE,
 AchievementType.SUBCATEGORY: AdvancedAchievementType.SUBCATEGORY}
MAX_PERCENT_VALUE = 100

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isLayoutEnabled(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().isLayoutEnabled()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isSummaryEnabled(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().isSummaryEnabled()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isWTREnabled(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().isWTREnabled()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getStagesOfWTR(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().getStagesOfWTR()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getLayoutLength(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().getLayoutLength()


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def isEditingEnabled(itemsCache=None, lobbyContext=None):
    achievements20GeneralConfig = lobbyContext.getServerSettings().getAchievements20GeneralConfig()
    mainRules = achievements20GeneralConfig.getAutoGeneratingMainRules()
    extraRules = achievements20GeneralConfig.getAutoGeneratingExtraRules()
    totalCount = 0
    countAchievementsOnRibbon = 0
    layoutLength = getLayoutLength()
    achievements = itemsCache.items.getAccountDossier().getTotalStats().getAchievements(isInDossier=True, showHidden=False)
    for sectionName, maxAchievements in mainRules:
        countOfAchievements = len(achievements[ACHIEVEMENT_SECTIONS_INDICES[sectionName]])
        totalCount += countOfAchievements
        countAchievementsOnRibbon += maxAchievements if countOfAchievements >= maxAchievements else countOfAchievements
        if countAchievementsOnRibbon >= layoutLength and totalCount > layoutLength:
            return True

    for sectionName in extraRules:
        countOfAchievements = len(achievements[ACHIEVEMENT_SECTIONS_INDICES[sectionName]])
        totalCount += countOfAchievements
        countAchievementsOnRibbon += countOfAchievements
        if countAchievementsOnRibbon >= layoutLength and totalCount > layoutLength:
            return True

    return False


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getRating(itemsCache=None, userId=None):
    if isWTREnabled():
        return itemsCache.items.getWTR(userId)
    elif userId is not None:
        result = dict()
        _receiveRating(itemsCache, userId, result)
        return result.get('globalRating', 0)
    else:
        return itemsCache.items.stats.globalRating


@adisp_process
def _receiveRating(itemsCache, userId, result):
    req = itemsCache.items.dossiers.getUserDossierRequester(int(userId))
    result['globalRating'] = yield req.getGlobalRating()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getAllAchievements(itemsCache=None):
    achievements = itemsCache.items.getAccountDossier().getTotalStats().getAchievements(isInDossier=True, showHidden=False)
    total = 0
    unique = 0
    for section in achievements:
        for achievement in section:
            unique += 1
            if achievement.isDone():
                total += 1
            if achievement.getValue() > 0:
                if achievement.getSection() == ACHIEVEMENT_SECTION.CLASS:
                    total += 1
                else:
                    total += achievement.getValue()

    return (total, unique)


def getProfileCommonInfo(dossier):
    lastBattleDate = None
    lastBattleTime = None
    if dossier['total']['lastBattleTime']:
        lbt = dossier['total']['lastBattleTime']
        lastBattleDate = getRegionalDateTime(lbt, DateTimeFormatsEnum.FULLDATE)
        lastBattleTime = getRegionalDateTime(lbt, DateTimeFormatsEnum.SHORTTIME)
    return {'registrationDate': '%s' % getRegionalDateTime(dossier['total']['creationTime'], DateTimeFormatsEnum.FULLDATE),
     'lastBattleDate': lastBattleDate,
     'lastBattleTime': lastBattleTime}


def getMasteryStatistic(dossier):
    epicRandomVehicles = set(dossier.getEpicRandomStats().getVehicles().keys())
    randomStats = dossier.getRandomStats()
    totalVehiclesCount = len(epicRandomVehicles.union(set(randomStats.getVehicles().keys())))
    return (randomStats.getMarksOfMastery()[3], totalVehiclesCount)


def getNormalizedValue(targetValue):
    return targetValue if targetValue is not None else 0


def getFormattedValue(targetValue):
    return getIntegralFormat(getNormalizedValue(targetValue))


def formatPercent(value):
    value = text_styles.concatStylesWithSpace(backport.getNiceNumberFormat(value), '%')
    return value


def fillAdvancedAchievementModel(achievement, achievementModel=None, withCurrentStage=False):
    if achievementModel is None:
        achievementModel = AdvancedAchievementModel()
    if withCurrentStage and isinstance(achievement, SteppedAchievement):
        stageID = achievement.getNextOrLastStageID() if achievement.getProgress().isCompleted() else achievement.getNextOrLastStageID() - 1
        achievement = achievement.getFakeAchievementForStage(stageID)
    with achievementModel.transaction() as model:
        displayType = achievement.getDisplayType()
        model.setType(_ACHIEVEMENT_TYPE_MAP[displayType])
        model.setKey(achievement.getStringKey())
        model.setId(achievement.getID())
        model.setBackground(achievement.getBackground())
        model.setCategory(achievement.getCategory())
        model.setTheme(achievement.getTheme())
        model.setIconPosition(AdvancedAchievementIconPosition(achievement.getIconPosition()))
        model.setIconSizeMap(AdvancedAchievementIconSizeMap(achievement.getIconSizeMap()))
        progress = achievement.getProgress()
        if displayType == AchievementType.SUBCATEGORY:
            model.setCurrentValue(int(progress.getAsPercent()))
            model.setMaxValue(MAX_PERCENT_VALUE)
        else:
            model.setCurrentValue(progress.current)
            model.setMaxValue(progress.total)
        model.setAchievementScore(achievement.getRewards().getPoints())
        model.setStage(achievement.getNextOrLastStageID())
        model.setIsTrophy(achievement.isDeprecated)
        if achievement.getTimeStamp():
            model.setReceivedDate(getRegionalDateTime(achievement.getTimeStamp(), DateTimeFormatsEnum.FULLDATE))
    return achievementModel


def fillSubcategoryAdvancedAchievementModel(achievement, bubbles, prevScore, prevValue, achievementModel=None):
    if achievementModel is None:
        achievementModel = SubcategoryAdvancedAchievementModel()
    with achievementModel.transaction() as model:
        model.setType(AchievementType.SUBCATEGORY)
        model.setKey(achievement.getStringKey())
        model.setId(achievement.getID())
        model.setBackground(achievement.getBackground())
        model.setCategory(achievement.getCategory())
        model.setTheme(achievement.getTheme())
        model.setIconPosition(AdvancedAchievementIconPosition(achievement.getIconPosition()))
        model.setIconPosition(AdvancedAchievementIconSizeMap(achievement.getIconSizeMap()))
        progress = achievement.getProgress()
        currentValue = int(progress.getAsPercent())
        model.setPrevValue(prevValue if prevValue < currentValue else currentValue)
        model.setPrevAchievementScore(prevScore)
        model.setCurrentValue(currentValue)
        model.setAchievementScore(achievement.getScore().current)
        model.setStage(achievement.getNextOrLastStageID())
        model.setBubbles(bubbles)
    return achievementModel


class AdvancedAchievementsCustomizationsBonusPacker(CustomizationBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return RewardsModel()

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(AdvancedAchievementsCustomizationsBonusPacker, cls)._packSingleBonus(bonus, item, label)
        model.setId(item.get('id'))
        return model


class AdvancedAchievementsDogTagsBonusPacker(DogTagComponentsUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return RewardsModel()

    @classmethod
    def _getBonusIterator(cls, bonus):
        unlockedBonuses = bonus.getUnlockedComponents()
        for dogTagRecord in unlockedBonuses:
            component = componentConfig.getComponentById(dogTagRecord.componentId)
            if component.purpose == ComponentPurpose.COUPLED:
                if component.viewType == ComponentViewType.ENGRAVING and any((value is not None and component.coupledComponentId == value['id'] for value in bonus.getValue())):
                    yield (component, dogTagRecord)
            yield (component, dogTagRecord)

    @classmethod
    def _pack(cls, bonus):
        result = []
        for component, dogTagRecord in cls._getBonusIterator(bonus):
            if component.purpose == ComponentPurpose.COUPLED:
                result.append(cls._packCoupledDogTag(bonus, component, dogTagRecord))
            result.append(cls._packDogTag(bonus, component, dogTagRecord))

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        tooltips = []
        for component, dogTagRecord in cls._getBonusIterator(bonus):
            if component.purpose == ComponentPurpose.COUPLED:
                tooltips.append(cls._getCoupledDogTagTooltip(component))
            tooltips.append(cls._getDogTagTooltip(dogTagRecord))

        return tooltips

    @classmethod
    def _getContentId(cls, bonus):
        tooltipContentIds = []
        for component, _ in cls._getBonusIterator(bonus):
            if component.purpose == ComponentPurpose.COUPLED:
                tooltipContentIds.append(R.views.lobby.dog_tags.CatalogAnimatedDogTagTooltip())
            tooltipContentIds.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return tooltipContentIds

    @classmethod
    def _getCoupledDogTagTooltip(cls, component):
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[{'backgroundId': component.coupledComponentId,
          'engravingId': component.componentId}])

    @classmethod
    def _packDogTag(cls, bonus, component, dogTagRecord):
        model = super(AdvancedAchievementsDogTagsBonusPacker, cls)._packDogTag(bonus, dogTagRecord)
        if component.viewType == ComponentViewType.ENGRAVING:
            model.setDogTagType(DogTagType.ENGRAVING)
        else:
            model.setDogTagType(DogTagType.BACKGROUND)
        model.setPurpose(component.purpose.value.lower())
        return model

    @classmethod
    def _packCoupledDogTag(cls, bonus, component, dogTagRecord):
        model = super(AdvancedAchievementsDogTagsBonusPacker, cls)._packDogTag(bonus, dogTagRecord)
        model.setDogTagType(DogTagType.ENGRAVING)
        model.setBackgroundId(component.coupledComponentId)
        model.setEngravingId(component.componentId)
        model.setPurpose(component.purpose.value.lower())
        return model


def getAdvancedAchievementsBonusPackersMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': AdvancedAchievementsCustomizationsBonusPacker(),
     'dogTagComponents': AdvancedAchievementsDogTagsBonusPacker()})
    return mapping


def getAdvancedAchievementsBonusPacker():
    return BonusUIPacker(getAdvancedAchievementsBonusPackersMap())


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def fillDetailsModel(achievement, tooltipData, detailsModel=None, itemsCache=None):
    if detailsModel is None:
        detailsModel = DetailsModel()
    with detailsModel.transaction() as model:
        fillAdvancedAchievementModel(achievement, model)
        rewards = achievement.getRewards()
        packer = getAdvancedAchievementsBonusPacker()
        with model.getRewards().transaction() as rewardArray:
            rewardArray.clear()
            packBonusModelAndTooltipData(rewards.getBonuses(), rewardArray, tooltipData=tooltipData, packer=packer)
        progress = achievement.getProgress()
        receivedDate = getRegionalDateTime(achievement.getTimeStamp(), DateTimeFormatsEnum.FULLDATE) if progress.isCompleted() else ''
        model.setReceivedDate(receivedDate)
        if achievement.getDisplayType() == AchievementType.SUBCATEGORY:
            model.setProgressType(ProgressType.PERCENTAGE)
        else:
            model.setProgressType(ProgressType.STEPPED)
        if achievement.getVehicle():
            model.setSpecificItemLevel(getVehicleByName(achievement.getVehicle()))
    return detailsModel


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def fillAchievementCardModel(achievement, tooltipData, bubbles, itemsCache=None, achievementCardModel=None):
    if achievementCardModel is None:
        achievementCardModel = AchievementCardModel()
    with achievementCardModel.transaction() as model:
        fillDetailsModel(achievement, tooltipData, model, itemsCache=itemsCache)
        model.setId(achievement.getID())
        model.setNewItemsCount(bubbles)
        if isinstance(achievement, VirtualStepAchievement):
            model.setIsSingleStage(True)
        elif isinstance(achievement, RegularAchievement) and not isinstance(achievement, SteppedAchievement):
            if achievement.getProgress().total == 1:
                model.setIsProgressive(False)
            conditionID = achievement.getConditionID()
            if conditionID is not None:
                model.setSpecificItemId(conditionID)
                item = itemsCache.items.getItemByCD(conditionID)
                model.setSpecificItemName(item.shortUserName)
                model.setSpecificItemIconName(getNationLessName(item.name))
                model.setSpecificItemLevel(item.level)
                model.setIsResearchable(bool(achievement.getOpenByUnlock()))
        if achievement.getVehicle():
            model.setSpecificItemLevel(getVehicleByName(achievement.getVehicle()))
        if achievement.isDeprecated:
            model.setIsProgressive(False)
    return achievementCardModel


def fillBreadcrumbModel(achievement, breadcrumbModel=None):
    if breadcrumbModel is None:
        breadcrumbModel = BreadcrumbModel()
    with breadcrumbModel.transaction() as model:
        model.setAchievementId(achievement.getID())
        model.setKey(achievement.getStringKey())
    return breadcrumbModel


def getVehicleByName(name):
    return vehicles.g_cache.vehicle(*vehicles.g_list.getIDsByName(name)).level


def getTrophiesData():
    return {'key': 'trophies',
     'type': AdvancedAchievementType.CATEGORY,
     'background': 'trophies',
     'iconPosition': AdvancedAchievementIconPosition.CENTER,
     'isTrophy': True}


def createAdvancedAchievementsCatalogInitAchievementIDs(achievementID, achievementCategory):
    if achievementCategory == 'vehicleAchievements':
        categoryDependencies = VEHICLE_ACHIEVEMENTS_DEPENDENCIES
    elif achievementCategory == 'customizationAchievements':
        categoryDependencies = CUSTOMIZATION_ACHIEVEMENTS_DEPENDENCIES
    else:
        raise SoftException('Unknown advanced achievement category: {}'.format(achievementCategory))
    initAchievementIDs = [achievementID]
    parentAchievementID = first((achievementDependency.args[0].id for achievementDependency in categoryDependencies.get(achievementID, [])))
    while parentAchievementID is not None:
        initAchievementIDs.append(parentAchievementID)
        parentAchievementID = first((achievementDependency.args[0].id for achievementDependency in categoryDependencies.get(parentAchievementID, [])))

    return initAchievementIDs[1::][::-1] if getAchievementByID(achievementID, achievementCategory).getType() == AchievementType.REGULAR else initAchievementIDs[::-1]


def createBackportTooltipDecorator():

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipData = self.getTooltipData(event)
                if tooltipData is None:
                    return
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
            else:
                return func(self, event)

        return wrapper

    return decorator


def createTooltipContentDecorator(uiParent):

    def decorator(func):

        def wrapper(self, event, contentID):
            tooltipData = self.getTooltipData(event)
            if contentID == R.views.lobby.dog_tags.CatalogAnimatedDogTagTooltip():
                if tooltipData is None:
                    return
                return CatalogAnimatedDogTagTooltip(uiParent=uiParent, *tooltipData.specialArgs)
            else:
                return func(self, event, contentID)

        return wrapper

    return decorator


class RewardViewDogTagsBonusPacker(AdvancedAchievementsDogTagsBonusPacker):

    @classmethod
    def _getBonusModel(cls):
        return RewardViewRewardsModel()

    @classmethod
    def _packDogTag(cls, bonus, component, dogTagRecord):
        model = super(RewardViewDogTagsBonusPacker, cls)._packDogTag(bonus, component, dogTagRecord)
        if component.viewType == ComponentViewType.ENGRAVING:
            progress = cls._getDogTagProgress(component)
            model.setCurrentProgress(progress.value)
        return model

    @classmethod
    def _packCoupledDogTag(cls, bonus, component, dogTagRecord):
        model = super(RewardViewDogTagsBonusPacker, cls)._packCoupledDogTag(bonus, component, dogTagRecord)
        progress = cls._getDogTagProgress(component)
        model.setCurrentProgress(progress.value)
        model.setAnimation(component.animation)
        return model

    @classmethod
    def _getDogTagProgress(cls, component):
        return getCoupledDogTagProgress(cls._getDossier(), component) if component.purpose == ComponentPurpose.COUPLED else BigWorld.player().dogTags.getComponentProgress(component.componentId)

    @classmethod
    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def _getDossier(cls, itemsCache=None):
        return itemsCache.items.getAccountDossier().getDossierDescr()


def getRewardViewBonusPacker():
    mapping = getAdvancedAchievementsBonusPackersMap()
    mapping.update({'dogTagComponents': RewardViewDogTagsBonusPacker()})
    return BonusUIPacker(mapping)


class AdvancedAchievementHintChecker(object):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def check(self, aliasId):
        return not bool(self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(aliasId))

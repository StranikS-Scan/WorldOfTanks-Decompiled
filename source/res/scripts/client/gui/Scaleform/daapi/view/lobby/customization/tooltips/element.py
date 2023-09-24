# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/tooltips/element.py
import logging
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.customization.shared import getItemInventoryCount, makeVehiclesShortNamesString, getSuitableText, ITEM_TYPE_TO_TAB, CustomizationTabs
from gui.Scaleform.daapi.view.lobby.customization.shared import getProgressionItemStatusText
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.SEASONS_CONSTANTS import SEASONS_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization.constants import CustomizationModes
from gui.customization.shared import PROJECTION_DECAL_TEXT_FORM_TAG, SEASON_TYPE_TO_NAME, PROJECTION_DECAL_FORM_TO_UI_ID, getBaseStyleItems, getAncestors, getInheritors
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.missions.cards_formatters import CARD_FIELDS_FORMATTERS
from gui.server_events.cond_formatters.bonus import BattlesCountFormatter
from gui.server_events.events_helpers import getC11nQuestsConfig
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.items_parameters import formatters as params_formatters
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.missions.packers.conditions import getDefaultMissionsBonusConditionsFormatter, getDefaultPostBattleCondFormatter, getDefaultVehicleCondFormatter
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.utils.graphics import isRendererPipelineDeferred
from shared_utils import first
from helpers import dependency, int2roman, time_utils
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import ProjectionDecalFormTags, SeasonType, ItemTags, CustomizationDisplayType
from items.vehicles import CamouflageBonus
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class SimplifiedStatsBlockConstructor(object):

    def __init__(self, stockParams, comparator, padding=None):
        self.__stockParams = stockParams
        self.__comparator = comparator
        self.__padding = padding or formatters.packPadding(left=67, top=8)

    def construct(self):
        blocks = []
        for parameter in params_formatters.getRelativeDiffParams(self.__comparator):
            delta = parameter.state[1]
            value = parameter.value
            if delta > 0:
                value -= delta
            blocks.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(MENU.tank_params(parameter.name)), valueStr=params_formatters.simplifiedDeltaParameter(parameter), statusBarData=SimplifiedBarVO(value=value, delta=delta, markerValue=self.__stockParams[parameter.name]), padding=self.__padding))

        return blocks


class SimpleCustomizationTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(SimpleCustomizationTooltip, self).__init__(context, TOOLTIP_TYPE.TECH_CUSTOMIZATION)
        self._setContentMargin(top=20, left=19, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(440)

    def _packBlocks(self, *args, **kwargs):
        blocks = self._packItemBlocks(*args, **kwargs)
        blockData = formatters.packBuildUpBlockData(blocks, gap=-6, padding={'bottom': -5})
        return [blockData]

    def _packItemBlocks(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def _packNonHistoricBlock(topPadding):
        title = R.strings.vehicle_customization.customization.tooltip.description.historic.false.title
        desc = R.strings.vehicle_customization.customization.tooltip.description.historic.false.description
        blocks = [formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(title())), padding={'top': topPadding,
          'bottom': 10}), formatters.packTextBlockData(text=text_styles.main(backport.text(desc())))]
        return blocks


class NonHistoricTooltip(SimpleCustomizationTooltip):

    def _packItemBlocks(self):
        img = R.images.gui.maps.icons.customization.non_historical
        nonHistoricTitle = R.strings.vehicle_customization.customization.tooltip.description.nonHistoric.title
        nonHistoricDesc = R.strings.vehicle_customization.customization.tooltip.description.historic.false.description
        blocks = [formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(nonHistoricTitle())), img=backport.image(img()), imgPadding={'left': -3,
          'top': -4}), formatters.packTextBlockData(text=text_styles.main(backport.text(nonHistoricDesc())))]
        return blocks


class FantasticalTooltip(SimpleCustomizationTooltip):

    def _packItemBlocks(self):
        img = R.images.gui.maps.icons.customization.fantastical
        fantasticalTitle = R.strings.vehicle_customization.customization.tooltip.description.fantastical.title
        fantasticalDesc = R.strings.vehicle_customization.customization.tooltip.description.historic.false.description
        blocks = [formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(fantasticalTitle())), img=backport.image(img()), imgPadding={'left': -3,
          'top': -4}), formatters.packTextBlockData(text=text_styles.main(backport.text(fantasticalDesc())))]
        return blocks


class ChainedTooltip(SimpleCustomizationTooltip):

    def _packItemBlocks(self):
        return self._packChainedBlock()

    @staticmethod
    def _packChainedBlock():
        img = R.images.gui.maps.icons.customization.chained_ico
        title = R.strings.vehicle_customization.carousel.chained.header
        desc = R.strings.vehicle_customization.carousel.chained.description
        blocks = [formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(title())), img=backport.image(img()), imgPadding={'left': 4,
          'right': 6,
          'top': 4}, padding={'bottom': 10}), formatters.packTextBlockData(text=text_styles.main(backport.text(desc())))]
        return blocks


class PopoverTooltip(SimpleCustomizationTooltip):
    __service = dependency.descriptor(ICustomizationService)

    def _packItemBlocks(self, isNonHistoric):
        blocks = self.__packPopoverBlock()
        if isNonHistoric:
            blocks.extend(self._packNonHistoricBlock(topPadding=20))
        return blocks

    @classmethod
    def __packPopoverBlock(cls):
        ctx = cls.__service.getCtx()
        if ctx.modeId == CustomizationModes.CUSTOM:
            seasonName = SEASON_TYPE_TO_NAME.get(ctx.season)
            mapName = R.strings.vehicle_customization.season.selection.mapName.dyn(seasonName)
        else:
            mapName = R.strings.vehicle_customization.season.selection.mapName.all
        title = R.strings.vehicle_customization.customization.itemsPopover.btn
        desc = R.strings.vehicle_customization.season.selection.tooltip
        blocks = [formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(title()))), formatters.packTextBlockData(text=text_styles.main(backport.text(desc(), mapName=backport.text(mapName()))), padding={'top': 10})]
        return blocks


class ElementTooltip(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __service = dependency.descriptor(ICustomizationService)
    __eventsCache = dependency.descriptor(IEventsCache)
    CUSTOMIZATION_TOOLTIP_WIDTH = 446
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH = 104
    CUSTOMIZATION_TOOLTIP_ICON_HEIGHT = 102
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH_WIDE = 204
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH_OTHER_BIG = 226
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH_INSCRIPTION = 278
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH_PERSONAL_NUMBER = 390
    ALL_SEASON_MAP_ICON = 'all_season'
    HISTORICAL_ICON = 'historical'
    NON_HISTORICAL_ICON = 'non_historical'
    FANTASTICAL_ICON = 'fantastical'
    RENTABLE_ICON = 'rentable'
    EDITABLE_DISABLE_ICON = 'editable_disable'
    EDITED_ICON = 'edited'
    EDITABLE_ICON = 'editable'
    NON_EDITABLE_ICON = 'non_editable'
    PROGRESSION_REWIND_ICON = 'progression_rewind'
    SERIAL_NUMBER_ICON = 'serial_number'
    QUEST_PROGRESSION_ICON = 'questProgression'
    OPENED_ICON = 'opened'

    def __init__(self, context, tooltipType=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM):
        super(ElementTooltip, self).__init__(context, tooltipType)
        self._setContentMargin(top=10, left=19, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(self.CUSTOMIZATION_TOOLTIP_WIDTH)
        self._item = None
        self._appliedCount = 0
        self._progressionLevel = 0
        self._showOnlyProgressBlock = False
        self.__ctx = None
        self.__vehicle = None
        return

    def _packBlocks(self, *args):
        config = CustomizationTooltipContext(*args)
        self._item = self.__itemsCache.items.getItemByCD(config.itemCD)
        statsConfig = self.context.getStatsConfiguration(self._item)
        self.__ctx = self.__service.getCtx()
        if config.vehicleIntCD == 0:
            self.__vehicle = None
        elif config.vehicleIntCD == -1:
            self.__vehicle = g_currentVehicle.item
        else:
            self.__vehicle = self.__itemsCache.items.getItemByCD(config.vehicleIntCD)
        showInventoryBlock = config.showInventoryBlock
        statsConfig.buyPrice = showInventoryBlock
        statsConfig.sellPrice = showInventoryBlock
        statsConfig.inventoryCount = showInventoryBlock
        self._progressionLevel = config.level
        self._showOnlyProgressBlock = config.showOnlyProgressBlock
        return self._packItemBlocks(statsConfig)

    def _packItemBlocks(self, statsConfig):
        vehIntCD = self.__vehicle.intCD if self.__vehicle is not None else 0
        self.bonusDescription = VEHICLE_CUSTOMIZATION.BONUS_CONDITION_SEASON
        topBlocks = [self._packTitleBlock(), self._packIconBlock(self._item.isDim())]
        items = [formatters.packBuildUpBlockData(blocks=topBlocks, gap=10)]
        self.boundVehs = self._item.getBoundVehicles()
        self.installedVehs = self._item.getInstalledVehicles()
        self.installedCount = self._item.installedCount(vehIntCD) if vehIntCD else 0
        itemCD = self._item.intCD
        isItemInStyle = self._item.isStyleOnly or itemCD in getBaseStyleItems()
        if self._item.isProgressive:
            progressBlock = self._packProgressBlock()
            if progressBlock is not None:
                items.append(progressBlock)
            if self._showOnlyProgressBlock and self._progressionLevel > 0:
                block = self._packCharacteristicsBlock()
                if block:
                    items.append(block)
                suitableBlock = self._packSuitableBlock()
                if suitableBlock is not None:
                    items.append(suitableBlock)
                block = self._packUnsupportedBlock()
                if block is not None:
                    items.append(block)
                progressStateBlock = self._packProgressStateBlock()
                if progressStateBlock is not None:
                    items.append(progressStateBlock)
                return items
        camo = None
        self._appliedCount = 0
        bonusEnabled = False
        bonus = None
        if self._item.itemTypeID != GUI_ITEM_TYPE.STYLE:
            bonus = self._item.bonus
            if self.__ctx is not None:
                self._appliedCount = self.__ctx.mode.getItemAppliedCount(self._item)
                hullContainer = self.__ctx.mode.currentOutfit.hull
                bonusEnabled = hullContainer.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD() == itemCD
        elif self.__vehicle is not None:
            self.bonusDescription = VEHICLE_CUSTOMIZATION.BONUS_STYLE
            vehicleCD = self.__vehicle.descriptor.makeCompactDescr()
            for season in SeasonType.COMMON_SEASONS:
                hullContainer = self._item.getOutfit(season, vehicleCD=vehicleCD).hull
                intCD = hullContainer.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD()
                if intCD:
                    camo = self.__service.getItemByCD(intCD)
                    if camo.bonus:
                        bonus = camo.bonus
                        break

            if self.__ctx is not None:
                currentStyleDesc = self.__ctx.mode.currentOutfit.style
                isApplied = currentStyleDesc is not None and self._item.id == currentStyleDesc.id
                bonusEnabled = bonus is not None and isApplied
                self._appliedCount = int(isApplied)
        if bonus and statsConfig.showBonus:
            camo = camo or self._item
            bonusBlock = self._packBonusBlock(bonus, camo, bonusEnabled)
            items.append(bonusBlock)
        if self._item.customizationDisplayType() != CustomizationDisplayType.HISTORICAL or self._item.fullDescription:
            block = self._packDescriptionBlock()
            if block:
                items.append(block)
        if self._item.isQuestsProgression and self._item.itemTypeID != GUI_ITEM_TYPE.STYLE:
            block = self._packQuestsBlock()
            if block:
                items.append(block)
        block = self._packCharacteristicsBlock()
        if block:
            items.append(block)
        styleDependencies = None
        if self.__ctx is not None:
            styleDependencies = self.__ctx.mode.getDependenciesData()
        if styleDependencies:
            if self._item.itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
                inheritors = getInheritors(itemCD, styleDependencies)
                if inheritors:
                    items.append(self.__packAncestorBlock(inheritors))
            else:
                ancestors = getAncestors(itemCD, styleDependencies)
                if ancestors:
                    items.append(self.__packInheritorBlock(ancestors))
        if statsConfig.buyPrice or statsConfig.sellPrice or statsConfig.inventoryCount:
            inventoryBlocks = self._packInventoryBlock(statsConfig.buyPrice, statsConfig.sellPrice, statsConfig.inventoryCount)
            if inventoryBlocks['data']['blocksData']:
                items.append(inventoryBlocks)
        if not self._item.isUnlocked:
            items.append(self._packLockedBlock())
        block = self._packSuitableBlock()
        if block:
            items.append(block)
        if not self._item.isVehicleBound and (self._item.isHidden or self._item.isLimited) and not isItemInStyle:
            block = self._packAppliedBlock()
            if block:
                items.append(block)
        if self._item.isVehicleBound or self._item.isLimited and not isItemInStyle:
            block = self._packSpecialBlock()
            if block is not None:
                items.append(block)
        block = self._packUnsupportedBlock()
        if block is not None:
            items.append(block)
        block = self._packStatusBlock()
        if block:
            items.append(block)
        return items

    def _packStatusBlock(self):
        blocks = []
        if not self._item.isQuestsProgression or self._item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            return None
        else:
            rStatus = R.strings.vehicle_customization.customization.tooltip.quests.status
            _, level = self._item.getQuestsProgressionInfo()
            if not self._item.requiredToken:
                blocks.append(formatters.packImageTextBlockData(desc=text_styles.bonusAppliedText(backport.text(rStatus.completed(), level=int2roman(level))), img=backport.image(R.images.gui.maps.icons.library.ConfirmIcon_1()), imgPadding=formatters.packPadding(top=2)))
            else:
                quests = self._item.getUnlockingQuests()
                tokenCount = self.__itemsCache.items.tokens.getTokenCount(self._item.requiredToken)
                isCompleted = any((quest.isCompleted() for quest in quests)) if quests else False
                if isCompleted or tokenCount >= self._item.descriptor.requiredTokenCount:
                    if level < 1:
                        return None
                    blocks.append(formatters.packImageTextBlockData(desc=text_styles.bonusAppliedText(backport.text(rStatus.completed(), level=int2roman(level))), img=backport.image(R.images.gui.maps.icons.library.ConfirmIcon_1()), imgPadding=formatters.packPadding(top=2)))
                else:
                    isAvailable = tokenCount == self._item.descriptor.requiredTokenCount - 1
                    isValid = not self._item.isUnlockingExpired()
                    if not isValid or not isAvailable:
                        unavailableBlocks = []
                        unavailableBlocks.append(formatters.packImageTextBlockData(desc=text_styles.error(backport.text(rStatus.unavailable())), img=backport.image(R.images.gui.maps.icons.library.CancelIcon_1()), imgPadding=formatters.packPadding(top=2)))
                        if not isValid:
                            unavailableBlocks.append(formatters.packAlignedTextBlockData(text=text_styles.main(backport.text(rStatus.timedOut())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
                        elif not isAvailable:
                            unavailableBlocks.append(formatters.packAlignedTextBlockData(text=text_styles.main(backport.text(rStatus.insufficientLevel())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
                        blocks.append(formatters.packBuildUpBlockData(blocks=unavailableBlocks, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=-8)))
                    else:
                        blocks.append(formatters.packImageTextBlockData(desc=text_styles.neutral(backport.text(rStatus.inProgress())), img=backport.image(R.images.gui.maps.icons.library.inProgressIcon()), imgPadding=formatters.packPadding(top=2)))
                        questsConfig = getC11nQuestsConfig()[self._item.requiredToken]
                        timeLeft = time_utils.getServerTimeDiffInLocal(time_utils.makeLocalServerTime(questsConfig[self._item.descriptor.requiredTokenCount]['finishTime']))
                        if timeLeft <= time_utils.ONE_WEEK:
                            blocks.append(formatters.packImageTextBlockData(desc=text_styles.tutorial(backport.backport_time_utils.getTillTimeStringByRClass(timeLeft, R.strings.vehicle_customization.customization.tooltip.quests.status.timeLeft)), img=backport.image(R.images.gui.maps.icons.library.ClockIcon_1()), imgPadding=formatters.packPadding(top=-8, right=-8), padding=formatters.packPadding(bottom=-15)))
            return formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(top=-3, bottom=-13, right=20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL)

    def _packQuestsBlock(self):
        blocks = []
        quests = self._item.getUnlockingQuests()
        tokenCount = self.__itemsCache.items.tokens.getTokenCount(self._item.requiredToken)
        if not self._item.requiredToken or self._item.requiredToken and (self._item.isUnlockingExpired() or tokenCount >= self._item.descriptor.requiredTokenCount):
            return
        else:
            blocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.vehicle_customization.customization.tooltip.quests.title()))))
            padding = formatters.packPadding(left=83, bottom=0)

            def formatCondition(quest, isCompleted, isAvailable, current, total, description):
                if current == total or quest.isCompleted():
                    value = text_styles.bonusAppliedText(backport.text(R.strings.vehicle_customization.customization.tooltip.quests.progress()))
                    icon = backport.image(R.images.gui.maps.icons.library.ConfirmIcon_1())
                    iconPadding = formatters.packPadding(top=2, left=4)
                    titlePadding = formatters.packPadding(left=4)
                else:
                    if isAvailable:
                        value = '{} / {}'.format(text_styles.neutral(current), total)
                    else:
                        value = text_styles.standard('{} / {}'.format(current, total))
                    icon = backport.image(R.images.gui.maps.icons.library.circle())
                    iconPadding = formatters.packPadding(top=5, left=7)
                    titlePadding = formatters.packPadding(left=6)
                return formatters.packTitleDescParameterWithIconBlockData(title=text_styles.standard(description) if isCompleted or not isAvailable else text_styles.main(description), value=value, icon=icon, padding=padding, titlePadding=titlePadding, iconPadding=iconPadding, titleWidth=300)

            isLevelCompleted = False
            progressPercents = []
            isAvailable = tokenCount == self._item.descriptor.requiredTokenCount - 1
            delimitersToPost = len(quests) - 1
            for quest in quests:
                vehCond = getDefaultVehicleCondFormatter().format(quest.vehicleReqs, quest)
                postBattleCond = getDefaultPostBattleCondFormatter().format(quest.postBattleCond, quest)
                bonusCond = getDefaultMissionsBonusConditionsFormatter().format(quest.bonusCond, quest)
                isCompleted = quest is not None and quest.isCompleted() or tokenCount >= self._item.descriptor.requiredTokenCount
                isLevelCompleted = isLevelCompleted or isCompleted
                battleCountCondition = quest.bonusCond.getConditions().find('battles')
                battlesCount = None
                hasBattleConditions = False
                if battleCountCondition is not None:
                    battlesCount = first(BattlesCountFormatter(bool(postBattleCond)).format(battleCountCondition, quest))
                for orItem in postBattleCond:
                    progress = 0
                    andItems = orItem + first(vehCond, []) + first(bonusCond, [])
                    for andItem in andItems:
                        descrData = andItem.descrData
                        if andItem.conditionData:
                            description = andItem.conditionData.get('data', {}).get('description')
                        elif descrData and first(descrData.args):
                            description = CARD_FIELDS_FORMATTERS[descrData.formatterID](*descrData.args)
                        else:
                            description = ''
                            _logger.error('Description is not provided for questID: %d', 0)
                        current = int(andItem.current or 0 if battlesCount is None else battlesCount.current)
                        total = int(andItem.total or 1 if battlesCount is None else battlesCount.total)
                        progress += int(round(current * 100.0 / total))
                        blocks.append(formatCondition(quest, isCompleted, isAvailable, current, total, description))
                        hasBattleConditions = True

                    if andItems:
                        progress /= len(andItems)
                    progressPercents.append(progress)

                if quest.accountReqs.getTokens() and not hasBattleConditions:
                    blocks.append(formatCondition(quest, isCompleted, isAvailable, 0, 1, quest.getDescription()))
                if delimitersToPost:
                    blocks.append(formatters.packQuestOrConditionBlockData(padding=formatters.packPadding(bottom=-22, right=17)))
                    delimitersToPost -= 1

            if not isLevelCompleted and isAvailable:
                blocks.append(formatters.packQuestProgressBlockData(max(progressPercents), padding=formatters.packPadding(left=-19, top=13, bottom=-35)))
            return formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(top=-8, bottom=-8))

    def _packCharacteristicsBlock(self):
        blocks = []
        blocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_CHARACTERISTICS_TITLE)))
        rCharacteristics = R.strings.vehicle_customization.customization.tooltip.characteristics
        mapType = None
        mapIcon = ''
        if not self._item.isAllSeason():
            if self._item.isSummer():
                mapType = backport.text(rCharacteristics.map.summer())
                mapIcon = SEASONS_CONSTANTS.SUMMER
            elif self._item.isWinter():
                mapType = backport.text(rCharacteristics.map.winter())
                mapIcon = SEASONS_CONSTANTS.WINTER
            elif self._item.isDesert():
                mapType = backport.text(rCharacteristics.map.desert())
                mapIcon = SEASONS_CONSTANTS.DESERT
        else:
            mapType = backport.text(rCharacteristics.map.all())
            mapIcon = self.ALL_SEASON_MAP_ICON
        isWideOffset = False
        if self._item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            tag = self._item.formfactor
            isWideOffset = tag == ProjectionDecalFormTags.RECT1X4 or tag == ProjectionDecalFormTags.RECT1X6
        if mapType:
            blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(mapType), padding=formatters.packPadding(top=-2), icon=mapIcon, isWideOffset=isWideOffset))
        if self._item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL:
            blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(rCharacteristics.historicity.historical())), padding=formatters.packPadding(top=-2), icon=self.HISTORICAL_ICON, isWideOffset=isWideOffset))
        elif self._item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL:
            blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(rCharacteristics.historicity.nonHistorical())), padding=formatters.packPadding(top=-2), icon=self.NON_HISTORICAL_ICON, isWideOffset=isWideOffset))
        else:
            blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(rCharacteristics.historicity.fantastical())), padding=formatters.packPadding(top=-2), icon=self.FANTASTICAL_ICON, isWideOffset=isWideOffset))
        if self._item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(_ms(backport.text(rCharacteristics.form.text()), value=text_styles.stats(PROJECTION_DECAL_TEXT_FORM_TAG[self._item.formfactor]))), padding=formatters.packPadding(top=-2), icon='form_' + str(PROJECTION_DECAL_FORM_TO_UI_ID[self._item.formfactor]), isWideOffset=isWideOffset))
        if (self._item.isProgressive or self._item.isQuestsProgression) and self.__vehicle is not None:
            currentLevel = self._progressionLevel if self._progressionLevel > 0 else self._item.getLatestOpenedProgressionLevel(self.__vehicle)
            if self._item.isProgressionRewindEnabled:
                blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(rCharacteristics.progressionRewind())), padding=formatters.packPadding(top=-2), icon=self.PROGRESSION_REWIND_ICON, isWideOffset=isWideOffset))
            elif currentLevel > 0:
                icon = 'progression_{}'
                if self._item.itemTypeID == GUI_ITEM_TYPE.STYLE or self._item.isQuestsProgression:
                    icon = 'style_progression_{}'
                levelText = GUI_ITEM_TYPE_NAMES[self._item.itemTypeID]
                if not rCharacteristics.level.dyn(levelText):
                    levelText = 'progression'
                blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(rCharacteristics.level.dyn(levelText).text(), value=text_styles.stats(int2roman(currentLevel)))), padding=formatters.packPadding(top=-2), icon=icon.format(currentLevel), isWideOffset=isWideOffset))
        if self._item.itemTypeID == GUI_ITEM_TYPE.STYLE and self._item.isWithSerialNumber and self._item.serialNumber:
            blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(R.strings.vehicle_customization.customization.tooltip.characteristics.serialNumber(), number=text_styles.stats(self._item.serialNumber))), padding=formatters.packPadding(top=-2), icon=self.SERIAL_NUMBER_ICON, isWideOffset=isWideOffset))
        if self._item.isRentable:
            blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(rCharacteristics.rentable())), padding=formatters.packPadding(top=-2), icon=self.RENTABLE_ICON, isWideOffset=isWideOffset))
        if self._item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            modifiedStrRoot = rCharacteristics.collapsible
            if self._item.isEditable:
                if self.__vehicle is not None:
                    vehicleIntCD = self.__vehicle.intCD
                    if not self._item.canBeEditedForVehicle(vehicleIntCD) and self._progressionLevel <= 0:
                        modifiedStr = modifiedStrRoot.mutableWithDecal()
                        modifiedIcon = self.EDITABLE_DISABLE_ICON
                    elif self._item.isEditedForVehicle(vehicleIntCD):
                        modifiedStr = modifiedStrRoot.modified()
                        modifiedIcon = self.EDITED_ICON
                    else:
                        modifiedStr = modifiedStrRoot.mutable()
                        modifiedIcon = self.EDITABLE_ICON
                else:
                    modifiedStr = modifiedStrRoot.mutable()
                    modifiedIcon = self.EDITABLE_ICON
            else:
                modifiedStr = modifiedStrRoot.unmutable()
                modifiedIcon = self.NON_EDITABLE_ICON
            blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(modifiedStr)), padding=formatters.packPadding(top=-2), icon=modifiedIcon, isWideOffset=isWideOffset))
            if self._item.isQuestsProgression:
                blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(backport.text(rCharacteristics.questProgression())), padding=formatters.packPadding(top=-2), icon=self.QUEST_PROGRESSION_ICON, isWideOffset=isWideOffset))
        return formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(top=-8, bottom=-10))

    @staticmethod
    def _getCustomizationTypes():
        return set()

    def _packSuitableBlock(self):
        if self._item.isQuestsProgression and self._item.itemTypeID != GUI_ITEM_TYPE.STYLE:
            return []
        else:
            customizationTypes = self._getCustomizationTypes()
            isItemInStyle = self._item.isStyleOnly or self._item.intCD in getBaseStyleItems()
            isItemHidden = self._item.isHidden
            mustNotHave = self._item.itemTypeID in customizationTypes
            mayHave = self._item.itemTypeID in GUI_ITEM_TYPE.CUSTOMIZATIONS and self._item.itemTypeID not in customizationTypes
            if mustNotHave and (isItemHidden or isItemInStyle) or mayHave and isItemHidden and isItemInStyle and not self._item.isQuestsProgression:
                return None
            if self._item.isProgressive and self._item.isProgressionAutoBound or ItemTags.NATIONAL_EMBLEM in self._item.tags:
                return formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SUITABLE_TITLE), desc=text_styles.main(self.__vehicle.shortUserName), padding=formatters.packPadding(top=-2))
            boundAndInstalledVehs = self.boundVehs | self.installedVehs
            if self._item.isVehicleBound and not self._item.mayApply and boundAndInstalledVehs:
                return formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SUITABLE_TITLE), desc=text_styles.main(makeVehiclesShortNamesString(boundAndInstalledVehs, self.__vehicle)), padding=formatters.packPadding(top=-2))
            if not self._item.descriptor.filter or not self._item.descriptor.filter.include:
                return formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SUITABLE_TITLE), desc=text_styles.main(backport.text(R.strings.vehicle_customization.customization.tooltip.suitable.text.allVehicle())), padding=formatters.packPadding(top=-2))
            blocks = []
            icn = getSuitableText(self._item, self.__vehicle)
            blocks.append(formatters.packTextBlockData(text=icn, padding=formatters.packPadding(top=-2)))
            blocks.insert(0, formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SUITABLE_TITLE)))
            return formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(top=-8, bottom=-18))

    def _packAppliedBlock(self):
        if self.__ctx is not None and self.__ctx.modeId == CustomizationModes.STYLED:
            if self._item.itemTypeID != GUI_ITEM_TYPE.STYLE:
                return
        if self._item.isStyleOnly:
            return
        else:
            vehicles = set(self.installedVehs)
            if self._appliedCount > 0:
                vehicles.add(self.__vehicle.intCD)
            elif not self.installedVehs:
                return
            if self.__vehicle.intCD not in vehicles and self._item.descriptor.filter is not None and not self._item.descriptor.filter.match(self.__vehicle.descriptor):
                return
            if self._item.mayApply or self.__vehicle.intCD in self.installedVehs:
                return formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LIMITED_ON_VEHICLE), desc=text_styles.main(makeVehiclesShortNamesString(vehicles, self.__vehicle)), padding=formatters.packPadding(top=-2))
            blocks = [formatters.packImageTextBlockData(title=text_styles.critical(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LIMITED_ON_OTHER_VEHICLE), img=RES_ICONS.MAPS_ICONS_LIBRARY_MARKER_BLOCKED, imgPadding=formatters.packPadding(left=2, top=2)), formatters.packTextBlockData(text=text_styles.main(_ms(makeVehiclesShortNamesString(vehicles, self.__vehicle))), padding=formatters.packPadding(top=-7))]
            return formatters.packBuildUpBlockData(blocks, gap=3, padding=formatters.packPadding(bottom=-5))

    def _packSpecialBlock(self):
        blocks = []
        specials = []
        if self._item.isVehicleBound and self._item.mayApply and not self._item.isProgressionAutoBound:
            if self._item.isRentable:
                specials.append(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_RENT_SPECIAL_TEXT))
            else:
                specials.append(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BOUND_SPECIAL_TEXT))
        if self._item.isLimited:
            if self.__ctx is not None:
                purchaseLimit = self.__ctx.mode.getPurchaseLimit(self._item)
            else:
                purchaseLimit = self._item.buyCount
            if self._item.buyCount > 0 and purchaseLimit > 0:
                specials.append(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LIMITED_SPECIAL_RULES_TEXT, available=text_styles.neutral(purchaseLimit)))
        if not specials:
            return
        else:
            if len(specials) > 1:
                specials = [ '<li>{}</li>'.format(s) for s in specials ]
            for special in specials:
                blocks.append(formatters.packTextBlockData(text=text_styles.main(special)))

            blocks.insert(0, formatters.packImageTextBlockData(title=text_styles.statusAttention(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LIMITED_SPECIAL_RULES_TITLE), img=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_STAR, imgPadding=formatters.packPadding(left=-3, top=2)))
            return formatters.packBuildUpBlockData(blocks, gap=3, padding=formatters.packPadding(bottom=-5))

    def _packTitleBlock(self):
        title = self._item.userName
        tooltipKey = TOOLTIPS.getItemBoxTooltip(self._item.itemTypeName)
        if tooltipKey:
            title = _ms(tooltipKey, group=self._item.userType, value=self._item.userName)
        return formatters.packItemTitleDescBlockData(title=text_styles.highTitle(title), highlightPath=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_CORNER_RARE, img=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_BRUSH_RARE, imgPadding=formatters.packPadding(top=15, left=8), padding=formatters.packPadding(top=-20, left=-19, bottom=-7), txtPadding=formatters.packPadding(top=20, left=-8), descPadding=formatters.packPadding(top=25, left=-8)) if self._item.isRare() else formatters.packTitleDescBlock(title=text_styles.highTitle(title), descPadding=formatters.packPadding(top=-5))

    def _packInventoryBlock(self, showBuyPrice, showSellPrice, showInventoryCount):
        subBlocks = []
        money = self.__itemsCache.items.stats.money
        if showBuyPrice and not self._item.isHidden:
            for itemPrice in self._item.buyPrices:
                currency = itemPrice.getCurrency()
                value = itemPrice.price.getSignValue(currency)
                defValue = itemPrice.defPrice.getSignValue(currency)
                needValue = value - money.getSignValue(currency)
                actionPercent = itemPrice.getActionPrc()
                if not self._item.isRentable:
                    setting = CURRENCY_SETTINGS.getBuySetting
                    forcedText = ''
                else:
                    setting = CURRENCY_SETTINGS.getRentSetting
                    forcedText = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_COST_RENT, battlesNum=self._item.rentCount)
                if self._item.buyCount > 0:
                    subBlocks.append(makePriceBlock(value, setting(currency), needValue if needValue > 0 else None, defValue if defValue > 0 else None, actionPercent, valueWidth=88, leftPadding=49, iconRightOffset=2, gap=4, forcedText=forcedText))

        if showSellPrice and not (self._item.isHidden or self._item.isRentable):
            for itemPrice in self._item.sellPrices:
                currency = itemPrice.getCurrency()
                value = itemPrice.price.getSignValue(currency)
                defValue = itemPrice.defPrice.getSignValue(currency)
                actionPercent = itemPrice.getActionPrc()
                if actionPercent > 0:
                    subBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.ACTIONPRICE_SELL_BODY_SIMPLE), value=text_styles.concatStylesToSingleLine(text_styles.credits(backport.getIntegralFormat(value)), '    ', icons.credits()), icon='alertMedium', valueWidth=88, padding=formatters.packPadding(left=-5)))
                subBlocks.append(makePriceBlock(value, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=defValue if defValue > 0 else None, percent=actionPercent, valueWidth=88, leftPadding=49, iconRightOffset=2, gap=4))

        if self._item.isQuestsProgression and self._item.itemTypeID == GUI_ITEM_TYPE.STYLE and self._item.descriptor.questsProgression:
            padding = formatters.packPadding(left=83, bottom=0)
            titlePadding = formatters.packPadding(left=-1)
            totalItems = self._item.descriptor.questsProgression.getTotalCount()
            itemsOpened = sum([ self._item.descriptor.questsProgression.getUnlockedCount(token, self.__eventsCache.questsProgress.getTokenCount(token)) for token in self._item.descriptor.questsProgression.getGroupTokens() ])
            countText = '{} / {}'.format(text_styles.stats(itemsOpened), text_styles.main(totalItems))
            subBlocks.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(backport.text(R.strings.vehicle_customization.customization.tooltip.characteristics.opened())), value=countText, icon=backport.image(R.images.gui.maps.icons.customization.opened()), padding=padding, titlePadding=titlePadding, iconPadding=formatters.packPadding(top=2)))
        if self._item.isUnlockedByToken():
            if self.__ctx is not None:
                inventoryCount = self.__ctx.mode.getItemInventoryCount(self._item)
            else:
                inventoryCount = getItemInventoryCount(self._item)
        else:
            inventoryCount = 0
        info = text_styles.concatStylesWithSpace(text_styles.stats(inventoryCount))
        padding = formatters.packPadding(left=83, bottom=0)
        titlePadding = formatters.packPadding(left=-1)
        if showInventoryCount and inventoryCount > 0:
            if self._item.isRentable:
                textKey = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_RENT_BATTLESLEFT
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_CLOCKICON_1
                autoRentEnabled = self.__ctx.mode.isAutoRentEnabled() if self.__ctx is not None else False
                if self._item.isRented and autoRentEnabled:
                    textKey = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_RENT_BATTLESLEFT_AUTOPROLONGATIONON
                    icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ICON_RENT
                title = text_styles.main(_ms(textKey, tankname=self.__vehicle.shortUserName))
                padding = formatters.packPadding(left=83, bottom=-14)
                titlePadding = formatters.packPadding(left=-8)
                iconPadding = formatters.packPadding(top=-7, left=-3)
            else:
                title = text_styles.main(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_AVAILABLE)
                icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_STORAGE_ICON
                padding = formatters.packPadding(left=83, bottom=0)
                titlePadding = formatters.packPadding(left=-1)
                iconPadding = formatters.packPadding(top=-2, left=-2)
            subBlocks.append(formatters.packTitleDescParameterWithIconBlockData(title=title, value=info, icon=icon, padding=padding, titlePadding=titlePadding, iconPadding=iconPadding))
        boundCount = self._item.boundInventoryCount(self.__vehicle.intCD)
        commonCount = boundCount + self.installedCount
        isVehicleBound = self._item.isVehicleBound and not self._item.isProgressionAutoBound
        if showInventoryCount and commonCount > 0 and isVehicleBound and not self._item.isRentable:
            subBlocks.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BOUND_ON_VEHICLE, tankname=self.__vehicle.shortUserName)), value=text_styles.concatStylesWithSpace(text_styles.stats(commonCount)), icon=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_TANK, padding=padding, titlePadding=titlePadding, iconPadding=formatters.packPadding(top=2)))
        return formatters.packBuildUpBlockData(blocks=subBlocks, gap=-1, padding=formatters.packPadding(top=-8, bottom=-15))

    def _countImageWidth(self):
        iconWidth = self.CUSTOMIZATION_TOOLTIP_ICON_WIDTH
        if self._item.isWide():
            if self._item.itemTypeID == GUI_ITEM_TYPE.INSCRIPTION:
                iconWidth = self.CUSTOMIZATION_TOOLTIP_ICON_WIDTH_WIDE
            elif self._item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
                iconWidth = self.CUSTOMIZATION_TOOLTIP_ICON_WIDTH_PERSONAL_NUMBER
            elif self._item.itemTypeID in (GUI_ITEM_TYPE.MODIFICATION, GUI_ITEM_TYPE.STYLE, GUI_ITEM_TYPE.PROJECTION_DECAL):
                iconWidth = self.CUSTOMIZATION_TOOLTIP_ICON_WIDTH_OTHER_BIG
        return iconWidth

    def _packIconBlock(self, isDim=False):
        width = self._countImageWidth()
        formfactor = ''
        if self._item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            formfactor = self._item.formfactor
        if self._item.isProgressive:
            if self._progressionLevel > 0:
                progressionLevel = self._progressionLevel
            else:
                progressionLevel = self._item.getLatestOpenedProgressionLevel(self.__vehicle)
                if progressionLevel <= 0:
                    return
            img = self._item.iconByProgressionLevel(progressionLevel)
        else:
            component = None
            img = self._item.getIconApplied(component)
        return formatters.packCustomizationImageBlockData(img=img, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=width, height=self.CUSTOMIZATION_TOOLTIP_ICON_HEIGHT, padding=formatters.packPadding(top=-5, bottom=-3, right=20), formfactor=formfactor, isDim=isDim)

    def _packBonusBlock(self, bonus, camo, isApplied):
        blocks = []
        bonusPercent = bonus.getFormattedValue(self.__vehicle)
        block = formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(text_styles.main(self.bonusDescription)), icon='+' + bonusPercent, isTextIcon=True)
        blocks.append(block)
        return formatters.packBuildUpBlockData(blocks, gap=-6, padding=formatters.packPadding(bottom=-5), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packLockedBlock(self):
        titleString = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_LOCKED_TITLE
        seasonString = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_LOCKED_SUMMER
        return formatters.packImageTextBlockData(title=text_styles.middleTitleLocked(_ms(titleString)), desc=text_styles.locked(_ms(seasonString)), img=RES_ICONS.MAPS_ICONS_LIBRARY_INFOTYPE_LOCKED)

    def _packDescriptionBlock(self):
        event = VEHICLE_CUSTOMIZATION.CAMOUFLAGE_EVENT_NAME
        eventName = text_styles.stats(event)
        desc = _ms(self._item.fullDescription, event=eventName)
        if not desc:
            return None
        else:
            blocks = [formatters.packTextBlockData(text=text_styles.main(desc))]
            return formatters.packBuildUpBlockData(blocks, gap=-6, padding=formatters.packPadding(bottom=-5))

    def _packUnsupportedBlock(self):
        if isRendererPipelineDeferred():
            return None
        else:
            hasGMTexture = self._item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL and self._item.descriptor.glossTexture
            if self._item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION or hasGMTexture:
                desc = backport.text(R.strings.vehicle_customization.customization.tooltip.warning.title())
                return formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.alertIcon()), imgPadding=formatters.packPadding(top=3, right=3), desc=text_styles.alert(desc))
            return None

    def _packProgressBlock(self):
        blocks = []
        unlockedLevel = self._item.getLatestOpenedProgressionLevel(self.__vehicle)
        if self._showOnlyProgressBlock:
            level = self._progressionLevel
        else:
            level = unlockedLevel + 1
        if level > self._item.getMaxProgressionLevel():
            return None
        else:
            if level == 1:
                titleDesc = backport.text(R.strings.vehicle_customization.customization.infotype.progression.achievementConditionFirstItem())
            else:
                titleDesc = backport.text(R.strings.vehicle_customization.customization.infotype.progression.achievementCondition(), level=int2roman(level))
            blocks.append(formatters.packTextBlockData(text=text_styles.middleTitle(titleDesc)))
            conditions = self._item.progressionConditions.get(level, []).get('conditions')
            if not conditions:
                return None
            if unlockedLevel > 0:
                showCurrentProgress = level == unlockedLevel + 1
            else:
                showCurrentProgress = level == 1
            desc = text_styles.concatStylesToMultiLine('', self.__packProgressDescriptionText(conditions[0], showCurrentProgress=showCurrentProgress))
            if not self._showOnlyProgressBlock:
                blocks.append(formatters.packImageTextBlockData(padding=formatters.packPadding(top=10, bottom=-10), img=self._item.iconByProgressionLevel(level), desc=desc, descPadding=formatters.packPadding(left=15), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGE_TEXT_BLOCK_PROGRESSIVE_LINKAGE))
            else:
                blocks.append(formatters.packTextBlockData(padding=formatters.packPadding(top=-19), text=desc))
            return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def __packProgressDescriptionText(self, condition, showCurrentProgress=False):
        vehicle = self.__vehicle
        conditionDescription = text_styles.main(condition.get('description', ''))
        currentProgressDescription = text_styles.concatStylesToSingleLine(text_styles.main(backport.text(R.strings.vehicle_customization.customization.infotype.progression.currentProgress())), text_styles.neutral(int(self._item.getCurrentProgressOnCurrentLevel(vehicle))), text_styles.main(backport.text(R.strings.vehicle_customization.customization.infotype.progression.maxProgress(), maxProgress=condition['value']))) if showCurrentProgress and 'value' in condition.keys() else ''
        return text_styles.concatStylesToMultiLine(conditionDescription, currentProgressDescription)

    def _packProgressStateBlock(self):
        currentLevel = self._item.getLatestOpenedProgressionLevel(self.__vehicle)
        if currentLevel == -1 and self._progressionLevel == 1:
            currentLevel = 0
        if self._progressionLevel < 1:
            return None
        else:
            if currentLevel >= self._progressionLevel:
                desc = text_styles.concatStylesToSingleLine(icons.checkmark(), text_styles.bonusAppliedText(getProgressionItemStatusText(self._progressionLevel)))
            elif currentLevel + 1 == self._progressionLevel:
                desc = text_styles.concatStylesToSingleLine(icons.inProgress(), text_styles.neutral(backport.text(R.strings.vehicle_customization.customization.infotype.progression.inProgressState())))
            else:
                desc = text_styles.concatStylesToSingleLine(icons.markerBlocked(), text_styles.error(backport.text(R.strings.vehicle_customization.customization.infotype.progression.notAvailableState.title())))
                desc = text_styles.concatStylesToMultiLine(desc, text_styles.main(backport.text(R.strings.vehicle_customization.customization.infotype.progression.notAvailableState.desc())))
            return formatters.packAlignedTextBlockData(text=desc, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def __packInheritorBlock(self, ancestors):
        getItemByCD = self.__itemsCache.items.getItemByCD
        quotedText = R.strings.vehicle_customization.quotedText
        blocks = [self.__packChainedBlockTitle(R.strings.vehicle_customization.customization.tooltip.chained.suitable()), self.__packDependentContentFormat(text=', '.join([ backport.text(quotedText(), getItemByCD(intCD).userName) for intCD in ancestors ]), icon=backport.image(R.images.gui.maps.icons.customization.customization_icon.c_16x16.camouflage()))]
        return formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(top=-3))

    def __packAncestorBlock(self, dependentItems):
        blocks = [self.__packChainedBlockTitle(R.strings.vehicle_customization.customization.tooltip.chained.default())]
        getItemByCD = self.__itemsCache.items.getItemByCD
        quotedText = R.strings.vehicle_customization.quotedText
        itemsBySlot = {}
        for intCD in dependentItems:
            item = getItemByCD(intCD)
            itemTabID = ITEM_TYPE_TO_TAB[item.itemTypeID]
            itemSlotType = CustomizationTabs.SLOT_TYPES[itemTabID]
            itemSlotName = GUI_ITEM_TYPE_NAMES[itemSlotType]
            if itemSlotName not in itemsBySlot.keys():
                itemsBySlot[itemSlotName] = [item.userName]
            itemsBySlot[itemSlotName].append(item.userName)

        image = R.images.gui.maps.icons.customization.customization_icon.c_16x16
        for key, value in itemsBySlot.iteritems():
            blocks.append(self.__packDependentContentFormat(text=', '.join([ backport.text(quotedText(), slotTypeName) for slotTypeName in value ]), icon=backport.image(image.dyn(key)())))

        return formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(top=-3))

    @staticmethod
    def __packChainedBlockTitle(title):
        icon = backport.image(R.images.gui.maps.icons.customization.chained_ico())
        titleText = text_styles.middleTitle(backport.text(title))
        return formatters.packImageTextBlockData(img=icon, title=titleText, imgPadding=formatters.packPadding(top=3, right=4))

    @staticmethod
    def __packDependentContentFormat(text, icon):
        titleText = text_styles.main(text)
        return formatters.packImageTextBlockData(img=icon, title=titleText, imgPadding=formatters.packPadding(top=3, right=4), ignoreImageSize=True, padding=formatters.packPadding(left=88, bottom=4))


class ElementIconTooltip(ElementTooltip):

    def __init__(self, context):
        super(ElementIconTooltip, self).__init__(context, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON)

    @staticmethod
    def _getCustomizationTypes():
        return {GUI_ITEM_TYPE.PAINT, GUI_ITEM_TYPE.CAMOUFLAGE, GUI_ITEM_TYPE.MODIFICATION}

    def _packBonusBlock(self, bonus, camo, isApplied):
        return super(ElementIconTooltip, self)._packBonusBlock(bonus, camo, True)


class ElementAwardTooltip(ElementTooltip):

    def __init__(self, context):
        super(ElementAwardTooltip, self).__init__(context, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD)

    def _packBonusBlock(self, bonus, camo, isApplied):
        blocks = []
        bonusDescription = self.bonusDescription
        if self._item.itemTypeName == 'style':
            bonusDescription = VEHICLE_CUSTOMIZATION.ELEMENTAWARDTOOLTIP_DESCRIPTION_STYLE
        elif self._item.itemTypeName == 'camouflage':
            bonusDescription = VEHICLE_CUSTOMIZATION.ELEMENTAWARDTOOLTIP_DESCRIPTION_CAMOUFLAGE
        bonusPercent = '{min:.0f}-{max:.0f}%'.format(min=CamouflageBonus.MIN * 100, max=CamouflageBonus.MAX * 100)
        blocks.append(formatters.packCustomizationCharacteristicBlockData(text=text_styles.main(text_styles.main(bonusDescription)), icon=bonusPercent, isTextIcon=True, padding=formatters.packPadding(right=20)))
        return formatters.packBuildUpBlockData(blocks, gap=-6, padding=formatters.packPadding(bottom=-5), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class ElementPurchaseTooltip(ElementTooltip):

    def __init__(self, context):
        super(ElementPurchaseTooltip, self).__init__(context, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE)

    @staticmethod
    def _getCustomizationTypes():
        return {GUI_ITEM_TYPE.PAINT, GUI_ITEM_TYPE.CAMOUFLAGE, GUI_ITEM_TYPE.MODIFICATION}

    def _packBonusBlock(self, bonus, camo, isApplied):
        return super(ElementPurchaseTooltip, self)._packBonusBlock(bonus, camo, True)

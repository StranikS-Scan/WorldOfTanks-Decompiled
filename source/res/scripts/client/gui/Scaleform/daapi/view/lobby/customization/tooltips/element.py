# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/tooltips/element.py
import nations
import BigWorld
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.Scaleform import getNationsFilterAssetPath
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.shared import getItemInventoryCount
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_TAGS
from gui.shared.items_parameters import params_helper, formatters as params_formatters
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from items.components.c11n_constants import SeasonType
from items.vehicles import VEHICLE_CLASS_TAGS
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache

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


class ElementTooltip(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, context):
        super(ElementTooltip, self).__init__(context, TOOLTIP_TYPE.TECH_CUSTOMIZATION)
        self._setContentMargin(top=20, left=19, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(387)
        self._item = None
        self._isQuestReward = False
        return

    def _packBlocks(self, *args):
        itemIntCD = first(args)
        if len(args) == 1:
            self._isQuestReward = False
        else:
            self._isQuestReward = True
        self._item = self.itemsCache.items.getItemByCD(itemIntCD)
        return self._packItemBlocks()

    def _packItemBlocks(self):
        isDeferredRenderer = self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == 0
        topBlocks = [self._packTitleBlock(), self._packIconBlock()]
        items = [formatters.packBuildUpBlockData(blocks=topBlocks, gap=10)]
        camo = None
        if self._item.itemTypeID != GUI_ITEM_TYPE.STYLE:
            bonus = self._item.bonus
        else:
            for container in (self._item.getOutfit(season).hull for season in SeasonType.SEASONS):
                camo = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItem()
                if camo and camo.bonus:
                    bonus = camo.bonus
                    break
            else:
                bonus = None

        if bonus:
            camo = self._item if not camo else camo
            items.append(self._packBonusBlock(bonus, camo))
        if not self._item.isHistorical() or self._item.fullDescription:
            items.append(self._packDescriptionBlock())
        if not self._isQuestReward:
            items.append(self._packInventoryBlock())
        if not self._item.isUnlocked:
            items.append(self._packLockedBlock())
        if self._item.descriptor.filter:
            block = self._packSuitableBlock()
            if block:
                items.append(block)
        if self._item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION and not isDeferredRenderer:
            items.append(self._packUnsupportedBlock())
        return items

    def _packTitleBlock(self):
        if self._item.isAllSeason():
            mapType = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_ANY
        elif self._item.isSummer():
            mapType = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_SUMMER
        elif self._item.isWinter():
            mapType = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_WINTER
        elif self._item.isDesert():
            mapType = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_DESERT
        else:
            mapType = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_EMPTYSLOT
        desc = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_DESCRIPTION_MAP, mapType=text_styles.stats(mapType))
        if self._item.groupUserName:
            desc = text_styles.concatStylesToSingleLine(desc, _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_DESCRIPTION_TYPE, elementType=text_styles.stats(self._item.groupUserName)))
        return formatters.packItemTitleDescBlockData(title=text_styles.highTitle(self._item.userName), desc=text_styles.main(desc), highlightPath=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_CORNER_RARE, img=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_BRUSH_RARE, imgPadding={'top': 15,
         'left': 8}, padding={'top': -20,
         'left': -19,
         'bottom': -7}, txtPadding={'top': 20,
         'left': -8}, descPadding={'left': -25,
         'top': 17}) if self._item.isRare() else formatters.packTitleDescBlock(title=text_styles.highTitle(self._item.userName), desc=text_styles.main(desc), descPadding={'top': -5})

    def _packInventoryBlock(self):
        container = self.app.containerManager.getContainer(ViewTypes.LOBBY_SUB)
        view = container.getView()
        if view.alias == VIEW_ALIAS.LOBBY_CUSTOMIZATION:
            getInventoryCount = view.getItemInventoryCount
        else:
            getInventoryCount = getItemInventoryCount
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_TITLE), padding={'bottom': 4})]
        money = self.itemsCache.items.stats.money
        if not self._item.isHidden:
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
                subBlocks.append(makePriceBlock(value, setting(currency), needValue if needValue > 0 else None, defValue if defValue > 0 else None, actionPercent, valueWidth=88, leftPadding=49, forcedText=forcedText))

            if not self._item.isRentable:
                for itemPrice in self._item.sellPrices:
                    currency = itemPrice.getCurrency()
                    value = itemPrice.price.getSignValue(currency)
                    defValue = itemPrice.defPrice.getSignValue(currency)
                    actionPercent = itemPrice.getActionPrc()
                    if actionPercent > 0:
                        subBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.ACTIONPRICE_SELL_BODY_SIMPLE), value=text_styles.concatStylesToSingleLine(text_styles.credits(BigWorld.wg_getIntegralFormat(value)), '    ', icons.credits()), icon='alertMedium', valueWidth=88, padding=formatters.packPadding(left=-5)))
                    subBlocks.append(makePriceBlock(value, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=defValue if defValue > 0 else None, percent=actionPercent, valueWidth=88, leftPadding=49))

        inventoryCount = getInventoryCount(self._item)
        info = text_styles.concatStylesWithSpace(text_styles.stats(inventoryCount))
        if self._item.isRentable and inventoryCount > 0 or not self._item.isRentable:
            title = text_styles.main(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_RENT_BATTLESLEFT if self._item.isRentable else VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_AVAILABLE)
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_CLOCKICON_1 if self._item.isRentable else RES_ICONS.MAPS_ICONS_CUSTOMIZATION_STORAGE_ICON
            padding = formatters.packPadding(left=83, bottom=-14 if self._item.isRentable else 0)
            titlePadding = formatters.packPadding(left=-8 if self._item.isRentable else -1)
            iconPadding = formatters.packPadding(top=-7 if self._item.isRentable else -2, left=-3 if self._item.isRentable else -2)
            subBlocks.append(formatters.packTitleDescParameterWithIconBlockData(title=title, value=info, icon=icon, padding=padding, titlePadding=titlePadding, iconPadding=iconPadding))
        return formatters.packBuildUpBlockData(blocks=subBlocks, gap=-1)

    def _packIconBlock(self):
        width = 102
        if self._item.isWide():
            width = 204 if self._item.itemTypeName == 'inscription' else 278
        return formatters.packImageBlockData(img=self._item.icon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=width, height=102, padding={'bottom': 2})

    def _packBonusBlock(self, bonus, camo):
        blocks = []
        vehicle = g_currentVehicle.item
        bonusPercent = bonus.getFormattedValue(vehicle)
        blocks.append(formatters.packImageTextBlockData(title=text_styles.bonusLocalInfoTipText(text_styles.concatStylesToSingleLine('+', bonusPercent)), img=RES_ICONS.MAPS_ICONS_LIBRARY_QUALIFIERS_48X48_CAMOUFLAGE, imgPadding={'left': 12,
         'top': -8}, txtPadding={'top': -4}, txtOffset=69))
        blocks.append(formatters.packTextBlockData(text=text_styles.main(camo.bonus.description), padding={'top': -46,
         'left': 110}))
        stockVehicle = self.itemsCache.items.getStockVehicle(vehicle.intCD)
        comparator = params_helper.camouflageComparator(vehicle, camo)
        stockParams = params_helper.getParameters(stockVehicle)
        padding = formatters.packPadding(left=105, top=2, bottom=-6)
        simplifiedBlocks = SimplifiedStatsBlockConstructor(stockParams, comparator, padding).construct()
        if simplifiedBlocks:
            blocks.extend(simplifiedBlocks)
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packLockedBlock(self):
        titleString = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_LOCKED_TITLE
        seasonString = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_LOCKED_SUMMER
        return formatters.packImageTextBlockData(title=text_styles.middleTitleLocked(_ms(titleString)), desc=text_styles.locked(_ms(seasonString)), img=RES_ICONS.MAPS_ICONS_LIBRARY_INFOTYPE_LOCKED)

    def _packDescriptionBlock(self):
        if self._item.isHistorical():
            img = None
            title = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_DESCRIPTION_HISTORIC_TRUE
            desc = self._item.fullDescription
        else:
            img = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_NON_HISTORICAL
            title = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_DESCRIPTION_HISTORIC_FALSE
            desc = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_DESCRIPTION_HISTORIC_FALSE_DESCRIPTION
        blocks = [formatters.packImageTextBlockData(title=text_styles.middleTitle(title), img=img, imgPadding={'left': -3,
          'top': -4}), formatters.packTextBlockData(text=text_styles.main(desc))]
        if not self._item.isHistorical() and self._item.fullDescription:
            blocks.insert(0, formatters.packTextBlockData(text=text_styles.main(self._item.fullDescription), padding={'bottom': 40}))
        return formatters.packBuildUpBlockData(blocks, gap=-6 if img is not None else 3, padding={'bottom': -5})

    def _packSuitableBlock(self):
        blocks = []
        for node in self._item.descriptor.filter.include:
            conditions = []
            separator = ''.join(['&nbsp;&nbsp;', icons.makeImageTag(RES_ICONS.MAPS_ICONS_CUSTOMIZATION_TOOLTIP_SEPARATOR, 3, 21, -6), '  '])
            if node.levels:
                conditions.append(text_styles.main(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SUITABLE_TIER))
                for level in node.levels:
                    conditions.append(text_styles.stats(int2roman(level)))
                    conditions.append(text_styles.stats(',&nbsp;'))

                conditions = conditions[:-1]
                conditions.append(separator)
            if node.nations:
                for nation in node.nations:
                    name = nations.NAMES[nation]
                    conditions.append(icons.makeImageTag(getNationsFilterAssetPath(name), 26, 16, -4))
                    conditions.append('  ')

                conditions = conditions[:-1]
                conditions.append(separator)
            if node.tags:
                for vehType in VEHICLE_TYPES_ORDER:
                    if vehType in node.tags:
                        conditions.append(icons.makeImageTag(RES_ICONS.getFilterVehicleType(vehType), 27, 17, -4))

                if VEHICLE_CLASS_TAGS & node.tags:
                    conditions.append(separator)
                if VEHICLE_TAGS.PREMIUM in node.tags:
                    conditions.append(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_PREM_SMALL_ICON, 20, 17, -4))
                    conditions.append(separator)
                if VEHICLE_TAGS.PREMIUM_IGR in node.tags:
                    conditions.append(icons.premiumIgrSmall())
                    conditions.append(separator)
            if not conditions:
                continue
            icn = text_styles.concatStylesToSingleLine(*conditions[:-1])
            blocks.append(formatters.packTextBlockData(text=icn, padding={'top': -2}))
            blocks.append(formatters.packTextBlockData(text=text_styles.neutral(VEHICLE_CUSTOMIZATION.FILTER_OR), padding={'top': -4}))

        if not blocks:
            return None
        else:
            blocks.insert(0, formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SUITABLE_TITLE)))
            return formatters.packBuildUpBlockData(blocks=blocks[:-1], padding={'top': -3})

    def _packUnsupportedBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.statusAlert(icons.alert(-3) + ' ' + _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WARNING_TITLE)), desc=text_styles.standard(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WARNING_REASON_FORWARD), padding={'top': -2})

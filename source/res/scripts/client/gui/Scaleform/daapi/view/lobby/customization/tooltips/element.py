# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/tooltips/element.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.customization.shared import getItemInventoryCount, getItemAppliedCount, makeVehiclesShortNamesString, getSuitableText
from gui.customization.shared import SEASON_TYPE_TO_NAME
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization.shared import PROJECTION_DECAL_IMAGE_FORM_TAG, PROJECTION_DECAL_TEXT_FORM_TAG
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.packers import pickPacker
from gui.shared.items_parameters import params_helper, formatters as params_formatters
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_constants import SeasonType
from items.vehicles import CamouflageBonus
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from items.components.c11n_constants import ProjectionDecalFormTags

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


class NonHistoricTooltip(BlocksTooltipData):
    service = dependency.descriptor(ICustomizationService)
    isNonHistoric = False
    isInfo = False
    isCustomStyleMode = False

    def __init__(self, context):
        super(NonHistoricTooltip, self).__init__(context, TOOLTIP_TYPE.TECH_CUSTOMIZATION)
        self._setContentMargin(top=20, left=19, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(440)

    def _packBlocks(self, isNonHistoric, isInfo, isCustomStyleMode):
        self.isNonHistoric = isNonHistoric
        self.isInfo = isInfo
        self.isCustomStyleMode = isCustomStyleMode
        return self._packItemBlocks()

    def _packItemBlocks(self):
        items = []
        items.append(self._packDescriptionBlock())
        return items

    def _packDescriptionBlock(self):
        img = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_NON_HISTORICAL
        nonHistoricTitle = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_HISTORICCHECKBOX_ITEMS
        nonHistoricDesc = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_DESCRIPTION_HISTORIC_FALSE_DESCRIPTION
        if self.isCustomStyleMode:
            seasonName = SEASON_TYPE_TO_NAME.get(self.service.getCtx().currentSeason)
            mapName = _ms(VEHICLE_CUSTOMIZATION.getMapName(seasonName))
        else:
            mapName = _ms(VEHICLE_CUSTOMIZATION.SEASON_SELECTION_MAPNAME_ALL)
        title = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_BTN)
        desc = _ms(VEHICLE_CUSTOMIZATION.SEASON_SELECTION_TOOLTIP, mapName=mapName)
        blocks = []
        if not self.isInfo:
            blocks.append(formatters.packTextBlockData(text=text_styles.middleTitle(title)))
            blocks.append(formatters.packTextBlockData(text=text_styles.main(desc), padding={'top': 10}))
        if self.isNonHistoric:
            blocks.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(nonHistoricTitle), img=img, imgPadding={'left': -3,
             'top': -4}, padding={'top': 20 if not self.isInfo else 0}))
            blocks.append(formatters.packTextBlockData(text=text_styles.main(nonHistoricDesc)))
        return formatters.packBuildUpBlockData(blocks, gap=-6, padding={'bottom': -5})


class ElementTooltip(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    service = dependency.descriptor(ICustomizationService)
    CUSTOMIZATION_TOOLTIP_WIDTH = 446
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH = 104
    CUSTOMIZATION_TOOLTIP_ICON_HEIGHT = 104
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH_WIDE = 204
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH_OTHER_BIG = 228
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH_INSCRIPTION = 278
    CUSTOMIZATION_TOOLTIP_ICON_WIDTH_PERSONAL_NUMBER = 390

    def __init__(self, context, tooltipType=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM):
        super(ElementTooltip, self).__init__(context, tooltipType)
        self._setContentMargin(top=20, left=19, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(self.CUSTOMIZATION_TOOLTIP_WIDTH)
        self._item = None
        self._specialArgs = None
        self._isUnsupportedForm = None
        self._appliedCount = 0
        self.__ctx = None
        return

    def _packBlocks(self, *args):
        self._item = self.itemsCache.items.getItemByCD(args[0])
        statsConfig = self.context.getStatsConfiguration(self._item)
        self.__ctx = self.service.getCtx()
        if len(args) > 1:
            showInventoryBlock = args[1]
            statsConfig.buyPrice = showInventoryBlock
            statsConfig.sellPrice = showInventoryBlock
            statsConfig.inventoryCount = showInventoryBlock
        self._isUnsupportedForm = args[2] if len(args) > 2 else False
        self._specialArgs = args[3] if len(args) > 3 else []
        return self._packItemBlocks(statsConfig)

    def _packItemBlocks(self, statsConfig):
        self.bonusDescription = VEHICLE_CUSTOMIZATION.BONUS_CONDITION_SEASON
        topBlocks = [self._packTitleBlock(), self._packIconBlock(self._item.isHistorical(), self._item.isDim())]
        items = [formatters.packBuildUpBlockData(blocks=topBlocks, gap=10)]
        self.currentVehicle = g_currentVehicle.item
        self.boundVehs = [ vehicleCD for vehicleCD in self._item.boundInventoryCount if vehicleCD != -1 ]
        self.installedToVehs = self._item.getInstalledVehicles()
        self.installedCount = self._item.getInstalledOnVehicleCount(self.currentVehicle.intCD)
        camo = None
        self._appliedCount = 0
        bonusEnabled = False
        if self._item.itemTypeID != GUI_ITEM_TYPE.STYLE:
            bonus = self._item.bonus
            if self.__ctx is not None:
                self._appliedCount = getItemAppliedCount(self._item, self.__ctx.getOutfitsInfo())
                hullContainer = self.__ctx.currentOutfit.hull
                bonusEnabled = hullContainer.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItem() == self._item
        else:
            self.bonusDescription = VEHICLE_CUSTOMIZATION.BONUS_STYLE
            for container in (self._item.getOutfit(season).hull for season in SeasonType.SEASONS if self._item.getOutfit(season)):
                camo = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItem()
                if camo and camo.bonus:
                    bonus = camo.bonus
                    break
            else:
                bonus = None

            if self.__ctx is not None:
                originalStyle = self.__ctx.originalStyle
                modifiedStyle = self.__ctx.modifiedStyle
                if modifiedStyle:
                    isApplied = self._item == modifiedStyle
                else:
                    isApplied = self._item == originalStyle
                bonusEnabled = bonus is not None and isApplied
                self._appliedCount = int(isApplied)
        if bonus and statsConfig.showBonus:
            camo = self._item if not camo else camo
            items.append(self._packBonusBlock(bonus, camo, bonusEnabled))
        if not self._item.isHistorical() or self._item.fullDescription:
            block = self._packDescriptionBlock()
            if block:
                items.append(block)
        if statsConfig.buyPrice or statsConfig.sellPrice or statsConfig.inventoryCount:
            inventoryBlocks = self._packInventoryBlock(statsConfig.buyPrice, statsConfig.sellPrice, statsConfig.inventoryCount)
            if inventoryBlocks['data']['blocksData']:
                items.append(inventoryBlocks)
        if not self._item.isUnlocked:
            items.append(self._packLockedBlock())
        if self._item.descriptor.filter:
            block = self._packSuitableBlock()
            if block:
                items.append(block)
        if not self._item.isVehicleBound and (self._item.isHidden or self._item.isLimited):
            block = self._packAppliedBlock()
            if block:
                items.append(block)
        if self._isUnsupportedForm:
            items.append(self._packUnsupportedFormBlock())
        if self._item.isVehicleBound or self._item.isLimited:
            block = self._packSpecialBlock()
            if block:
                items.append(block)
        if self._item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION and not isRendererPipelineDeferred():
            items.append(self._packUnsupportedBlock())
        return items

    def _packSuitableBlock(self):
        blocks = []
        if not self._item.descriptor.filter.include:
            return None
        elif self._item.isVehicleBound and not self._item.mayApply:
            return formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SUITABLE_TITLE), desc=text_styles.main(makeVehiclesShortNamesString(set(self.boundVehs + self.installedToVehs), self.currentVehicle)), padding=formatters.packPadding(top=-2))
        else:
            icn = getSuitableText(self._item, self.currentVehicle)
            blocks.append(formatters.packTextBlockData(text=icn, padding=formatters.packPadding(top=-2)))
            blocks.insert(0, formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SUITABLE_TITLE)))
            return formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(top=-3))

    def _packAppliedBlock(self):
        vehicles = set(self.installedToVehs)
        if self._appliedCount > 0:
            vehicles.add(self.currentVehicle.intCD)
        elif not self.installedToVehs:
            return None
        if self._item.mayApply or self.currentVehicle.intCD in self.installedToVehs:
            return formatters.packTitleDescBlock(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LIMITED_ON_VEHICLE), desc=text_styles.main(makeVehiclesShortNamesString(vehicles, self.currentVehicle)), padding=formatters.packPadding(top=-2))
        else:
            blocks = [formatters.packImageTextBlockData(title=text_styles.critical(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LIMITED_ON_OTHER_VEHICLE), img=RES_ICONS.MAPS_ICONS_LIBRARY_MARKER_BLOCKED, imgPadding=formatters.packPadding(left=-3, top=2)), formatters.packTextBlockData(text=text_styles.main(_ms(makeVehiclesShortNamesString(vehicles, self.currentVehicle))))]
            return formatters.packBuildUpBlockData(blocks, gap=3, padding=formatters.packPadding(bottom=-5))

    def _packUnsupportedFormBlock(self):
        blocks = [formatters.packImageTextBlockData(title=text_styles.critical(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_UNSUPPORTEDFORM), img=RES_ICONS.MAPS_ICONS_LIBRARY_MARKER_BLOCKED, imgPadding=formatters.packPadding(left=-3, right=5, top=2)), formatters.packTextBlockData(text=text_styles.main(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_UNSUPPORTEDFORM_DESCR))]
        return formatters.packBuildUpBlockData(blocks, gap=3, padding=formatters.packPadding(bottom=-5))

    def _packSpecialBlock(self):
        blocks = []
        specials = []
        if self._item.isVehicleBound and self._item.mayApply:
            if self._item.isRentable:
                specials.append(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_RENT_SPECIAL_TEXT))
            else:
                specials.append(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BOUND_SPECIAL_TEXT))
        if self._item.isLimited:
            purchaseLimit = self.__ctx.getPurchaseLimit(self._item) if self.__ctx is not None else self._item.buyCount
            if self._item.buyCount > 0 and (purchaseLimit > 0 or self._appliedCount > 0):
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
        if self._item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            formIconSource = PROJECTION_DECAL_IMAGE_FORM_TAG[self._item.formfactor]
            iconSize = 39
            if self._item.formfactor == ProjectionDecalFormTags.SQUARE:
                iconSize = 9
            elif self._item.formfactor == ProjectionDecalFormTags.RECT1X2:
                iconSize = 15
            elif self._item.formfactor == ProjectionDecalFormTags.RECT1X3:
                iconSize = 21
            elif self._item.formfactor == ProjectionDecalFormTags.RECT1X4:
                iconSize = 27
            desc = text_styles.concatStylesToSingleLine(desc, '{desc} {form} '.format(desc=backport.text(R.strings.vehicle_customization.element.formIconSource()), form=text_styles.stats(PROJECTION_DECAL_TEXT_FORM_TAG[self._item.formfactor])), icons.makeImageTag(formIconSource, iconSize, 9, 0))
        title = self._item.userName
        tooltipKey = TOOLTIPS.getItemBoxTooltip(self._item.itemTypeName)
        if tooltipKey:
            title = _ms(tooltipKey, group=self._item.userType, value=self._item.userName)
        return formatters.packItemTitleDescBlockData(title=text_styles.highTitle(title), desc=text_styles.main(desc), highlightPath=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_CORNER_RARE, img=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_BRUSH_RARE, imgPadding=formatters.packPadding(top=15, left=8), padding=formatters.packPadding(top=-20, left=-19, bottom=-7), txtPadding=formatters.packPadding(top=20, left=-8), descPadding=formatters.packPadding(top=25, left=-8)) if self._item.isRare() else formatters.packTitleDescBlock(title=text_styles.highTitle(title), desc=text_styles.main(desc), descPadding=formatters.packPadding(top=-5))

    def _packInventoryBlock(self, showBuyPrice, showSellPrice, showInventoryCount):
        subBlocks = []
        money = self.itemsCache.items.stats.money
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
                    subBlocks.append(makePriceBlock(value, setting(currency), needValue if needValue > 0 else None, defValue if defValue > 0 else None, actionPercent, valueWidth=88, leftPadding=49, forcedText=forcedText))

        if showSellPrice and not (self._item.isHidden or self._item.isRentable):
            for itemPrice in self._item.sellPrices:
                currency = itemPrice.getCurrency()
                value = itemPrice.price.getSignValue(currency)
                defValue = itemPrice.defPrice.getSignValue(currency)
                actionPercent = itemPrice.getActionPrc()
                if actionPercent > 0:
                    subBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.ACTIONPRICE_SELL_BODY_SIMPLE), value=text_styles.concatStylesToSingleLine(text_styles.credits(backport.getIntegralFormat(value)), '    ', icons.credits()), icon='alertMedium', valueWidth=88, padding=formatters.packPadding(left=-5)))
                subBlocks.append(makePriceBlock(value, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=defValue if defValue > 0 else None, percent=actionPercent, valueWidth=88, leftPadding=49))

        if self.__ctx is not None:
            inventoryCount = self.__ctx.getItemInventoryCount(self._item)
        else:
            inventoryCount = getItemInventoryCount(self._item)
        info = text_styles.concatStylesWithSpace(text_styles.stats(inventoryCount))
        padding = formatters.packPadding(left=83, bottom=0)
        titlePadding = formatters.packPadding(left=-1)
        if showInventoryCount and inventoryCount > 0:
            if self._item.isRentable:
                textKey = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_RENT_BATTLESLEFT
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_CLOCKICON_1
                autoRentEnabled = self.__ctx.autoRentEnabled() if self.__ctx is not None else False
                if self._item.isRented and autoRentEnabled:
                    textKey = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_INVENTORY_RENT_BATTLESLEFT_AUTOPROLONGATIONON
                    icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_ICON_RENT
                title = text_styles.main(_ms(textKey, tankname=g_currentVehicle.item.shortUserName))
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
        boundCount = self._item.boundInventoryCount.get(self.currentVehicle.intCD, 0)
        commonCount = boundCount + self.installedCount
        if showInventoryCount and commonCount > 0 and self._item.isVehicleBound and not self._item.isRentable:
            subBlocks.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BOUND_ON_VEHICLE, tankname=g_currentVehicle.item.shortUserName)), value=text_styles.concatStylesWithSpace(text_styles.stats(commonCount)), icon=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_TANK, padding=padding, titlePadding=titlePadding, iconPadding=formatters.packPadding(top=2)))
        return formatters.packBuildUpBlockData(blocks=subBlocks, gap=-1)

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

    def _packIconBlock(self, isHistorical=False, isDim=False):
        width = self._countImageWidth()
        if self._specialArgs:
            component = pickPacker(self._item.itemTypeID).getRawComponent()(*self._specialArgs)
        else:
            component = None
        formfactor = ''
        if self._item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            formfactor = self._item.formfactor
        return formatters.packCustomizationImageBlockData(img=self._item.getIconApplied(component), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGE_BLOCK_NON_HISTORICAL_LINKAGE, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=width, height=self.CUSTOMIZATION_TOOLTIP_ICON_HEIGHT, padding=formatters.packPadding(bottom=2), isHistorical=isHistorical, formfactor=formfactor, isDim=isDim)

    def _packBonusBlock(self, bonus, camo, isApplied):
        blocks = []
        vehicle = g_currentVehicle.item
        bonusPercent = bonus.getFormattedValue(vehicle)
        blocks.append(formatters.packImageTextBlockData(title=text_styles.bonusLocalInfoTipText(text_styles.concatStylesToSingleLine('+', bonusPercent)), img=RES_ICONS.MAPS_ICONS_VEHPARAMS_BIG_INVISIBILITYSTILLFACTOR, imgPadding=formatters.packPadding(top=-8, left=12), txtPadding=formatters.packPadding(top=-4), txtOffset=69))
        blocks.append(formatters.packTextBlockData(text=text_styles.main(self.bonusDescription), padding=formatters.packPadding(top=-46, left=110)))
        stockVehicle = self.itemsCache.items.getStockVehicle(vehicle.intCD)
        comparator = params_helper.camouflageComparator(stockVehicle, camo)
        stockParams = params_helper.getParameters(stockVehicle)
        padding = formatters.packPadding(left=105, top=2, bottom=-6)
        simplifiedBlocks = SimplifiedStatsBlockConstructor(stockParams, comparator, padding).construct()
        if simplifiedBlocks and not isApplied:
            blocks.extend(simplifiedBlocks)
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

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
        return formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON, imgPadding=formatters.packPadding(top=3, right=3), desc=text_styles.alert(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WARNING_TITLE)))


class ElementIconTooltip(ElementTooltip):

    def __init__(self, context):
        super(ElementIconTooltip, self).__init__(context, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON)

    def _packBonusBlock(self, bonus, camo, isApplied):
        return super(ElementIconTooltip, self)._packBonusBlock(bonus, camo, True)

    def _packSuitableBlock(self):
        return None


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
        blocks.append(formatters.packImageTextBlockData(title=text_styles.bonusLocalInfoTipText(bonusPercent), img=RES_ICONS.MAPS_ICONS_VEHPARAMS_BIG_INVISIBILITYSTILLFACTOR, imgPadding=formatters.packPadding(top=-8, left=12), txtPadding=formatters.packPadding(top=-4), txtOffset=69))
        blocks.append(formatters.packTextBlockData(text=text_styles.main(bonusDescription), padding=formatters.packPadding(top=-55, left=120)))
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class ElementPurchaseTooltip(ElementTooltip):

    def __init__(self, context):
        super(ElementPurchaseTooltip, self).__init__(context, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE)

    def _packBonusBlock(self, bonus, camo, isApplied):
        return super(ElementPurchaseTooltip, self)._packBonusBlock(bonus, camo, True)

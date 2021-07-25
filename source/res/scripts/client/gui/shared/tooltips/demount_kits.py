# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/demount_kits.py
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.goodies.goodie_items import DemountKit
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, _logger
from gui.shared.money import Currency
from gui.shared.tooltips import TOOLTIP_TYPE, ToolTipBaseData
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.wgm_currency import WGMCurrencyTooltip
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache

class GoldToolTipData(BlocksTooltipData):
    _itemsCache = dependency.descriptor(IItemsCache)
    _WIDTH = 320
    _TOP = 17
    _LEFT = 20
    _BOTTOM = 18
    _RIGHT = 13
    _ICON_Y_OFFSET = 2
    _LEFT_PADDING = 20

    def __init__(self, ctx):
        super(GoldToolTipData, self).__init__(ctx, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI)
        self._setContentMargin(top=self._TOP, left=self._LEFT, bottom=self._BOTTOM, right=self._RIGHT)
        self._setMargins(afterBlock=14)
        self._setWidth(self._WIDTH)
        from gui.Scaleform.genConsts import CURRENCIES_CONSTANTS
        self._btnType = CURRENCIES_CONSTANTS.CURRENCIES_CONSTANTS.GOLD

    def _packBlocks(self, btnType=None, *args, **kwargs):
        tooltipBlocks = super(GoldToolTipData, self)._packBlocks(*args, **kwargs)
        if self._btnType is None:
            _logger.error('HeaderMoneyAndXpTooltipData empty btnType!')
            return tooltipBlocks
        else:
            valueBlock = formatters.packMoneyAndXpValueBlock(value=text_styles.gold(backport.getIntegralFormat(self._itemsCache.items.stats.money.gold)), icon=self._btnType, iconYoffset=self._ICON_Y_OFFSET)
            return formatters.packMoneyAndXpBlocks(tooltipBlocks, btnType=self._btnType, valueBlocks=[valueBlock], alternativeData={'btnClickDesc': 'goldAlternative',
             'btnClickDescAlign': BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT})


class GoldStatsToolTipData(WGMCurrencyTooltip):

    def _getAlternativeData(self):
        return {'btnClickDesc': 'goldAlternative',
         'btnClickDescAlign': BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT}


class DemountKitToolTipData(BlocksTooltipData):
    _WIDTH = 320

    def __init__(self, context):
        super(DemountKitToolTipData, self).__init__(context, TOOLTIP_TYPE.DEMOUNT_KIT)
        self._setContentMargin(top=15, left=19, bottom=21, right=13)
        self._setMargins(afterBlock=14)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(DemountKitToolTipData, self)._packBlocks(*args, **kwargs)
        self._item = self.context.buildItem(*args, **kwargs)
        items.append(self._packHeader())
        items.append(self._packDescription())
        items.append(self._packInventoryBlock())
        return items

    def _packHeader(self):
        image = formatters.packImageBlockData(self._item.iconInfo, BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(left=3, top=3))
        message = formatters.packTextBlockData(text_styles.highTitle(self._item.userName), useHtml=True, padding=formatters.packPadding(left=5, right=5))
        block = formatters.packBuildUpBlockData(blocks=[image, message], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL)
        return block

    def _packDescription(self):
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.effect())), desc=text_styles.main(self._item.longDescription), blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packInventoryBlock(self):
        count = self._item.inventoryCount
        valueFormatter = text_styles.critical if count == 0 else text_styles.stats
        return formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(backport.text(R.strings.tooltips.vehicle.inventoryCount())), value=valueFormatter(count), icon=backport.image(R.images.gui.maps.icons.library.storage_icon()), padding=formatters.packPadding(left=105), titlePadding=formatters.packPadding(left=-2), iconPadding=formatters.packPadding(top=-2, left=-2))


class NotEnoughMoneyTooltipData(ToolTipBaseData):
    gui = dependency.descriptor(IGuiLoader)
    RESOURCES_BY_CURRENCY = {Currency.CREDITS: (R.strings.tooltips.moduleFits.credits_error.header(), R.strings.tooltips.moduleFits.credits_error.text(), R.images.gui.maps.icons.library.CreditsIcon_2()),
     Currency.CRYSTAL: (R.strings.demount_kit.equipmentDemount.notEnoughBonds.text(), R.strings.demount_kit.equipmentDemount.notEnoughBonds.description(), R.images.gui.maps.icons.library.CrystalIcon_2()),
     Currency.GOLD: (R.strings.tooltips.moduleFits.gold_error.header(), R.strings.tooltips.moduleFits.gold_error.text(), R.images.gui.maps.icons.library.GoldIcon_2())}

    def __init__(self, context):
        super(NotEnoughMoneyTooltipData, self).__init__(context, TOOLTIP_TYPE.DEMOUNT_KIT)

    def getDisplayableData(self, value, currencyType):
        header, body, icon = self.RESOURCES_BY_CURRENCY.get(currencyType, ('', '', ''))
        formattedBody = makeHtmlString('html_templates:lobby/tooltips', 'not_enough_money', {'description': backport.text(body),
         'value': text_styles.error(self.gui.systemLocale.getNumberFormat(value)),
         'icon': backport.image(icon)})
        return {'header': backport.text(header),
         'body': formattedBody}

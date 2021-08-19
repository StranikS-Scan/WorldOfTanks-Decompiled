# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/referral_program/awards.py
import logging
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.daapi.view.lobby.vehicle_preview.items_kit_helper import lookupItem, getCDFromId, getItemIcon, getItemTitle
from web.web_client_api.common import ItemPackEntry, ItemPackType, ItemPackTypeGroup
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from skeletons.gui.shared import IItemsCache
from skeletons.gui.goodies import IGoodiesCache
_logger = logging.getLogger(__name__)
_ICON_SIZE = '48x48'

class AwardsTooltipData(BlocksTooltipData):
    _TOOLTIP_MIN_WIDTH = 340
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __resPath = R.strings.tooltips.referralProgram.newLevelAwards

    def __init__(self, context):
        super(AwardsTooltipData, self).__init__(context, TOOLTIP_TYPE.REFERRAL_PROGRAMM)
        self.__shieldStatus = None
        self.item = None
        self._setContentMargin(top=19, bottom=25, left=25, right=15)
        self._setMargins(10, 0)
        self._setWidth(self._TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        data = args[0] if args else []
        return self.__packHeader('') if not data else [self.__packHeader()] + [self.__packItemBlock(data.get('items', []))]

    def __packHeader(self):
        name = backport.text(self.__resPath.header())
        description = backport.text(self.__resPath.description())
        return formatters.packTitleDescBlock(title=text_styles.highTitle(name), desc=text_styles.main(description), padding=formatters.packPadding(left=0, right=0))

    def __packItemBlock(self, items):
        blocks = []
        for itemData in items:
            count = itemData.get('count', 0)
            itemId = itemData.get('id', 0)
            itemType = itemData.get('type', '')
            icon, title = self.__getItemData(itemType, itemId)
            if not icon:
                continue
            awardCount = backport.text(self.__resPath.awardCount(), count=count) if count > 1 else ' '
            textBlock = formatters.packTitleDescBlock(title=text_styles.main(title), desc=text_styles.stats(awardCount), padding=formatters.packPadding(top=-35, left=58), descPadding=formatters.packPadding(top=0, left=-24))
            imageBlock = formatters.packImageBlockData(img=icon, width=48, height=48)
            blocks.append(imageBlock)
            blocks.append(textBlock)

        return formatters.packBuildUpBlockData(blocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL, padding=formatters.packPadding(top=10, bottom=-20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, stretchBg=False)

    def __getItemData(self, itemType, itemId):
        rawItem = ItemPackEntry(type=itemType, id=itemId)
        if itemType in ItemPackTypeGroup.CUSTOMIZATION:
            return self.__getCustomization(rawItem, itemId)
        elif itemType == ItemPackType.DEMOUNT_KIT:
            return self.__getDemountKit(itemId)
        item = lookupItem(rawItem, self.__itemsCache, self.__goodiesCache)
        if item is None:
            _logger.warning("Award '%r' not supported", itemType)
            return ('', '')
        else:
            return (item.icon, item.userName)

    def __getCustomization(self, rawItem, itemId):
        itemCD = getCDFromId(rawItem.type, itemId)
        item = self.__itemsCache.items.getItemByCD(itemCD)
        icon = getItemIcon(rawItem, item)
        title = getItemTitle(rawItem, item, forBox=True)
        return (icon, title)

    def __getDemountKit(self, itemId):
        kits = self.__goodiesCache.getDemountKits()
        item = kits.get(itemId)
        icon = item.getIcon(_ICON_SIZE)
        return ('', '') if item is None else (icon, item.userName)

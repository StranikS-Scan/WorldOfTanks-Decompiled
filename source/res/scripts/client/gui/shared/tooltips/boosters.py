# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/boosters.py
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import events_helpers
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from gui.shared.money import Currency
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from helpers import dependency
from helpers.i18n import makeString
from gui.Scaleform.locale.MENU import MENU
from skeletons.gui.shared import IItemsCache

class BoosterTooltipData(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(BoosterTooltipData, self).__init__(context, TOOLTIP_TYPE.BOOSTER)
        self._setContentMargin(top=15, left=19, bottom=21, right=22)
        self._setMargins(afterBlock=14)
        self._setWidth(396)
        self.leftPadding = 20

    def _packBlocks(self, boosterID, *args, **kwargs):
        items = super(BoosterTooltipData, self)._packBlocks(*args, **kwargs)
        booster = self.context.buildItem(boosterID)
        statsFields = self.context.getStatsConfiguration(booster)
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.highTitle(booster.fullUserName), desc=text_styles.main(booster.description)), formatters.packImageBlockData(img=booster.bigTooltipIcon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=180, height=180, padding={'top': -14,
          'bottom': -14})]))
        items.append(self.__packDueDate(booster))
        if statsFields.quests:
            questsResult = self.__getBoosterQuestNames(boosterID)
            if questsResult:
                items.append(self.__packAccessCondition(questsResult))
        inventoryBlock = self.__getInventoryBlock(booster=booster, showPrice=statsFields.buyPrice and booster.buyPrices, showInventoryCount=statsFields.inventoryCount and booster.count)
        if inventoryBlock:
            items.append(formatters.packBuildUpBlockData(inventoryBlock))
        if statsFields.activeState and booster.inCooldown:
            items.append(self.__packActiveState(booster.getUsageLeftTimeStr()))
        return items

    def __packDueDate(self, booster):
        if booster.expiryTime:
            text = makeString(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_DUEDATE_VALUE, date=booster.getExpiryDate())
        else:
            text = makeString(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_UNDEFINETIME)
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_DUEDATE_TITLE), text_styles.standard(text))])

    def __packAccessCondition(self, questsResult):
        qNames = '"%s"' % ', '.join(questsResult)
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_GETCONDITION_TITLE), text_styles.standard(makeString(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_GETCONDITION_VALUE, questName=text_styles.neutral(qNames))))])

    def __packActiveState(self, time):
        state = text_styles.main(makeString(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_ACTIVE_VALUE, time=text_styles.stats(time)))
        return formatters.packBuildUpBlockData([formatters.packAlignedTextBlockData(text_styles.statInfo(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_ACTIVE_TITLE), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding={'bottom': 4}), formatters.packAlignedTextBlockData(state, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)])

    def __getBoosterQuestNames(self, boosterID):
        questsResult = set()
        quests = events_helpers.getBoosterQuests()
        for q in quests.itervalues():
            bonuses = q.getBonuses('goodies')
            for b in bonuses:
                boosters = b.getBoosters()
                for qBooster, _ in boosters.iteritems():
                    if boosterID == qBooster.boosterID:
                        questsResult.add(q.getUserName())

        return questsResult

    def __getInventoryBlock(self, booster, showPrice, showInventoryCount):
        block = []
        money = self.itemsCache.items.stats.money
        if showPrice:
            showDelimiter = False
            leftPadding = 92
            for itemPrice in booster.buyPrices:
                currency = itemPrice.getCurrency()
                value = itemPrice.price.getSignValue(currency)
                defValue = itemPrice.defPrice.getSignValue(currency)
                needValue = value - money.getSignValue(currency)
                actionPercent = itemPrice.getActionPrc()
                if currency == Currency.GOLD and actionPercent > 0:
                    leftActionPadding = 101 + self.leftPadding
                else:
                    leftActionPadding = 81 + self.leftPadding
                if showDelimiter:
                    block.append(formatters.packTextBlockData(text=text_styles.standard(TOOLTIPS.VEHICLE_TEXTDELIMITER_OR), padding=formatters.packPadding(left=leftActionPadding)))
                block.append(makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), needValue if needValue > 0 else None, defValue if defValue > 0 else None, actionPercent, leftPadding=leftPadding))
                showDelimiter = True

        if showInventoryCount:
            block.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(TOOLTIPS.VEHICLE_INVENTORYCOUNT), value=text_styles.stats(booster.count), icon=RES_ICONS.MAPS_ICONS_LIBRARY_STORAGE_ICON, padding=formatters.packPadding(left=49), titlePadding=formatters.packPadding(), iconPadding=formatters.packPadding(top=-2, left=-2)))
        return block

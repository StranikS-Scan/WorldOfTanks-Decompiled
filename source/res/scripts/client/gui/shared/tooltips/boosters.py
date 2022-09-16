# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/boosters.py
from typing import TYPE_CHECKING
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.goodies.goodie_items import Booster
from gui.impl.backport import image, text
from gui.impl.gen import R
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PREMIUM_BOOSTER_IDS
from gui.impl.lobby.personal_reserves.personal_reserves_utils import canBuyBooster
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import getTotalBoostersByResourceAndPremium
from gui.server_events import events_helpers
from gui.shared.formatters import text_styles as _ts
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE
from gui.shared.money import Currency
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.tooltips.contexts import BoosterStatsConfiguration, BoosterContext
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Dict, List, Any, Optional
    from gui.shared.items_cache import ItemsCache
    from gui.goodies import GoodiesCache

class BoosterTooltipData(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, context):
        super(BoosterTooltipData, self).__init__(context, TOOLTIP_TYPE.BOOSTER)
        self._setContentMargin(top=15, left=19, bottom=21, right=22)
        self._setMargins(afterBlock=14)
        self._setWidth(400)
        self.leftPadding = 20

    def _packBlocks(self, boosterID, *args, **kwargs):
        items = super(BoosterTooltipData, self)._packBlocks(*args, **kwargs)
        booster = self.context.buildItem(boosterID)
        if not booster:
            return items
        stats = self.context.getStatsConfiguration(booster)
        items.append(self.__getHeader(booster))
        infoBlocks = self.__getInfoBlocks(booster, stats)
        if infoBlocks:
            items.append(infoBlocks)
        items.append(formatters.packBuildUpBlockData([self.__getBonusBlocks(booster)], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(top=-5, bottom=-10)))
        priceStorageItems = list()
        priceInfo = self.__getPriceInfo(stats, booster)
        if priceInfo:
            priceStorageItems.append(priceInfo)
        priceStorageItems.append(self.__getInDepot(booster))
        items.append(formatters.packBuildUpBlockData(priceStorageItems, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=60, top=-10, bottom=-15)))
        if stats.quests:
            questsResult = self.__getBoosterQuestNames(boosterID)
            if questsResult:
                items.append(self.__getAccessCondition(questsResult))
        inventoryBlock = self.__getInventoryBlock(booster=booster, showPrice=stats.buyPrice and booster.buyPrices, showInventoryCount=stats.inventoryCount and booster.count)
        if inventoryBlock:
            items.append(formatters.packBuildUpBlockData(inventoryBlock))
        items.append(self.__getReceiveBlock(booster))
        items.extend(self.__getActivationInfo(stats, booster))
        return items

    def __getHeader(self, booster):
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=_ts.highTitle(text(R.strings.tooltips.boostersWindow.booster.activateInfo.title.dyn(booster.boosterGuiType)())), desc=_ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.dyn('improvedReserve' if booster.boosterID in PREMIUM_BOOSTER_IDS else 'basicReserve')()))), formatters.packImageBlockData(img=booster.bigTooltipIcon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=180, height=135, padding=formatters.packPadding(top=-14, bottom=-14))])

    def __getInfoBlocks(self, booster, stats):
        blocks = []
        if stats.activateInfo:
            activateInfo = formatters.packTitleDescBlock(title=_ts.middleTitle(text(R.strings.tooltips.boostersWindow.booster.activateInfo.title())), desc=_ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.description())))
            blocks.append(activateInfo)
        if stats.dueDate:
            if booster.expiryTime:
                dueDateStr = text(R.strings.tooltips.boostersWindow.booster.dueDate.value(), date=booster.getExpiryDate())
            else:
                dueDateStr = text(R.strings.tooltips.boostersWindow.boostersWindow.boostersTableRenderer.undefineTime())
            dueDate = formatters.packTitleDescBlock(title=_ts.middleTitle(R.strings.tooltips.boostersWindow.booster.dueDate.title()), desc=_ts.main(dueDateStr))
            blocks.append(dueDate)
        return formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=-16)) if blocks else None

    def __getBonusBlocks(self, booster):
        return formatters.packMultipleText('', formatters.getImage(image(R.images.gui.maps.icons.personal_reserves.tooltips.lightening_icon()), width=10, height=16, vspace=-3), _ts.gold(text(R.strings.tooltips.boostersWindow.booster.activateInfo.bonus())), ' ', _ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.bonusValueTime.dyn(booster.boosterGuiType)(), effectValue=booster.getFormattedValue(), effectTime=booster.getEffectTimeStr(hoursOnly=True))))

    def __getPriceInfo(self, stats, booster):
        if booster.boosterID not in PREMIUM_BOOSTER_IDS:
            return
        if stats.activeState and booster.inCooldown or not booster.getBuyPrice().price.gold:
            return
        canBuy, problem = canBuyBooster(booster, self.itemsCache)
        content = [' ',
         _ts.gold(booster.getBuyPrice().price.gold),
         formatters.getImage(image(R.images.gui.maps.icons.personal_reserves.tooltips.gold_icon()), width=16, height=16, vspace=-4),
         _ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.purchase()))]
        if not canBuy and problem in GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_CURRENCIES:
            missing = booster.getBuyPrice().price.gold - self.itemsCache.items.stats.money.gold
            content.extend([_ts.main('('),
             _ts.locked(text(R.strings.tooltips.boostersWindow.booster.activateInfo.notEnough())),
             _ts.gold(missing),
             formatters.getImage(image(R.images.gui.maps.icons.personal_reserves.tooltips.gold_icon()), width=16, height=16, vspace=-4),
             _ts.main(')')])
        return formatters.packMultipleText(*content)

    def __getInDepot(self, booster):
        return formatters.packMultipleText(' ', _ts.stats(getTotalBoostersByResourceAndPremium(booster, BoosterTooltipData.goodiesCache)), formatters.getImage(image(R.images.gui.maps.icons.personal_reserves.tooltips.in_hangar_icon()), width=30, height=24, vspace=-6), _ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.inDepot())))

    def __getReceiveBlock(self, booster):
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=_ts.middleTitle(text(R.strings.tooltips.boostersWindow.booster.activateInfo.receive())), desc=_ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.dyn('paidReceiveInfo' if booster.boosterID in PREMIUM_BOOSTER_IDS else 'nonPaidReceiveInfo')())))], padding=formatters.packPadding(bottom=-16))

    def __getActivationInfo(self, stats, booster):
        return [self.__getActiveState(booster.getUsageLeftTimeStr()), self.__packGrayText(text(R.strings.tooltips.boostersWindow.booster.activateInfo.bonusTimeInfo()))] if stats.activeState and booster.inCooldown else [formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=_ts.middleTitle(text(R.strings.tooltips.boostersWindow.booster.activateInfo.activation()))), formatters.packTitleDescBlock(title=_ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.activationInfo())))], padding=formatters.packPadding(bottom=-16)), self.__packGrayText(text(R.strings.tooltips.boostersWindow.booster.activateInfo.notActivated()))]

    def __packGrayText(self, message):
        return formatters.packBuildUpBlockData([formatters.packAlignedTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'standardText', {'message': message}), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=-16))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def __getAccessCondition(self, questsResult):
        qNames = '"{}"'.format(', '.join(questsResult))
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(_ts.middleTitle(text(R.strings.tooltips.boostersWindow.booster.getCondition.title())), _ts.standard(text(R.strings.tooltips.boostersWindow.booster.getCondition.value(), questName=_ts.neutral(qNames))))])

    def __getActiveState(self, time):
        state = _ts.statInfo(text(R.strings.tooltips.boostersWindow.booster.active.title()))
        timeLeft = _ts.main(text(R.strings.tooltips.boostersWindow.booster.active.value(), time=_ts.stats(time)))
        return formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(title=state, icon=image(R.images.gui.maps.icons.tooltip.activeIcon()), padding=formatters.packPadding(left=132), titlePadding=formatters.packPadding(), iconPadding=formatters.packPadding(top=2, left=-2)), formatters.packAlignedTextBlockData(text=timeLeft, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=-10))])

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
        money = BoosterTooltipData.itemsCache.items.stats.money
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
                    block.append(formatters.packTextBlockData(text=_ts.standard(text(R.strings.tooltips.vehicle.textDelimiter.dyn('or')())), padding=formatters.packPadding(left=leftActionPadding)))
                block.append(makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), needValue if needValue > 0 else None, defValue if defValue > 0 else None, actionPercent, leftPadding=leftPadding))
                showDelimiter = True

        if showInventoryCount:
            block.append(formatters.packTitleDescParameterWithIconBlockData(title=_ts.main(text(R.strings.tooltips.vehicle.inventoryCount())), value=_ts.stats(booster.count), icon=image(R.images.gui.maps.icons.library.storage_icon()), padding=formatters.packPadding(left=104), titlePadding=formatters.packPadding(), iconPadding=formatters.packPadding(top=-2, left=-2)))
        return block

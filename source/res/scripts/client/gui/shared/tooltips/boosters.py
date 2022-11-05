# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/boosters.py
from typing import TYPE_CHECKING
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.goodies.goodie_items import Booster, ClanReservePresenter
from gui.impl.backport import image, text
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PREMIUM_BOOSTER_IDS
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import getTotalBoostersByResourceAndPremium
from gui.impl.gen import R
from gui.server_events import events_helpers
from gui.shared.formatters import text_styles as _ts
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.tooltips.contexts import BoosterStatsConfiguration, BoosterInfoContext
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Dict, List, Optional
    from gui.shared.items_cache import ItemsCache
    from gui.goodies import GoodiesCache
    from gui.goodies.goodie_items import BoostersType

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
        if isinstance(booster, Booster):
            priceStorageItems.append(self.__getInDepot(booster))
        if priceStorageItems:
            items.append(formatters.packBuildUpBlockData(priceStorageItems, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=60, top=-10, bottom=-10)))
        if stats.quests:
            questsResult = self.__getBoosterQuestNames(boosterID)
            if questsResult:
                items.append(self.__getAccessCondition(questsResult))
        if booster.getIsAttainable():
            items.append(self.__getReceiveBlock(booster))
        if stats.activeState:
            items.extend(self.__getActivationInfo(booster))
        return items

    def __getHeader(self, booster):
        descriptionColor = _ts.gold if booster.getIsPremium() else _ts.main
        descriptionText = R.strings.tooltips.boostersWindow.booster.activateInfo.dyn('improvedReserve' if booster.getIsPremium() else 'basicReserve')()
        if isinstance(booster, ClanReservePresenter):
            descriptionText = R.strings.fortifications.orders.dyn(booster.clanReserveType)()
            descriptionColor = _ts.main
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=_ts.highTitle(text(R.strings.tooltips.boostersWindow.booster.activateInfo.title.dyn(booster.boosterGuiType)())), desc=descriptionColor(text(descriptionText))), formatters.packImageBlockData(img=booster.bigTooltipIcon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=180, height=135, padding=formatters.packPadding(top=-14, bottom=-14))])

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
        elif stats.activeState and booster.inCooldown or not booster.getBuyPrice().price.gold:
            return
        else:
            itemPrice = booster.getBuyPrice()
            currency = itemPrice.price.getCurrency()
            value = itemPrice.price.getSignValue(currency)
            needValue = value - self.itemsCache.items.stats.money.getSignValue(currency)
            if needValue <= 0:
                needValue = None
            oldPrice = itemPrice.defPrice.getSignValue(currency)
            percent = itemPrice.getActionPrc()
            return formatters.packBuildUpBlockData([makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), neededValue=needValue, oldPrice=oldPrice, percent=percent, valueWidth=-1, leftPadding=0, iconRightOffset=0)], padding=formatters.packPadding(left=0 if percent else -38, top=-12, bottom=0))

    def __getInDepot(self, booster):
        return formatters.packMultipleText(' ', _ts.stats(getTotalBoostersByResourceAndPremium(booster, BoosterTooltipData.goodiesCache)), formatters.getImage(image(R.images.gui.maps.icons.personal_reserves.tooltips.in_hangar_icon()), width=30, height=24, vspace=-6), _ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.inDepot())), padding=formatters.packPadding(top=-10, bottom=-10))

    def __getReceiveBlock(self, booster):
        if isinstance(booster, ClanReservePresenter):
            receiveText = R.strings.tooltips.boostersWindow.booster.activateInfo.clanReserveReceiveInfo()
        else:
            receiveText = R.strings.tooltips.boostersWindow.booster.activateInfo.dyn('paidReceiveInfo' if booster.boosterID in PREMIUM_BOOSTER_IDS else 'nonPaidReceiveInfo')()
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=_ts.middleTitle(text(R.strings.tooltips.boostersWindow.booster.activateInfo.receive())), desc=_ts.main(text(receiveText)))], padding=formatters.packPadding(bottom=-16))

    def __getActivationInfo(self, booster):
        result = []
        if booster.inCooldown:
            result.append(self.__getActiveState(booster.getUsageLeftTimeStr()))
            if isinstance(booster, ClanReservePresenter):
                return result
            result.append(self.__packGrayText(text(R.strings.tooltips.boostersWindow.booster.activateInfo.bonusTimeInfo())))
            return result
        return [formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=_ts.middleTitle(text(R.strings.tooltips.boostersWindow.booster.activateInfo.activation()))), formatters.packTitleDescBlock(title=_ts.main(text(R.strings.tooltips.boostersWindow.booster.activateInfo.activationInfo())))], padding=formatters.packPadding(bottom=-16)), self.__packGrayText(text(R.strings.tooltips.boostersWindow.booster.activateInfo.notActivated()))]

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

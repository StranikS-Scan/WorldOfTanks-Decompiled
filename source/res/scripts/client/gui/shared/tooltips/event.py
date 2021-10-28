# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/event.py
import time
from collections import namedtuple
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatTimeAndDate
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.halloween.tooltips.daily_widget_tooltip import DailyWidgetTooltip
from gui.impl.lobby.halloween.tooltips.event_banner_tooltip import EventBannerTooltip
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events import events_helpers
from gui.server_events.awards_formatters import AWARDS_SIZES, getHW21RewardBoxTooltipAwardFormatter, getHW21FinalRewardBoxTooltipAwardFormatter
from gui.server_events.events_helpers import isHalloween, isHalloweenAFK
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.tooltips import TOOLTIP_TYPE, formatters, ToolTipBaseData
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.formatters import packBuildUpBlockData
from gui.shared.tooltips.quests import QuestsPreviewTooltipData
from gui.shared.tooltips.shell import ShellBlockToolTipData
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from helpers.time_utils import getTodayStartingTimeUTC, getTimeStructInLocal
from skeletons.gui.game_control import IQuestsController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from vehicle import VehicleInfoTooltipData, HeaderBlockConstructor, StatusBlockConstructor
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.impl.lobby.halloween.event_helpers import filterVehicleBonuses

class GfBannerTooltipData(ToolTipBaseData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(GfBannerTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.GF_BANNER_TOOLTIP)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(EventBannerTooltip(), useDecorator=False)


class EventVehicleInfoTooltipData(VehicleInfoTooltipData, IGlobalListener):

    def _getCrewIconBlock(self):
        tImg = RES_ICONS.MAPS_ICONS_MESSENGER_ICONCONTACTS
        return [formatters.packImageBlockData(img=tImg, alpha=0)]

    def _getHeaderBlockConstructorDescr(self):
        return EventHeaderBlockConstructor

    def _getStatusBlockConstructorDescr(self):
        return StatusBlockConstructor


class EventHeaderBlockConstructor(HeaderBlockConstructor):

    def construct(self):
        block = []
        headerBlocks = []
        if self.vehicle.isElite:
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_ELITE_VEHICLE_BG_LINKAGE
        else:
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE
        nameStr = text_styles.highTitle(self.vehicle.userName)
        typeStr = text_styles.main(backport.text(R.strings.event.vehicleTooltip.header.vehicleType.event.dyn(self.vehicle.type)()))
        levelStr = text_styles.concatStylesWithSpace(text_styles.stats(int2roman(self.vehicle.level)), text_styles.standard(_ms(TOOLTIPS.VEHICLE_LEVEL)))
        icon = getTypeBigIconPath(self.vehicle.type, self.vehicle.isElite)
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc=text_styles.concatStylesToMultiLine(levelStr + ' ' + typeStr, ''), img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-9, txtOffset=99, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


def getEndingInfoBlockBonusToken(finishDate, blockWidth, padding=None):
    date = backport.getShortDateFormat(finishDate)
    times = backport.getShortTimeFormat(finishDate)
    text = text_styles.standard(backport.text(R.strings.tooltips.quests.bonuses.token.he19_money.specialConditionsDesc()).format(text_styles.standard(date), text_styles.standard(times)))
    infoBlock = formatters.packTextParameterWithIconBlockData(name=text, value='', icon=ICON_TEXT_FRAMES.ATTENTION1, nameOffset=10, padding=formatters.packPadding(left=-60, bottom=-2))
    return formatters.packBuildUpBlockData([infoBlock], blockWidth=blockWidth, padding=padding)


def getEventCoinsBlock(coinsCount, title, width, left=30):
    valueBlock = formatters.packTextParameterWithIconBlockData(name=text_styles.crystal(title), value=text_styles.crystal(coinsCount), icon=ICON_TEXT_FRAMES.HW21_EVENT_COIN, padding=formatters.packPadding(left=left, bottom=15), valueWidth=64, iconYOffset=-3)
    return packBuildUpBlockData([valueBlock], blockWidth=width, padding=formatters.packPadding(left=-4))


def formatAccrualValue(value):
    return '+{}'.format(value)


def getHowToGetInfoBlock(title, description, blockWidth=None, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE):
    return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(title))), formatters.packTextBlockData(text=text_styles.main(text_styles.concatStylesToMultiLine(backport.text(description))))], blockWidth=blockWidth, linkage=linkage)


class EventCostTooltipData(BlocksTooltipData):
    _eventsCache = dependency.descriptor(IEventsCache)
    _BLOCK_WIDTH = 350

    def __init__(self, context):
        super(EventCostTooltipData, self).__init__(context, None)
        self._setWidth(self._BLOCK_WIDTH)
        return

    def _packBlocks(self):
        items = super(EventCostTooltipData, self)._packBlocks()
        blocks = [formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.tooltips.event.cost.title()))), formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.event.cost.description())))]
        items.append(formatters.packBuildUpBlockData(blocks))
        finishDate = self._eventsCache.getEventFinishTime()
        items.append(getEndingInfoBlockBonusToken(finishDate, self._BLOCK_WIDTH))
        return items


InterrogationCtx = namedtuple('InterrogationCtx', 'status phase difficulty numberMemories totalMemories')
InterrogationCtx.__new__.__defaults__ = (None, None, None, None, None)

class EventInterrogationTooltipData(BlocksTooltipData):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _gameEventController = dependency.descriptor(IGameEventController)
    _BLOCK_WIDTH = 350
    NOT_RECEIVED = 1
    NOT_DECODED = 2
    HOW_MUCH = 3
    DECODED = 4
    LAST = 5
    LAST_DECODED = 6

    def __init__(self, context):
        super(EventInterrogationTooltipData, self).__init__(context, None)
        self._setWidth(self._BLOCK_WIDTH)
        self._setContentMargin(top=2, left=-4, bottom=3, right=1)
        self._setMargins(afterBlock=0)
        return

    @staticmethod
    def getFormat(label, imgSource, align):
        return {'label': label,
         'imgSource': imgSource,
         'gap': 5,
         'align': align}

    def getExtBonus(self):
        return self.getFormat('', '../maps/icons/library/badge_94_54.png', 'center')

    def packBonus(self, bonus, size):
        return self.getFormat(bonus.getFormattedLabel(), bonus.getImage(size), bonus.align)

    def _packBonuses(self, preformattedBonuses, size=AWARDS_SIZES.SMALL, isAddExtBonus=False):
        result = []
        for b in preformattedBonuses:
            result.append(self.packBonus(b, size))

        if isAddExtBonus:
            result.append(self.getExtBonus())
        return result

    def getStatus(self, ctx):
        status = ctx.status
        return self.LAST_DECODED if status == self.LAST and ctx.numberMemories >= ctx.totalMemories else status

    def getBlockAttributes(self, tokenID, ctx):
        data = dict(title='', description='', columnWidth=55, bottom=30, value=None, bonuses=None)
        status = self.getStatus(ctx)
        rewardBox = self._gameEventController.getEventRewardController().rewardBoxesConfig[tokenID]
        data['value'] = rewardBox.decodePrice.amount
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        bonusRewards = filterVehicleBonuses(rewardBox.bonusVehicles, self._itemsCache.items.getVehicles(criteria=criteria).keys())
        formatter = getHW21FinalRewardBoxTooltipAwardFormatter
        if status not in [self.LAST, self.LAST_DECODED]:
            formatter = getHW21RewardBoxTooltipAwardFormatter
            bonusRewards += rewardBox.bonusRewards
        data['bonuses'] = self._packBonuses(formatter().format(bonusRewards), AWARDS_SIZES.SMALL, ctx.status == self.LAST)
        r = R.strings.tooltips.event.interrogation
        if status == self.NOT_RECEIVED:
            data['title'] = backport.text(r.title.not_received())
            data['description'] = backport.text(r.description.not_received(), phase=text_styles.middleTitle(backport.text(r.phase(), number=ctx.phase)), difficulty=text_styles.middleTitle(backport.text(r.difficulty.num(ctx.difficulty)())))
        elif status in [self.NOT_DECODED, self.HOW_MUCH]:
            data['title'] = backport.text(r.title.not_decoded())
            data['description'] = backport.text(r.description.not_decoded(), currency=text_styles.middleTitle(backport.text(r.currency())))
        elif status == self.DECODED:
            data['title'] = backport.text(r.title.decoded())
            data['bottom'] = 10
        elif status == self.LAST:
            data['title'] = backport.text(r.title.last())
            data['description'] = backport.text(r.description.last(), uniq_tank=text_styles.middleTitle(backport.text(r.uniq_tank())))
            data['columnWidth'] = 94
        elif status == self.LAST_DECODED:
            data['title'] = backport.text(r.title.last_decoded())
            data['columnWidth'] = 94
            data['bottom'] = 10
        return data

    def _packBlocks(self, tokenID, data):
        items = super(EventInterrogationTooltipData, self)._packBlocks()
        ctx = InterrogationCtx(*data)
        status = self.getStatus(ctx)
        blocksData = self.getBlockAttributes(tokenID, ctx)
        items.append(self._getTitleBlock(blocksData['title']))
        items.append(self._getDescriptionBlock(blocksData['description'], 20 if status in [self.LAST, self.NOT_RECEIVED] else 0))
        if status in [self.NOT_DECODED, self.HOW_MUCH]:
            items.append(getEventCoinsBlock(blocksData['value'], backport.text(R.strings.tooltips.event.interrogation.value_to_decoded()), self._BLOCK_WIDTH))
        if status == self.LAST:
            items.append(self._getEventMemoriesBlock(ctx.numberMemories, ctx.totalMemories))
        if blocksData['bonuses']:
            items.append(self._getEventBonusBlock(blocksData))
        if status == self.NOT_DECODED and blocksData['value'] > self._gameEventController.getShop().getKeys():
            items.append(self._getNotEnoughCoinsBlock())
        if status in [self.DECODED, self.LAST_DECODED]:
            items.append(self._getAwardReceivedBlock())
        return items

    def _getEventMemoriesBlock(self, numberMemories, totalMemories):
        block = formatters.packAlignedTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.event.interrogation.memories_decoded(), number_memories=numberMemories, total_memories=totalMemories)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8))
        return packBuildUpBlockData([block], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, blockWidth=self._BLOCK_WIDTH)

    def _getAwardReceivedBlock(self):
        text = backport.text(R.strings.tooltips.event.interrogation.award_received())
        img = R.images.gui.maps.icons.library.check()
        title = text_styles.bonusAppliedText(text)
        return formatters.packImageTextBlockData(title=title, img=backport.image(img), imgPadding=formatters.packPadding(left=-4, top=-1), txtOffset=20, padding=formatters.packPadding(left=110, bottom=10))

    def _getNotEnoughCoinsBlock(self):
        items = [formatters.packAlignedTextBlockData(text=text_styles.critical(backport.text(R.strings.tooltips.event.interrogation.not_enough.title())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT), formatters.packAlignedTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.interrogation.not_enough.description())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT)]
        return packBuildUpBlockData(blocks=items, padding=formatters.packPadding(top=-16, left=20, bottom=10))

    def _getTitleBlock(self, title):
        return formatters.packTextBlockData(text_styles.highTitle(title), padding=formatters.packPadding(top=8, left=20))

    def _getDescriptionBlock(self, title, bottom=0):
        return formatters.packTextBlockData(text_styles.main(title), padding=formatters.packPadding(top=-4, left=20, bottom=bottom, right=5))

    def _getEventBonusBlock(self, data):
        items = []
        items.append(formatters.packAlignedTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.event.interrogation.award_decode())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=8)))
        items.append(formatters.packAwardsExBlockData(data['bonuses'], columnWidth=data['columnWidth'], rowHeight=40, horizontalGap=5, renderersAlign=formatters.RENDERERS_ALIGN_CENTER, padding=formatters.packPadding(top=10, bottom=18)))
        return packBuildUpBlockData(blocks=items, stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_EVENT_AWARD_UI, padding=formatters.packPadding(top=-16, left=10, bottom=data['bottom']), blockWidth=self._BLOCK_WIDTH)


class EventKeyInfoTooltipData(BlocksTooltipData):
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _BLOCK_WIDTH = 300
    _ICON_TOKEN = '../maps/icons/event/token_key_348_114.png'

    def __init__(self, context):
        super(EventKeyInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.TANKMAN)

    def _packBlocks(self, accrued=None):
        self.config = self._gameEventController.getVehicleSettings()
        items = super(EventKeyInfoTooltipData, self)._packBlocks()
        items.append(self._getTitleBlock())
        items.append(self._getIconBlock(self._ICON_TOKEN))
        items.append(self._getDescriptionBlock())
        items.append(self._getCoinsBlock())
        if accrued is None:
            items.append(self._getHowToGetInfoBlock())
        else:
            items.append(self._getAccrualInfoBlock(accrued.efficiency, accrued.boss, accrued.daily))
        items.append(getEndingInfoBlockBonusToken(self._eventsCache.getEventFinishTime(), self._BLOCK_WIDTH))
        return items

    def _getTitleBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.event.key.title())))], blockWidth=self._BLOCK_WIDTH)

    def _getIconBlock(self, icon):
        return formatters.packBuildUpBlockData([formatters.packImageBlockData(img=icon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)], blockWidth=self._BLOCK_WIDTH, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_BLUE_BIG_LINKAGE)

    def _getDescriptionBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.key.description())))], blockWidth=self._BLOCK_WIDTH)

    def _getCoinsBlock(self):
        coinsCount = self._gameEventController.getShop().getKeys()
        eventCoinsBlock = formatters.packMoneyAndXpValueBlock(value=text_styles.eventCoin(backport.getIntegralFormat(coinsCount)), icon=ICON_TEXT_FRAMES.HW21_EVENT_COIN, iconYoffset=-3, paddingBottom=0)
        return packBuildUpBlockData([eventCoinsBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=30), blockWidth=self._BLOCK_WIDTH)

    def _getHowToGetInfoBlock(self):
        return getHowToGetInfoBlock(R.strings.tooltips.event.key.how_to_get(), R.strings.tooltips.event.key.how_to_get_variants(), self._BLOCK_WIDTH)

    def _getVariant(self, title, value):
        return (backport.text(title, value=text_styles.middleTitle(formatAccrualValue(value))),) if value > 0 else ()

    def _getAccrualInfoBlock(self, efficiency, boss, daily):
        rKey = R.strings.tooltips.event.key.what_accrual_variants
        variants = self._getVariant(rKey.efficiency(), efficiency) + self._getVariant(rKey.boss(), boss) + self._getVariant(rKey.daily(), daily)
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.event.key.what_accrual()))), formatters.packTextBlockData(text=text_styles.main(text_styles.concatStylesToMultiLine(*variants)))], blockWidth=self._BLOCK_WIDTH)


class EventEfficientInfoTooltipData(BlocksTooltipData):
    _BLOCK_WIDTH = 300

    def __init__(self, context):
        super(EventEfficientInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.TANKMAN)

    def _packBlocks(self, icon, keys):
        items = super(EventEfficientInfoTooltipData, self)._packBlocks()
        items.append(self._getTitleBlock())
        items.append(self._getIconBlock(icon))
        items.append(self._getDescriptionBlock())
        items.append(self._getCoinsBlock(keys))
        items.append(self._getHowToGetInfoBlock())
        return items

    def _getTitleBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.event.efficient.title())))], blockWidth=self._BLOCK_WIDTH)

    def _getIconBlock(self, icon):
        return formatters.packBuildUpBlockData([formatters.packImageBlockData(img=icon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)], blockWidth=self._BLOCK_WIDTH, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getDescriptionBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.efficient.description())))], blockWidth=self._BLOCK_WIDTH)

    def _getCoinsBlock(self, keys):
        return getEventCoinsBlock(formatAccrualValue(keys), backport.text(R.strings.tooltips.event.efficient.key_label()), self._BLOCK_WIDTH, 0)

    def _getHowToGetInfoBlock(self):
        return getHowToGetInfoBlock(R.strings.tooltips.event.efficient.how_to_get(), R.strings.tooltips.event.efficient.how_to_get_variants(), self._BLOCK_WIDTH, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_BLUE_BIG_LINKAGE)


class EventDailyInfoTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EventDailyInfoTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.EVENT_DAILY_INFO)

    def getDisplayableData(self, specArgs, *args, **kwargs):
        vehicleCD = specArgs[0] if specArgs else None
        return DecoratedTooltipWindow(DailyWidgetTooltip(vehicleCD), useDecorator=False)


class EventSelectorPerfInfoTooltip(BlocksTooltipData):

    def __init__(self, context=None):
        super(EventSelectorPerfInfoTooltip, self).__init__(context, None)
        self._setWidth(370)
        self._setContentMargin(top=20, left=20, bottom=20, right=25)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EventSelectorPerfInfoTooltip, self)._packBlocks(*args, **kwargs)
        message = backport.text(R.strings.tooltips.battle_royale.hangar.perf.high_risk.header())
        problemIcon = icons.alert()
        formattedMessage = text_styles.alert(message)
        title = text_styles.concatStylesWithSpace(problemIcon, formattedMessage)
        description = text_styles.main(backport.text(R.strings.tooltips.battle_royale.hangar.perf.medium_risk.description()))
        items.append(formatters.packTitleDescBlock(title=title, desc=description))
        return items


class EventSelectorWarningTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(EventSelectorWarningTooltip, self).__init__(context, None)
        self._setWidth(width=400)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EventSelectorWarningTooltip, self)._packBlocks(*args, **kwargs)
        items.append(self._getHeaderBlock())
        items.append(self._getInfoBlock())
        return items

    def _getHeaderBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.battleTypes.event.header()))), formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.battleTypes.event.body())))])

    def _getInfoBlock(self):
        return formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(icons.info(), text_styles.stats(backport.text(R.strings.tooltips.battleTypes.event.description()))))


class EventBanInfoToolTipData(BlocksTooltipData):
    _WIDTH = 400

    def __init__(self, context):
        super(EventBanInfoToolTipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, banExpiryTime, **kwargs):
        items = super(EventBanInfoToolTipData, self)._packBlocks(banExpiryTime, **kwargs)
        self._item = self.context.buildItem(banExpiryTime, **kwargs)
        items.append(self._packHeader())
        items.append(self._packDescription())
        items.append(self._packExpiration(banExpiryTime))
        return items

    def _packHeader(self):
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.event.lobby.ban.header())), desc=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/eventBanTooltip/', 'header')))

    def _packDescription(self):
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.event.lobby.ban.quest())), desc=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/eventBanTooltip/', 'quest')), blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packExpiration(self, banExpiryTime):
        return formatters.packAlignedTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.lobby.ban.expiration(), value=formatTimeAndDate(banExpiryTime))), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-1, bottom=-6))


class HalloweenQuestsPreviewTooltipData(QuestsPreviewTooltipData):

    def _getQuestList(self, vehicle):
        return sorted([ q for q in self._questController.getQuestForVehicle(vehicle) if (isHalloween(q.getGroupID()) or isHalloweenAFK(q.getGroupID())) and q.isAvailable()[0] and not q.isCompleted() ], key=events_helpers.questsSortFunc)

    def _getHeader(self, count, vehicleName, description):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.tooltips.hangar.header.halloween.quests.header(), count=count)), img=backport.image(R.images.gui.maps.icons.event.quests.questHalloweenTooltipHeader()), txtPadding=formatters.packPadding(top=20), txtOffset=20, desc=text_styles.main(backport.text(description, vehicle=vehicleName)))

    def _getAllQuestsCompleteBlock(self):
        newDayUTC = getTodayStartingTimeUTC()
        localtime = getTimeStructInLocal(newDayUTC)
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.header.quests.empty(), hour=time.strftime('%H', localtime), min=time.strftime('%M', localtime))), padding=formatters.packPadding(left=20, top=-10, bottom=10))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class EventNoSuitableVehicleForQuest(ToolTipBaseData):
    _questController = dependency.descriptor(IQuestsController)
    _DEFAULT_LEVELS = (1, 10)

    def __init__(self, context):
        super(EventNoSuitableVehicleForQuest, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def getDisplayableData(self, *args, **kwargs):
        headerText = backport.text(R.strings.tooltips.hangar.header.halloween.noVehicle.header())
        levelMin, levelMax = self._getLevels()
        bodyText = backport.text(R.strings.tooltips.hangar.header.halloween.noVehicle.body(), min=int2roman(levelMin), max=int2roman(levelMax))
        return {'header': headerText,
         'body': bodyText}

    def _getLevels(self):
        quests = [ q for q in self._questController.getAllAvailableQuests() if (isHalloweenAFK(q.getGroupID()) or isHalloween(q.getGroupID())) and not q.isCompleted() and q.isAvailable()[0] ]
        levelList = set()
        for q in quests:
            vehicleDescr = q.vehicleReqs.getConditions().find('vehicleDescr')
            if vehicleDescr:
                _, _, level, _, _ = vehicleDescr.getParsedConditions()
                if level is not None:
                    levelList |= level

        return self._DEFAULT_LEVELS if not levelList else (min(levelList), max(levelList))


class EventShellBlockToolTipData(ShellBlockToolTipData):

    def _addBottomHint(self, items, showBasicData, leftPadding, rightPadding):
        lrPaddings = formatters.packPadding(left=leftPadding, right=rightPadding)
        rPadding = formatters.packPadding(right=rightPadding)
        if showBasicData:
            boldTextID = R.strings.tooltips.shell.event.description.bold()
            textID = R.strings.tooltips.shell.event.description()
        else:
            boldTextID = R.strings.tooltips.shell.pickups.description.bold()
            textID = R.strings.tooltips.shell.pickups.description()
        boldText = text_styles.neutral(backport.msgid(boldTextID))
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.standard(_ms(backport.msgid(textID), bold=boldText)), padding=lrPaddings)], padding=rPadding, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))

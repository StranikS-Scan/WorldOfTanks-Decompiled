# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/event_battles_tooltips.py
import logging
from gui import makeHtmlString
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.wt_event.tooltips.wt_event_buy_lootboxes_tooltip_view import WtEventBuyLootBoxesTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_carousel_vehicle_tooltip_view import WtEventCarouselVehicleTooltipView
from gui.server_events.awards_formatters import AWARDS_SIZES, getEventAwardFormatter
from gui.server_events.events_helpers import questsSortFunc, EventInfoModel
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import formatDate, getTillTimeByResource
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.tooltips import TOOLTIP_TYPE, formatters, ToolTipBaseData, WulfTooltipData
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.daapi.view.lobby.formatters.tooltips import packTimeTableHeaderBlock, packCalendarBlock
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.wt_event.wt_event_helpers import getDaysLeftFormatted
from helpers import dependency, time_utils
from predefined_hosts import g_preDefinedHosts
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IGameEventController, IQuestsController
from skeletons.gui.shared import IItemsCache
from skeletons.prebattle_vehicle import IPrebattleVehicle
_logger = logging.getLogger(__name__)
_SELECTOR_TOOLTIP_MIN_WIDTH = 280
_STR_PATH = R.strings.event

def _correctLeftTime(timeLeft):
    if timeLeft >= time_utils.ONE_DAY:
        timeLeft += time_utils.ONE_DAY * 0.5
    elif timeLeft >= time_utils.ONE_HOUR:
        timeLeft += time_utils.ONE_HOUR * 0.5
    elif timeLeft >= time_utils.ONE_MINUTE:
        timeLeft += time_utils.ONE_MINUTE * 0.5
    return timeLeft


def _getLeftTime(currentCycleEnd):
    timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))
    return text_styles.stats(backport.getTillTimeStringByRClass(_correctLeftTime(timeLeft), R.strings.menu.headerButtons.battle.types.ranked.availability))


class EventBattlesSelectorTooltip(BlocksTooltipData):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, ctx):
        super(EventBattlesSelectorTooltip, self).__init__(ctx, TOOLTIP_TYPE.EVENT_BATTLES_SELECTOR_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(_SELECTOR_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(EventBattlesSelectorTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        timeTableBlocks = [self._packTimeTableHeaderBlock()]
        primeTime = self.__gameEventController.getPrimeTimes().get(self.__connectionMgr.peripheryID)
        currentCycleEnd = None
        todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
        todayEnd += 1
        tomorrowStart, tomorrowEnd = todayStart + time_utils.ONE_DAY, todayEnd + time_utils.ONE_DAY
        tomorrowEnd += 1
        todayPeriods = ()
        tomorrowPeriods = ()
        if primeTime is not None:
            currentCycleEnd = self.__gameEventController.getCurrentSeason().getCycleEndDate()
            todayPeriods = primeTime.getPeriodsBetween(todayStart, min(todayEnd, currentCycleEnd))
            if tomorrowStart < currentCycleEnd:
                tomorrowPeriods = primeTime.getPeriodsBetween(tomorrowStart, min(tomorrowEnd, currentCycleEnd))
        todayStr = self._packPeriods(todayPeriods)
        timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(_STR_PATH.tooltips.selector.timeTable.today())), timeStr=text_styles.bonusPreviewText(todayStr)))
        tomorrowStr = self._packPeriods(tomorrowPeriods)
        timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(_STR_PATH.tooltips.selector.timeTable.tomorrow())), timeStr=text_styles.stats(tomorrowStr)))
        items.append(formatters.packBuildUpBlockData(timeTableBlocks, 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        if currentCycleEnd is not None:
            items.append(self.__formatTillEndBlock(currentCycleEnd))
        return items

    def _packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(_STR_PATH.tooltips.selector.title())), desc=text_styles.main(backport.text(_STR_PATH.tooltips.selector.desc())))

    def _packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.stats(backport.text(_STR_PATH.tooltips.selector.timeTable.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))

    def _packTimeBlock(self, message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97)

    def _packPeriods(self, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(backport.text(_STR_PATH.calendarDay.time(), start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return backport.text(_STR_PATH.tooltips.selector.timeTable.empty())

    @staticmethod
    def __formatTillEndBlock(timeLeft):
        return formatters.packTextBlockData(text_styles.main(backport.text(_STR_PATH.tooltips.selector.timeTable.tillEnd())) + ' ' + _getLeftTime(timeLeft))


class EventBattlesServerPrimeTime(ToolTipBaseData):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(EventBattlesServerPrimeTime, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, peripheryID):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        serverName = ''
        for _, serverData in enumerate(hostsList):
            _, serverName, _, _, pID = serverData
            if pID == peripheryID:
                break

        timeLeftStr = '-'
        primeTimeStr = _STR_PATH.primeTime.tooltips.server
        isNow = False
        primeTime = self.__gameEventController.getPrimeTimes().get(peripheryID)
        if primeTime:
            currentCycleEnd = self.__gameEventController.getCurrentSeason().getCycleEndDate()
            isNow, timeLeft = primeTime.getAvailability(time_utils.getCurrentLocalServerTimestamp(), currentCycleEnd)
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, _STR_PATH.status.timeLeft)
        formatedTime = text_styles.neutral(timeLeftStr)
        if isNow:
            descriptionID = primeTimeStr.available.until()
        else:
            descriptionID = primeTimeStr.unavailable.inTime()
        sName = backport.text(primeTimeStr.onServer(), server=serverName)
        description = backport.text(descriptionID, time=formatedTime)
        return {'body': '{}\n{}'.format(sName, description)}


class EventBattlesCalendar(BlocksTooltipData):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(EventBattlesCalendar, self).__init__(context, TOOLTIP_TYPE.EVENT_BATTLES_CALENDAR)
        self._setWidth(320)

    def _packBlocks(self, *args, **kwargs):
        blocks = super(EventBattlesCalendar, self)._packBlocks(args, kwargs)
        if self.__gameEventController.isModeActive():
            blocks.append(formatters.packBuildUpBlockData([self.__packHeader(), packTimeTableHeaderBlock(SELECTOR_BATTLE_TYPES.EVENT), formatters.packBuildUpBlockData(packCalendarBlock(self.__gameEventController, time_utils.getCurrentTimestamp(), SELECTOR_BATTLE_TYPES.EVENT))]))
        return blocks

    def __packHeader(self):
        currentSeason = self.__gameEventController.getCurrentSeason()
        cycleEndTime = currentSeason.getCycleEndDate()
        if cycleEndTime is None:
            _logger.error('There is not active cycle of the event battles')
            return ''
        else:
            timeLeft = getFormattedTimeLeft(max(0, cycleEndTime - time_utils.getServerUTCTime()))
            return formatters.packTextBlockData(text_styles.highlightText(backport.text(_STR_PATH.selectorTooltip.timeTable.tillEnd(), time=timeLeft)), padding=formatters.packPadding(bottom=15))


class EventQuestsTooltipData(BlocksTooltipData):
    __gameEventController = dependency.descriptor(IGameEventController)
    __questController = dependency.descriptor(IQuestsController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    _MAX_QUESTS_PER_TOOLTIP = 3
    _TOOLTIP_MIN_WIDTH = 370

    def __init__(self, context):
        super(EventQuestsTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)
        self._setMargins(afterBlock=0)
        self._setWidth(350)

    def _packBlocks(self, *args, **kwargs):
        blocks = super(EventQuestsTooltipData, self)._packBlocks(*args, **kwargs)
        vehicle = self.__prebattleVehicle.item
        if vehicle is not None and self.__gameEventController.isInPrimeTime():
            quests = sorted([ q for q in self.__questController.getQuestForVehicle(vehicle) if q.isEventBattlesQuest() ], key=questsSortFunc)
            if quests:
                blocks.append(self.__packHeader(quests, vehicle))
                blocks += [ self.__packQuest(q) for i, q in enumerate(quests) if i < self._MAX_QUESTS_PER_TOOLTIP ]
                rest = len(quests) - self._MAX_QUESTS_PER_TOOLTIP
                if rest > 0:
                    blocks.append(self.__packBottom(rest))
                return blocks
        blocks.append(self.__packHeaderUnavailable())
        return blocks

    def __packHeader(self, quests, vehicle):
        desc = ''
        isPrimeTimeLeft = self.__gameEventController.hasPrimeTimesLeftForCurrentCycle()
        isLastSeasonDay = self.__gameEventController.isLastSeasonDay()
        total = len(quests)
        completed = len([ q for q in quests if q.isCompleted() ])
        diff = total - completed
        title = backport.text(R.strings.event.tooltips.header.quests.header.dyn(vehicle.eventType)())
        allBossCompleted = total == completed and vehicle.eventType == VEHICLE_TAGS.EVENT_BOSS
        if diff > 0 or not isPrimeTimeLeft or isLastSeasonDay or allBossCompleted:
            desc = text_styles.concatStylesToSingleLine(icons.inProgress(), text_styles.main(backport.text(R.strings.event.tooltips.header.quests.header.description.till_end(), time=text_styles.stats(getDaysLeftFormatted(gameEventController=self.__gameEventController)))))
        elif isPrimeTimeLeft:
            desc = text_styles.concatStylesToSingleLine(icons.clockSh(), text_styles.tutorial(backport.text(R.strings.event.tooltips.header.quests.header.description.till_upd(), time=getTillTimeByResource(EventInfoModel.getDailyProgressResetTimeDelta(), R.strings.menu.Time.timeLeftShort))))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(title), desc=desc, img=backport.image(R.images.gui.maps.icons.wtevent.quests.dyn('{}_header'.format(vehicle.eventType))()), txtPadding=formatters.packPadding(top=18), descPadding=formatters.packPadding(top=15, left=-4), txtOffset=20)

    def __packHeaderUnavailable(self):
        self._setWidth(385)
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.event.tooltips.header.quests.header.unavailable())), desc=text_styles.standard(backport.text(R.strings.event.tooltips.header.quests.header.description.unavailable())), padding=formatters.packPadding(top=23, left=19, bottom=15))

    def __packQuest(self, quest):
        blocks = [self.__packQuestInfo(quest)]
        questRewardBlocks = self.__packQuestReward(quest)
        if questRewardBlocks is not None:
            blocks.append(questRewardBlocks)
        return formatters.packBuildUpBlockData(blocks)

    def __packQuestInfo(self, quest):
        title = text_styles.middleTitle(quest.getUserName())
        if quest.isCompleted():
            name = text_styles.concatStylesToSingleLine(icons.check(), title)
            selfPadding = formatters.packPadding(top=-3, left=14, right=20)
            descPadding = formatters.packPadding(left=6, top=-6)
        else:
            name = title
            selfPadding = formatters.packPadding(left=20, right=20)
            descPadding = formatters.packPadding(top=-2)
        return formatters.packTitleDescBlock(title=name, desc=text_styles.main(quest.getDescription()), padding=selfPadding, descPadding=descPadding)

    def __packQuestReward(self, quest):
        bonusFormatter = getEventAwardFormatter()
        blocks = [ self.__packBonus(bonus) for bonus in bonusFormatter.format(quest.getBonuses()) ]
        return formatters.packBuildUpBlockData(blocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=20, right=20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER) if blocks else None

    def __packBonus(self, bonus):
        if bonus.label.startswith('x'):
            align = BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT
            padding = formatters.packPadding(top=-10, right=0)
        else:
            align = BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER
            padding = formatters.packPadding(top=-10)
        iconBlock = formatters.packImageBlockData(img=bonus.getImage(AWARDS_SIZES.SMALL), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        textBlock = formatters.packAlignedTextBlockData(text=bonus.getFormattedLabel(), align=align, padding=padding)
        return formatters.packBuildUpBlockData(blocks=[iconBlock, textBlock], blockWidth=72, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=-6))

    def __packBottom(self, count):
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': text_styles.main(backport.text(R.strings.event.tooltips.header.quests.bottom(), count=count))}), padding=formatters.packPadding(bottom=20))


class EventLootBoxTooltipWindowData(WulfTooltipData):

    def __init__(self, context):
        super(EventLootBoxTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.EVENT_LOOTBOX)

    def getTooltipContent(self, boxType, *args, **kwargs):
        return WtEventLootBoxTooltipView(isHunterLootBox=boxType == EventLootBoxes.WT_HUNTER)


class EventBuyLootBoxTooltipWindowData(WulfTooltipData):

    def __init__(self, context):
        super(EventBuyLootBoxTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.EVENT_BUY_LOOTBOX)

    def getTooltipContent(self, *args, **kwargs):
        return WtEventBuyLootBoxesTooltipView()


class EventTicketTooltipWindowData(WulfTooltipData):

    def __init__(self, context):
        super(EventTicketTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.EVENT_BATTLES_TICKET)

    def getTooltipContent(self, *args, **kwargs):
        return WtEventTicketTooltipView()


class EventCarouselVehicleTooltipData(WulfTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def getTooltipContent(self, intCD, *args, **kwargs):
        vehicle = self.__itemsCache.items.getItemByCD(intCD)
        return WtEventCarouselVehicleTooltipView(vehInvID=vehicle.invID)

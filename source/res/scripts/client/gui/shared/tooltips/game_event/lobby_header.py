# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/game_event/lobby_header.py
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES, getDefaultAwardFormatter
from gui.server_events.events_helpers import isWhiteTigerQuest, questsSortFunc, EventInfoModel
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import formatDate, getTillTimeByResource
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.wt_event.wt_event_helpers import getDaysLeftFormatted
from helpers import dependency, time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IGameEventController, IQuestsController
_MAX_QUESTS_PER_TOOLTIP = 4
_TOOLTIP_MIN_WIDTH = 370

class EventSelectorTooltip(BlocksTooltipData):
    _gameEventCtrl = dependency.descriptor(IGameEventController)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, context):
        super(EventSelectorTooltip, self).__init__(context, TOOLTIP_TYPE.EVENT_SELECTOR_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(EventSelectorTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        timeTableBlocks = [self._packTimeTableHeaderBlock()]
        primeTime = self._gameEventCtrl.getPrimeTimes().get(self._connectionMgr.peripheryID)
        currentCycleEnd = self._gameEventCtrl.getCurrentSeason().getCycleEndDate()
        todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
        todayEnd += 1
        tomorrowStart, tomorrowEnd = todayStart + time_utils.ONE_DAY, todayEnd + time_utils.ONE_DAY
        tomorrowEnd += 1
        todayPeriods = ()
        tomorrowPeriods = ()
        if primeTime is not None:
            todayPeriods = primeTime.getPeriodsBetween(todayStart, min(todayEnd, currentCycleEnd))
            if tomorrowStart < currentCycleEnd:
                tomorrowPeriods = primeTime.getPeriodsBetween(tomorrowStart, min(tomorrowEnd, currentCycleEnd))
        todayStr = self._packPeriods(todayPeriods)
        timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(R.strings.wt_event.tooltips.selector.timeTable.today())), timeStr=text_styles.neutral(todayStr)))
        tomorrowStr = self._packPeriods(tomorrowPeriods)
        timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(R.strings.wt_event.tooltips.selector.timeTable.tomorrow())), timeStr=text_styles.stats(tomorrowStr)))
        items.append(formatters.packBuildUpBlockData(timeTableBlocks, 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        items.append(self._getTillEndBlock())
        return items

    def _packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.wt_event.tooltips.selector.title())), desc=text_styles.main(backport.text(R.strings.wt_event.tooltips.selector.desc())))

    def _packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.stats(backport.text(R.strings.wt_event.tooltips.selector.timeTable.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))

    def _packTimeBlock(self, message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97)

    def _packPeriods(self, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(backport.text(R.strings.wt_event.calendarDay.time(), start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return backport.text(R.strings.wt_event.tooltips.selector.timeTable.empty())

    def _getTillEndBlock(self):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.wt_event.menu.selector.tillEnd(), time=text_styles.stats(getDaysLeftFormatted(gameEventController=self._gameEventCtrl)))))


class EventUnavailableTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(EventUnavailableTooltip, self).__init__(context, TOOLTIP_TYPE.EVENT_UNAVAILABLE_INFO)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(EventUnavailableTooltip, self)._packBlocks(*args, **kwargs)
        items.append(formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.wt_event.tooltips.selector.title())), desc=text_styles.main(backport.text(R.strings.wt_event.tooltips.selector.desc()))))
        items.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.wt_event.status.unavailable()))))
        return items


class EventQuestsTooltipData(BlocksTooltipData):
    __gameEventController = dependency.descriptor(IGameEventController)
    __questController = dependency.descriptor(IQuestsController)

    def __init__(self, context):
        super(EventQuestsTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)
        self._setMargins(afterBlock=0)
        self._setWidth(350)

    def _packBlocks(self, *args, **kwargs):
        blocks = super(EventQuestsTooltipData, self)._packBlocks(*args, **kwargs)
        vehicle = g_currentVehicle.item
        if vehicle is not None and self.__gameEventController.isInPrimeTime():
            quests = sorted([ q for q in self.__questController.getQuestForVehicle(g_currentVehicle.item) if isWhiteTigerQuest(q.getGroupID()) ], key=questsSortFunc)
            if quests:
                blocks.append(self.__packHeader(quests, vehicle))
                blocks += [ self.__packQuest(q) for i, q in enumerate(quests) if i < _MAX_QUESTS_PER_TOOLTIP ]
                rest = len(quests) - _MAX_QUESTS_PER_TOOLTIP
                if rest > 0:
                    blocks.append(self.__packBottom(rest))
                return blocks
        blocks.append(self.__packHeaderUnavailable())
        return blocks

    def __packHeader(self, quests, vehicle):
        rStrings = R.strings.wt_event.tooltips.header.quests
        desc = ''
        isPrimeTimeLeft = self.__gameEventController.hasPrimeTimesLeft()
        isLastSeasonDay = self.__gameEventController.isLastSeasonDay()
        total = len(quests)
        completed = len([ q for q in quests if q.isCompleted() ])
        diff = total - completed
        title = backport.text(R.strings.wt_event.tooltips.header.quests.header.dyn(vehicle.eventType)())
        if diff > 0 or not isPrimeTimeLeft or isLastSeasonDay:
            desc = text_styles.concatStylesToSingleLine(icons.inProgress(), text_styles.main(backport.text(rStrings.header.description.till_end(), time=text_styles.stats(getDaysLeftFormatted(gameEventController=self.__gameEventController)))))
        elif isPrimeTimeLeft:
            desc = text_styles.concatStylesToSingleLine(icons.clockSh(), text_styles.tutorial(backport.text(rStrings.header.description.till_upd(), time=getTillTimeByResource(EventInfoModel.getDailyProgressResetTimeDelta(), R.strings.menu.Time.timeLeftShort))))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(title), desc=desc, img=backport.image(R.images.gui.maps.icons.wtevent.quests.dyn('{}_header'.format(vehicle.eventType))()), txtPadding=formatters.packPadding(top=18), descPadding=formatters.packPadding(top=15, left=-4), txtOffset=20)

    def __packHeaderUnavailable(self):
        self._setWidth(385)
        rStrings = R.strings.wt_event.tooltips.header.quests
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(rStrings.header.unavailable())), desc=text_styles.standard(backport.text(rStrings.header.description.unavailable())), padding=formatters.packPadding(top=23, left=19, bottom=15))

    def __packQuest(self, quest):
        return formatters.packBuildUpBlockData([self.__packQuestInfo(quest), self.__packQuestReward(quest)])

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
        bonusFormatter = getDefaultAwardFormatter()
        return formatters.packBuildUpBlockData([ self.__packBonus(bonus) for bonus in bonusFormatter.format(quest.getBonuses()) ], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=20, right=20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

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
         'message': text_styles.main(backport.text(R.strings.wt_event.tooltips.header.quests.bottom(), count=count))}), padding=formatters.packPadding(bottom=20))

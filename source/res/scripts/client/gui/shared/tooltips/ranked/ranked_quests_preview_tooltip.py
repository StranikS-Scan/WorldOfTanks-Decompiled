# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_quests_preview_tooltip.py
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.server_events.events_helpers import isRankedDaily, EventInfoModel
from gui.server_events.awards_formatters import AWARDS_SIZES, getDefaultAwardFormatter
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.server_events import IEventsCache
_TOOLTIP_WIDTH = 322
_MAX_VISIBLE_QUESTS = 3

class RankedQuestsPreviewTooltip(BlocksTooltipData):
    __eventsCache = dependency.descriptor(IEventsCache)
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(RankedQuestsPreviewTooltip, self).__init__(context, TOOLTIP_TYPE.RANKED_QUESTS_PREVIEW)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)
        self._setMargins(afterBlock=0)
        self._setWidth(_TOOLTIP_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(RankedQuestsPreviewTooltip, self)._packBlocks()
        quests = self.__eventsCache.getActiveQuests(lambda quest: isRankedDaily(quest.getID())).values()
        quests.sort(key=lambda q: (q.isCompleted(), not q.isAvailable().isValid, -q.getPriority()))
        season = self.__rankedController.getCurrentSeason()
        if quests and season is not None:
            isLeagues = self.__rankedController.isAccountMastered()
            isAnyPrimeNow = self.__rankedController.hasAvailablePrimeTimeServers()
            isAnyPrimeLeftTotal = self.__rankedController.hasPrimeTimesTotalLeft()
            isGlobalAvailable = not isLeagues or not isAnyPrimeNow or not isAnyPrimeLeftTotal
            diff = len(quests) - _MAX_VISIBLE_QUESTS
            visibleQuests = quests[:_MAX_VISIBLE_QUESTS]
            awardsFormatter = getDefaultAwardFormatter()
            description = self.__packDescription(quests, season, isLeagues, isAnyPrimeNow, isAnyPrimeLeftTotal)
            items.append(self.__packHeader(description))
            items.extend([ self.__packQuest(q, isGlobalAvailable, awardsFormatter) for q in visibleQuests ])
            items.extend(self.__packBottom(diff))
        return items

    def __packBottom(self, diff):
        text = text_styles.main(backport.text(R.strings.ranked_battles.questsTooltip.bottom(), number=diff))
        return [formatters.packTextBlockData(text_styles.alignText(text, 'center'), padding=formatters.packPadding(top=-7, bottom=12))] if diff > 0 else []

    def __packDescription(self, quests, season, isLeagues, isAnyPrimeNow, isAnyPrimeLeftTotal):
        resShortCut = R.strings.ranked_battles.questsTooltip
        isAllCompleted = all((q.isCompleted() for q in quests))
        isAnyPrimeLeftNextDay = self.__rankedController.hasPrimeTimesNextDayLeft()
        icon = icons.markerBlocked()
        timeDelta = time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(season.getEndDate()))
        timeDeltaStr = text_styles.stats(backport.getTillTimeStringByRClass(timeDelta, resShortCut.available))
        text = text_styles.main(backport.text(resShortCut.available(), timeDelta=timeDeltaStr))
        if not isAnyPrimeLeftTotal:
            text = text_styles.error(backport.getTillTimeStringByRClass(timeDelta, resShortCut.unavailable.seasonEnd))
        elif not isLeagues:
            text = text_styles.error(backport.text(resShortCut.unavailable.notInLeagues()))
        elif not isAllCompleted:
            if isAnyPrimeNow:
                icon = icons.inProgress(vspace=-3)
            else:
                text = text_styles.error(backport.text(resShortCut.unavailable.allServersPrime()))
        elif not isAnyPrimeLeftNextDay:
            icon = icons.inProgress(vspace=-3)
        else:
            icon = icons.clockGold()
            timeDelta = EventInfoModel.getDailyProgressResetTimeDelta()
            text = text_styles.tutorial(backport.getTillTimeStringByRClass(timeDelta, resShortCut.cooldown))
        return text_styles.concatStylesWithSpace(icon, text)

    def __packHeader(self, description):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.questsTooltip.header())), desc=text_styles.main(description), img=backport.image(R.images.gui.maps.icons.quests.ranked_quests_infotip()), txtPadding=formatters.packPadding(top=18), descPadding=formatters.packPadding(top=15), txtOffset=20)

    def __packQuest(self, quest, isGlobalAvailable, awardsFormatter):
        return formatters.packBuildUpBlockData([self.__packQuestInfo(quest, isGlobalAvailable), self.__packQuestRewards(quest, awardsFormatter)])

    def __packQuestInfo(self, quest, isGlobalAvailable):
        titleIcon = ''
        isCompleted = quest.isCompleted()
        isAvailable = quest.isAvailable().isValid
        padding = formatters.packPadding(left=23, right=20)
        descPadding = formatters.packPadding(top=-2, left=-1, right=20)
        if isCompleted:
            titleIcon = icons.check()
            padding['left'] = 18
            descPadding['left'] = 4
            descPadding['top'] = -5
        elif not isAvailable and not isGlobalAvailable:
            titleIcon = icons.notAvailableRed() + '  '
        return formatters.packTitleDescBlock(title=text_styles.concatStylesToSingleLine(titleIcon, text_styles.middleTitle(quest.getUserName())), desc=text_styles.main(quest.getDescription()), padding=padding, descPadding=descPadding)

    def __packQuestRewards(self, quest, awardsFormatter):
        return formatters.packBuildUpBlockData([ self.__packSingleReward(bonus) for bonus in awardsFormatter.format(quest.getBonuses()) ], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=20, right=20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def __packSingleReward(self, bonus):
        isMultiBonus = bonus.label.startswith('x')
        iconBlock = formatters.packImageBlockData(img=bonus.getImage(AWARDS_SIZES.SMALL), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        textBlock = formatters.packAlignedTextBlockData(text=bonus.getFormattedLabel(), align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT if isMultiBonus else BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-16, right=12) if isMultiBonus else formatters.packPadding(top=-16))
        return formatters.packBuildUpBlockData(blocks=[iconBlock, textBlock], blockWidth=72, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=-6))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/event_progression.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.backport import getTillTimeStringByRClass as getTimeStr
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES, getEpicViewAwardPacker
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils, int2roman
from skeletons.gui.game_control import IEventProgressionController
_R_EPIC_BATTLE = R.strings.epic_battle.questsTooltip.epicBattle

class EventProgressionQuestsTooltipData(BlocksTooltipData):
    _eventProgression = dependency.descriptor(IEventProgressionController)
    __slots__ = ()

    def __init__(self, context):
        super(EventProgressionQuestsTooltipData, self).__init__(context, TOOLTIP_TYPE.EPIC_QUESTS)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)
        self._setMargins(afterBlock=0)
        self._setWidth(322)

    def _packBlocks(self, *args, **kwargs):
        completedIds = args[1] if args[1] != 'None' else None
        quests = self._eventProgression.getQuestForVehicle(g_currentVehicle.item, sortByPriority=True, questIDs=completedIds)
        if quests:
            return [self._packHeader(quests)] + [ self.__packQuest(q) for q in quests ]
        else:
            return super(EventProgressionQuestsTooltipData, self)._packBlocks()

    def _packHeader(self, quests):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(self._eventProgression.questTooltipHeaderTxtId)), desc=text_styles.main(self.__formatDescription(quests)), img=backport.image(self._eventProgression.questTooltipHeaderIconId), txtPadding=formatters.packPadding(top=18), descPadding=formatters.packPadding(top=15), txtOffset=20)

    @classmethod
    def _isQuestCompleted(cls, quest):
        return quest.isCompleted()

    def __packQuest(self, quest):
        return formatters.packBuildUpBlockData([self.__packQuestInfo(quest), self.__packQuestRewards(quest)])

    def __packQuestInfo(self, quest):
        title = text_styles.middleTitle(quest.getUserName())
        if self._isQuestCompleted(quest):
            name = text_styles.concatStylesToSingleLine(icons.check(), title)
            selfPadding = formatters.packPadding(top=-3, left=14, right=20)
            descPadding = formatters.packPadding(left=6, top=-6)
        else:
            name = title
            selfPadding = formatters.packPadding(left=20, right=20)
            descPadding = formatters.packPadding(top=-2)
        return formatters.packTitleDescBlock(title=name, desc=text_styles.main(quest.getDescription()), padding=selfPadding, descPadding=descPadding)

    def __packQuestRewards(self, quest):
        packer = getEpicViewAwardPacker()
        return formatters.packBuildUpBlockData([ self.__packQuestReward(bonus) for bonus in packer.format(quest.getBonuses()) ], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=20, right=20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def __packQuestReward(self, bonus):
        if bonus.label.startswith('x'):
            align = BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT
            padding = formatters.packPadding(top=-16, right=12)
        else:
            align = BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER
            padding = formatters.packPadding(top=-16)
        iconBlock = formatters.packImageBlockData(img=bonus.getImage(AWARDS_SIZES.SMALL), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        textBlock = formatters.packAlignedTextBlockData(text=bonus.getFormattedLabel(), align=align, padding=padding)
        return formatters.packBuildUpBlockData(blocks=[iconBlock, textBlock], blockWidth=72, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=-6))

    def __formatDescription(self, quests):
        season = self._eventProgression.getCurrentSeason() or self._eventProgression.getNextSeason()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        cycle = season.getCycleInfo()
        if not self._eventProgression.modeIsAvailable() or cycle is None:
            return ''
        elif self._eventProgression.isNeedAchieveMaxLevelForDailyQuest():
            maxLevel = self._eventProgression.getMaxPlayerLevel()
            description = backport.text(_R_EPIC_BATTLE.unavailable(), reason=backport.text(_R_EPIC_BATTLE.restrict.level(), level=maxLevel))
            return text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(description))
        elif cycle.endDate - currentTime < time_utils.ONE_DAY:
            icon = icons.inProgress(vspace=-3)
            messageID = _R_EPIC_BATTLE.timeLeft
            valueStyle = text_styles.stats
            timeStr = valueStyle(backport.text(R.strings.epic_battle.questsTooltip.epicBattle.lessThanDay()))
            textStyle = text_styles.main
            description = textStyle(backport.text(messageID(), cycle=int2roman(cycle.ordinalNumber), time=timeStr))
            return text_styles.concatStylesWithSpace(icon, description)
        elif all((q.isCompleted() for q in quests)) and self._eventProgression.isDailyQuestsRefreshAvailable():
            data = time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
            valueStyle = text_styles.tutorial
            timeToStr = valueStyle(getTimeStr(data, R.strings.menu.Time.timeLeftShort))
            icon = icons.clockGold()
            textStyle = text_styles.tutorial
            description = textStyle(backport.text(_R_EPIC_BATTLE.startIn(), time=timeToStr))
            return text_styles.concatStylesWithSpace(icon, description)
        else:
            getDate = lambda c: c.endDate
            messageID = _R_EPIC_BATTLE.timeLeft
            icon = icons.inProgress(vspace=-3)
            textStyle = text_styles.main
            valueStyle = text_styles.stats
            timeToStr = valueStyle(getTimeStr(getDate(cycle) - currentTime, R.strings.menu.Time.timeLeftShort))
            description = textStyle(backport.text(messageID(), cycle=int2roman(cycle.ordinalNumber), time=timeToStr))
            return text_styles.concatStylesWithSpace(icon, description)


class CompletedQuestsTooltipData(EventProgressionQuestsTooltipData):

    def _packHeader(self, quests):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(self._eventProgression.questTooltipHeaderTxtId)), img=backport.image(self._eventProgression.questTooltipHeaderIconId), txtPadding=formatters.packPadding(top=18, bottom=-12), txtOffset=20)

    @classmethod
    def _isQuestCompleted(cls, _):
        return True

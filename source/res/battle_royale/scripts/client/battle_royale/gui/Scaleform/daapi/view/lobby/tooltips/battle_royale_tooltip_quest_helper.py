# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tooltips/battle_royale_tooltip_quest_helper.py
from helpers import time_utils
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import IBattleRoyaleController
from gui.impl.gen import R
from helpers import int2roman
from gui.impl import backport
from gui.impl.backport import getTillTimeStringByRClass as getTimeStr
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles, icons
from gui.server_events.awards_formatters import AWARDS_SIZES, getEpicViewAwardPacker
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
_R_BATTLE_ROYALE = R.strings.battle_royale.questsTooltip

@replace_none_kwargs(battleRoyaleController=IBattleRoyaleController)
def getQuestsDescriptionForHangarFlag(battleRoyaleController=None):
    quests = battleRoyaleController.getQuests()
    season = battleRoyaleController.getCurrentSeason() or battleRoyaleController.getNextSeason()
    currentTime = time_utils.getCurrentLocalServerTimestamp()
    cycle = season.getCycleInfo()
    if not battleRoyaleController.isActive() or cycle is None:
        return ''
    elif cycle.endDate - currentTime < time_utils.ONE_DAY:
        icon = icons.inProgress(vspace=-3)
        messageID = _R_BATTLE_ROYALE.timeLeft
        valueStyle = text_styles.stats
        timeStr = valueStyle(backport.text(R.strings.battle_royale.questsTooltip.lessThanDay()))
        textStyle = text_styles.main
        description = textStyle(backport.text(messageID(), cycle=int2roman(cycle.ordinalNumber), time=timeStr))
        return text_styles.concatStylesWithSpace(icon, description)
    elif all((q.isCompleted() for _, q in quests.items())):
        data = time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
        valueStyle = text_styles.tutorial
        timeToStr = valueStyle(getTimeStr(data, R.strings.battle_royale.questsTooltip.timeLeftShort))
        icon = icons.clockGold()
        textStyle = text_styles.tutorial
        description = textStyle(backport.text(_R_BATTLE_ROYALE.startIn(), time=timeToStr))
        return text_styles.concatStylesWithSpace(icon, description)
    else:
        getDate = lambda c: c.endDate
        messageID = _R_BATTLE_ROYALE.timeLeft
        icon = icons.inProgress(vspace=-3)
        textStyle = text_styles.main
        valueStyle = text_styles.stats
        timeToStr = valueStyle(getTimeStr(getDate(cycle) - currentTime, R.strings.battle_royale.questsTooltip.timeLeftShort))
        description = textStyle(backport.text(messageID(), cycle=int2roman(cycle.ordinalNumber), time=timeToStr))
        return text_styles.concatStylesWithSpace(icon, description)


def getQuestTooltipBlock(quest):
    return formatters.packBuildUpBlockData([_packQuestInfo(quest), _packQuestRewards(quest)])


def _packQuestInfo(quest):
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


def _packQuestRewards(quest):
    packer = getEpicViewAwardPacker()
    return formatters.packBuildUpBlockData([ _packQuestReward(bonus) for bonus in packer.format(quest.getBonuses()) ], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=20, right=20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)


def _packQuestReward(bonus):
    if bonus.label.startswith('x'):
        align = BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT
        padding = formatters.packPadding(top=-14, right=12)
    else:
        align = BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER
        padding = formatters.packPadding(top=-14)
    iconBlock = formatters.packQuestRewardItemBlockData(img=bonus.getImage(AWARDS_SIZES.SMALL), overlayPath=bonus.getOverlayIcon(AWARDS_SIZES.SMALL), overlayPadding=formatters.packPadding(left=-24, top=-24), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
    textBlock = formatters.packAlignedTextBlockData(text=bonus.getFormattedLabel(), align=align, padding=padding)
    return formatters.packBuildUpBlockData(blocks=[iconBlock, textBlock], blockWidth=72, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=-6))

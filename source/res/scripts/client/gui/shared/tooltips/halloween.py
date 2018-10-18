# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/halloween.py
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.awards_formatters import AWARDS_SIZES, getHalloweenProgressAwardPacker
from gui.shared.formatters import text_styles as styles
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.formatters import packBuildUpBlockData, packImageTextBlockData, packPadding, packTextBlockData
from helpers.i18n import makeString
from helpers.time_utils import getTimeString
_TOOLTIP_WIDTH = 320
_BONUS_DEFAULT_FORMAT = styles.main
_BONUS_FORMAT_OVERRIDES = {'xpFactorEliteHE': styles.gold}

def packBonus(bonus):
    name = bonus.bonusName
    desc = TOOLTIPS.getAwardHeader(name)
    img = bonus.getImage(AWARDS_SIZES.SMALL)
    style = _BONUS_FORMAT_OVERRIDES.get(name, _BONUS_DEFAULT_FORMAT)
    return packImageTextBlockData(title=style(bonus.label), desc=style(desc), img=img)


class BaseTooltip(BlocksTooltipData):
    title = makeString(TOOLTIPS.HALLOWEEN_TITLE)
    awardPacker = getHalloweenProgressAwardPacker()

    def __init__(self, context):
        super(BaseTooltip, self).__init__(context, None)
        self._setWidth(_TOOLTIP_WIDTH)
        return

    def getLevelStatus(self, item, currentLevel=None, maxLevelAvailable=None):
        raise NotImplementedError

    def _packBlocks(self, level, currentLevel=None, maxLevelAvailable=None, *args, **kwargs):
        if level is None:
            return super(BaseTooltip, self)._packBlocks(*args)
        else:
            ctx = self.context
            progress = ctx.getProgress()
            item = ctx.buildItem(level)
            levelTxt = makeString(TOOLTIPS.HALLOWEEN_COURAGELEVEL, level=level)
            bonusDescrTxt = getTimeString(progress.getFinishTime(), TOOLTIPS.HALLOWEEN_BONUSDESCRIPTION)
            levelStatusTxt = self.getLevelStatus(item)
            body = [packTextBlockData(styles.highTitle(self.title)), packTextBlockData(styles.main(bonusDescrTxt), padding=packPadding(top=10, bottom=20)), packTextBlockData(styles.middleTitle(levelTxt), padding=packPadding(bottom=10))]
            for b in self.awardPacker.format(item.getBonuses()):
                body.append(packBonus(b))

            body.append(packTextBlockData(styles.main(levelStatusTxt), padding=packPadding(top=10)))
            blocks = super(BaseTooltip, self)._packBlocks(level, *args, **kwargs)
            blocks.append(packBuildUpBlockData(body))
            return blocks


class ProgressTooltip(BaseTooltip):

    def getLevelStatus(self, item, currentLevel=None, maxLevelAvailable=None):
        progress = self.context.getProgress()
        level = item.getLevel()
        currentLevel = currentLevel or progress.getCurrentProgressLevel()
        maxLevel = progress.getMaxLevel()
        if level == currentLevel:
            levelStatus = makeString(TOOLTIPS.HALLOWEEN_CURRENTLEVEL)
        elif level == maxLevel:
            levelStatus = makeString(TOOLTIPS.HALLOWEEN_MAXLEVEL)
        elif level < currentLevel:
            levelStatus = makeString(TOOLTIPS.HALLOWEEN_LEVELACHIEVED)
        elif level > currentLevel:
            if maxLevelAvailable is not None:
                if level <= maxLevelAvailable:
                    levelStatus = makeString(TOOLTIPS.HALLOWEEN_LEVELAVAILABLE)
                else:
                    levelStatus = makeString(TOOLTIPS.HALLOWEEN_LEVELISNOTAVAILABLE)
            elif item.isUnlocked():
                levelStatus = makeString(TOOLTIPS.HALLOWEEN_LEVELAVAILABLE)
            else:
                levelStatus = getTimeString(item.getStartTime(), TOOLTIPS.HALLOWEEN_LEVELAVAILABILITY)
        else:
            levelStatus = 'Unknown'
        return levelStatus


class HangarTooltip(BaseTooltip):

    def getLevelStatus(self, item, currentLevel=None, maxLevelAvailable=None):
        progress = self.context.getProgress()
        level = item.getLevel()
        maxLevel = progress.getMaxLevel()
        if level == maxLevel:
            return makeString(TOOLTIPS.HALLOWEEN_MAXLEVEL)
        nextItem = progress.items[level + 1]
        if nextItem.isUnlocked():
            amount = nextItem.getMaxProgress() - nextItem.getCurrentProgress()
            tmpl = 'html_templates:lobby/quests/halloween'
            amountToNextLevel = makeHtmlString(tmpl, 'tooltipSouls', {'amount': amount})
            return amountToNextLevel
        return getTimeString(nextItem.getStartTime(), TOOLTIPS.HALLOWEEN_NEXTLEVELAVAILABILITY)

    def _packBlocks(self, level, *args, **kwargs):
        blocks = super(HangarTooltip, self)._packBlocks(level, *args, **kwargs)
        progress = self.context.getProgress()
        maxLevel = progress.getMaxLevel()
        if level != maxLevel:
            maxItem = progress.getMaxProgressItem()
            levelTxt = makeString(TOOLTIPS.HALLOWEEN_COURAGELEVELMAX, level=maxLevel)
            body = [packTextBlockData(styles.middleTitle(levelTxt), padding=packPadding(bottom=10))]
            for b in self.awardPacker.format(maxItem.getBonuses()):
                body.append(packBonus(b))

            blocks.append(packBuildUpBlockData(body, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        return blocks

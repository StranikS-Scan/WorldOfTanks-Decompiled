# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_builders/progress_vos.py
import typing
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from gui.battle_royale.royale_builders import shared_vos
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
if typing.TYPE_CHECKING:
    from gui.battle_royale.royale_helpers.stats_composer import BattleRoyaleStatsComposer
    from gui.battle_royale.royale_models import Title

def getProgressStatsVO(statsComposer, isFirstEntry, blocks, firstTitleStepsCount):
    stats = None
    hasProgress = bool(statsComposer.battlesAmount)
    if hasProgress:
        stats = {BATTLEROYALE_CONSTS.STAT_TOP1: shared_vos.getSmallStatVO(statsComposer.top1Count, BATTLEROYALE_CONSTS.STAT_TOP1, BATTLEROYALE_CONSTS.STAT_TOP1, shared_vos.getTop1Tooltip(statsComposer)),
         BATTLEROYALE_CONSTS.STAT_MAX_KILLS: shared_vos.getSmallStatVO(statsComposer.maxKillsCount, BATTLEROYALE_CONSTS.STAT_MAX_KILLS, BATTLEROYALE_CONSTS.STAT_MAX_KILLS, shared_vos.getMaxKillsTooltip()),
         BATTLEROYALE_CONSTS.STAT_BATTLES_AMOUNT: shared_vos.getSmallStatVO(statsComposer.battlesAmount, BATTLEROYALE_CONSTS.STAT_BATTLES_AMOUNT, BATTLEROYALE_CONSTS.STAT_BATTLES_AMOUNT, shared_vos.getBattlesAmountTooltip())}
    stepsStr = backport.text(R.strings.battle_royale.mainPage.steps.stepsCount(), stepsCount=firstTitleStepsCount)
    stepsLabel = backport.text(R.strings.battle_royale.mainPage.steps.stepsLabel(), steps=stepsStr)
    data = {'stats': stats,
     'isFirstEntry': isFirstEntry,
     'stepsLabel': text_styles.promoTitle(stepsLabel),
     'stepsLabelSmall': text_styles.highTitle(stepsLabel),
     'stepsTitle': backport.text(R.strings.battle_royale.mainPage.steps.stepsTitle()),
     'stepsDescription': backport.text(R.strings.battle_royale.mainPage.steps.stepsDescription()),
     'stepsIcon': backport.image(R.images.gui.maps.icons.battleRoyale.shevron_tip()),
     'blocks': blocks}
    return data


def getTitleVO(title):
    steps = []
    achivedStepsCount = title.getAchievedStepsCount()
    for idx in range(1, title.getStepsCountToAchieve() + 1):
        if idx <= achivedStepsCount:
            steps.append(BATTLEROYALE_ALIASES.STEP_RECEIVED_STATE)
        steps.append(BATTLEROYALE_ALIASES.STEP_NOT_RECEIVED_STATE)

    return {'stepsData': {'steps': steps,
                   'infoText': '',
                   'hasTooltip': True},
     'titleLabel': backport.text(R.strings.battle_royale.mainPage.currentTitle()) if title.isCurrent() else '',
     'smallImageSrc': title.getIcon(BATTLEROYALE_ALIASES.TITLE_SMALL),
     'bigImageSrc': title.getIcon(BATTLEROYALE_ALIASES.TITLE_BIG),
     'hugeImageSrc': title.getIcon(BATTLEROYALE_ALIASES.TITLE_HUGE),
     'isAcquired': title.isAcquired(),
     'titleID': str(title.getID()),
     'hasTooltip': True}

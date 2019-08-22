# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_builders/progress_final_vos.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.battle_royale.royale_builders import shared_vos
if typing.TYPE_CHECKING:
    from gui.battle_royale.royale_models import Title
    from gui.battle_royale.royale_helpers.stats_composer import BattleRoyaleStatsComposer

def getDataVO(title):
    return {'label': backport.text(R.strings.battle_royale.progressPage.final.label(), titleID=title.getID()),
     'bigImageSrc': title.getIcon(BATTLEROYALE_ALIASES.TITLE_HUGE),
     'smallImageSrc': title.getIcon(BATTLEROYALE_ALIASES.TITLE_BIG),
     'titleID': str(title.getID())}


def getStatsVO(statsComposer):
    return {BATTLEROYALE_CONSTS.STAT_TOP1: shared_vos.getBigStatVO(statsComposer.top1Count, BATTLEROYALE_CONSTS.STAT_TOP1, BATTLEROYALE_CONSTS.STAT_TOP1, shared_vos.getTop1Tooltip(statsComposer)),
     BATTLEROYALE_CONSTS.STAT_MAX_KILLS: shared_vos.getBigStatVO(statsComposer.maxKillsCount, BATTLEROYALE_CONSTS.STAT_MAX_KILLS, BATTLEROYALE_CONSTS.STAT_MAX_KILLS, shared_vos.getMaxKillsTooltip()),
     BATTLEROYALE_CONSTS.STAT_BATTLES_AMOUNT: shared_vos.getSmallStatVO(statsComposer.battlesAmount, BATTLEROYALE_CONSTS.STAT_BATTLES_AMOUNT, BATTLEROYALE_CONSTS.STAT_BATTLES_AMOUNT, shared_vos.getBattlesAmountTooltip()),
     BATTLEROYALE_CONSTS.STAT_KILLS_AMOUNT: shared_vos.getSmallStatVO(statsComposer.killsAmount, BATTLEROYALE_CONSTS.STAT_KILLS_AMOUNT, BATTLEROYALE_CONSTS.STAT_KILLS_AMOUNT, shared_vos.getKillsAmountTooltip())}

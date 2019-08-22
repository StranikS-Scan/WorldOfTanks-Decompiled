# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_builders/shared_vos.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.shared.formatters import text_styles
from gui.battle_royale.royale_helpers import makeStatTooltip
from gui.battle_royale.royale_formatters import getIntegerStrStat
if typing.TYPE_CHECKING:
    from gui.battle_royale.royale_models import Title
    from gui.battle_royale.royale_helpers.stats_composer import BattleRoyaleStatsComposer

def getTitleTooltipVO(title, isEnabled=False, imageSize=BATTLEROYALE_ALIASES.TITLE_MEDIUM):
    return {'titleImage': title.getIcon(imageSize),
     'isEnabled': isEnabled}


def getSmallStatVO(value, statKey, iconKey, tooltip):
    return {'icon': iconKey,
     'label': text_styles.alignText(text_styles.main(backport.text(R.strings.battle_royale.progressPage.stats.dyn(statKey)())), 'center'),
     'value': text_styles.superPromoTitle(getIntegerStrStat(value)),
     'tooltip': tooltip}


def getBigStatVO(value, statKey, iconKey, tooltip):
    return {'icon': iconKey,
     'label': text_styles.alignText(text_styles.mainBig(backport.text(R.strings.battle_royale.progressPage.stats.dyn(statKey)())), 'center'),
     'value': text_styles.grandTitle(getIntegerStrStat(value)),
     'tooltip': tooltip}


def getTop1Tooltip(statsComposer):
    return makeStatTooltip(BATTLEROYALE_CONSTS.STAT_TOP1, top1Solo=getIntegerStrStat(statsComposer.top1SoloCount), top1Squad=getIntegerStrStat(statsComposer.top1SquadCount))


def getMaxKillsTooltip():
    return makeStatTooltip(BATTLEROYALE_CONSTS.STAT_MAX_KILLS, eventName=backport.text(R.strings.tooltips.battle_royale.progressPage.eventName()))


def getBattlesAmountTooltip():
    return makeStatTooltip(BATTLEROYALE_CONSTS.STAT_BATTLES_AMOUNT, eventName=backport.text(R.strings.tooltips.battle_royale.progressPage.eventName()))


def getKillsAmountTooltip():
    return makeStatTooltip(BATTLEROYALE_CONSTS.STAT_KILLS_AMOUNT, eventName=backport.text(R.strings.tooltips.battle_royale.progressPage.eventName()))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/divisions_vos.py
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles import ranked_formatters
from gui.ranked_battles.ranked_builders.shared_vos import getStatVO
from gui.shared.formatters import text_styles

def getDivisionVO(division):
    return {'id': division.getUserID(),
     'name': text_styles.middleTitle(division.getUserName()),
     'isCompleted': division.isCompleted(),
     'isLocked': not division.isUnlocked()}


def getDivisionStatsVO(divisionEfficiencyPercent, seasonEfficiencyPercent):
    return {'divisionEfficiency': getStatVO(ranked_formatters.getFloatPercentStrStat(divisionEfficiencyPercent), 'divisionEfficiency', 'divisionEfficiency', 'divisionEfficiency'),
     'seasonEfficiency': getStatVO(ranked_formatters.getFloatPercentStrStat(seasonEfficiencyPercent), 'seasonEfficiency', 'efficiency', 'seasonEfficiency')}


def getRankVO(rank):
    steps = []
    achivedStepsCount = rank.getAchievedStepsCount()
    for idx in range(1, rank.getStepsCountToAchieve() + 1):
        if idx <= achivedStepsCount:
            steps.append(RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE)
        steps.append(RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE)

    shield = None
    shieldStatus = rank.getShieldStatus()
    if shieldStatus is not None and shieldStatus.hp > 0:
        shortcut = R.images.gui.maps.icons.rankedBattles.ranks.shields
        hpShortcut = R.images.gui.maps.icons.rankedBattles.ranks.shields.plate
        shieldKey = 'c_{}'.format(shieldStatus.hp)
        shield = {'smallImageSrc': backport.image(shortcut.dyn(RANKEDBATTLES_ALIASES.WIDGET_SMALL)()),
         'bigImageSrc': backport.image(shortcut.dyn(RANKEDBATTLES_ALIASES.WIDGET_BIG)()),
         'hugeImageSrc': backport.image(shortcut.dyn(RANKEDBATTLES_ALIASES.WIDGET_HUGE)()),
         'smallPlateSrc': backport.image(hpShortcut.dyn(RANKEDBATTLES_ALIASES.WIDGET_SMALL).dyn(shieldKey)()),
         'mediumPlateSrc': backport.image(hpShortcut.dyn(RANKEDBATTLES_ALIASES.WIDGET_MEDIUM).dyn(shieldKey)()),
         'bigPlateSrc': backport.image(hpShortcut.dyn(RANKEDBATTLES_ALIASES.WIDGET_BIG).dyn(shieldKey)()),
         'hugePlateSrc': backport.image(hpShortcut.dyn(RANKEDBATTLES_ALIASES.WIDGET_HUGE).dyn(shieldKey)())}
    return {'stepsData': {'steps': steps,
                   'infoText': ''},
     'rankLabel': backport.text(R.strings.ranked_battles.rankedBattleMainView.divisions.currentRank()) if rank.isCurrent() else '',
     'smallImageSrc': rank.getIcon(RANKEDBATTLES_ALIASES.WIDGET_SMALL),
     'bigImageSrc': rank.getIcon(RANKEDBATTLES_ALIASES.WIDGET_BIG),
     'hugeImageSrc': rank.getIcon(RANKEDBATTLES_ALIASES.WIDGET_HUGE),
     'isAcquired': rank.isAcquired(),
     'rankID': str(rank.getID()),
     'hasTooltip': True,
     'shield': shield}

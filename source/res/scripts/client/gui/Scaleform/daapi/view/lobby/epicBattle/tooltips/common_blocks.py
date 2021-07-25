# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/tooltips/common_blocks.py
import typing
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getTimeToEndStr, getTimeToStartStr
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.tooltips import formatters
from helpers import int2roman, time_utils, dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def packEpicBattleInfoBlock(epicController=None):
    descLvl = text_styles.stats(backport.text(R.strings.epic_battle.selectorTooltip.epicBattle.bodyVehicleLevel(), level=toRomanRangeString(epicController.getValidVehicleLevels())))
    season = epicController.getCurrentSeason()
    cycle = None
    cycleNumber = None
    if season is not None and not season.isSingleCycleSeason():
        hasActiveCycle = season.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp())
        if epicController.isEnabled() and hasActiveCycle:
            cycle = season.getCycleInfo()
        else:
            cycle = season.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
    if cycle is not None:
        cycleNumber = cycle.getEpicCycleNumber()
    if cycleNumber:
        titleStr = R.strings.epic_battle.tooltips.common.titleWithCycle()
    else:
        titleStr = R.strings.epic_battle.tooltips.common.title()
    return formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(titleStr, season=int2roman(cycleNumber))), desc=text_styles.main(backport.text(R.strings.epic_battle.selectorTooltip.epicBattle.body(), bodyVehicleLevel=descLvl)), padding=formatters.packPadding(top=20, left=20, right=20), descPadding=formatters.packPadding(right=30))


@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def packEpicBattleSeasonBlock(epicController=None):
    if not epicController.isEnabled():
        return
    else:
        season = epicController.getCurrentSeason() or epicController.getNextSeason()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        if epicController.isCurrentCycleActive():
            cycle = season.getCycleInfo()
            getDate = lambda c: c.endDate
            getTimeToStr = getTimeToEndStr
        else:
            cycle = season.getNextByTimeCycle(currentTime) if season else None
            if cycle and cycle.announceOnly:
                return
            getDate = lambda c: c.startDate
            getTimeToStr = getTimeToStartStr
        if cycle is not None:
            description = getTimeToStr(getDate(cycle) - currentTime)
        elif season and season.getEndDate() > currentTime:
            description = backport.text(R.strings.epic_battle.tooltips.widget.allCyclesFinished())
        else:
            description = backport.text(R.strings.epic_battle.tooltips.widget.seasonFinished())
        return formatters.packBuildUpBlockData([formatters.packImageTextBlockData(desc=text_styles.main(description), padding=formatters.packPadding(left=20, right=20))])

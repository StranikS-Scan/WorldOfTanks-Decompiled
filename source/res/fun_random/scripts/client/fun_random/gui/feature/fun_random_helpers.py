# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/fun_random_helpers.py
from gui.impl import backport
from gui.shared.formatters.ranges import toRomanRangeString
from helpers import dependency, int2roman
from skeletons.gui.game_control import IFunRandomController

@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def getDisabledFunRandomTooltip(tooltipStr, funRandomCtrl=None):
    availableLevels = funRandomCtrl.getModeSettings().levels
    minLevel, maxLevel = min(availableLevels), max(availableLevels)
    levels = int2roman(minLevel) if minLevel == maxLevel else toRomanRangeString(availableLevels)
    return backport.text(tooltipStr, levels=levels)

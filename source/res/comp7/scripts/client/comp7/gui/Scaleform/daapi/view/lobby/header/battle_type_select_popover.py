# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/header/battle_type_select_popover.py
from __future__ import absolute_import
from adisp import adisp_process
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.comp7_constants import PREBATTLE_ACTION_NAME as COMP7_PREBATTLE_ACTION_NAME
from gui.Scaleform.daapi.view.lobby.header.BattleTypeSelectPopover import BattleTypeSelectPopover
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7BattleTypeSelectPopover(BattleTypeSelectPopover):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def getTooltipData(self, itemData, itemIsDisabled):
        if itemData == COMP7_PREBATTLE_ACTION_NAME.COMP7:
            self._tooltip, isSpecial = self.__getComp7AvailabilityData()
            result = {'isSpecial': isSpecial,
             'tooltip': self._tooltip}
            return result
        return super(Comp7BattleTypeSelectPopover, self).getTooltipData(itemData, itemIsDisabled)

    @adisp_process
    def __getComp7AvailabilityData(self):
        return (COMP7_TOOLTIPS.COMP7_SELECTOR_INFO, True) if self.__comp7Controller.isAvailable() else (COMP7_TOOLTIPS.COMP7_SELECTOR_UNAVAILABLE_INFO, True)

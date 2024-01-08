# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/frontline/ammunition_setup.py
from gui.impl.lobby.tank_setup.ammunition_setup.hangar import HangarAmmunitionSetupView
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

class FrontlineAmmunitionSetupView(HangarAmmunitionSetupView):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.frontline.lobby.tooltips.SkillOrderTooltip():
            from frontline.gui.impl.lobby.tooltips.skill_order_tooltip import SkillOrderTooltip
            return SkillOrderTooltip()
        if contentID == R.views.frontline.lobby.tooltips.LevelReservesTooltip():
            from frontline.gui.impl.lobby.tooltips.level_reserves_tooltip import LevelReservesTooltip
            return LevelReservesTooltip()
        if contentID == R.views.frontline.lobby.tooltips.NotEnoughPointsTooltip():
            from frontline.gui.impl.lobby.tooltips.not_enough_points_tooltip import NotEnoughPointsTooltip
            return NotEnoughPointsTooltip(event.getArgument('points'))
        return super(FrontlineAmmunitionSetupView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        super(FrontlineAmmunitionSetupView, self)._addListeners()
        self.__epicController.onUpdated += self.__onEpicUpdated

    def _removeListeners(self):
        self.__epicController.onUpdated -= self.__onEpicUpdated
        super(FrontlineAmmunitionSetupView, self)._removeListeners()

    def __onEpicUpdated(self, diff):
        if 'isEnabled' in diff and not diff['isEnabled']:
            super(FrontlineAmmunitionSetupView, self)._closeWindow()

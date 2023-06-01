# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/frontline/ammunition_panel.py
from gui.impl.gen import R
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView

class FrontlineAmmunitionPanelView(HangarAmmunitionPanelView):

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.frontline.lobby.tooltips.SkillOrderTooltip():
            from frontline.gui.impl.lobby.tooltips.skill_order_tooltip import SkillOrderTooltip
            return SkillOrderTooltip()
        return super(FrontlineAmmunitionPanelView, self).createToolTipContent(event, contentID)

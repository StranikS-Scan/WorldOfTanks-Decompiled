# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tooltips/skill_order_tooltip.py
from frameworks.wulf import ViewSettings, ViewFlags, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class SkillOrderTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.frontline.lobby.tooltips.SkillOrderTooltip(), ViewFlags.VIEW, ViewModel())
        super(SkillOrderTooltip, self).__init__(settings)

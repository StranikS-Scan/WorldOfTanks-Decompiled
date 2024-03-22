# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/skill_untrained_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class SkillUntrainedTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.crew.tooltips.SkillUntrainedTooltip(), model=ViewModel())
        super(SkillUntrainedTooltip, self).__init__(settings)

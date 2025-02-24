# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/crew_members_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.crew_members_tooltip_model import CrewMembersTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class CrewMembersTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.comp7.lobby.tooltips.CrewMembersTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = CrewMembersTooltipModel()
        super(CrewMembersTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrewMembersTooltip, self).getViewModel()

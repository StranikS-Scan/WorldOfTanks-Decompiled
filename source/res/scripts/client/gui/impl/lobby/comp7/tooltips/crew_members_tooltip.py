# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/crew_members_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.crew_members_tooltip_model import CrewMembersTooltipModel
from gui.impl.pub import ViewImpl

class CrewMembersTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.lobby.comp7.tooltips.CrewMembersTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = CrewMembersTooltipModel()
        super(CrewMembersTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrewMembersTooltip, self).getViewModel()

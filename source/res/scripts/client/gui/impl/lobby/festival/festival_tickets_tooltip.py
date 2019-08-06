# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_tickets_tooltip.py
from frameworks.wulf import ViewFlags, View
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_tickets_tooltip_model import FestivalTicketsTooltipModel

class FestivalTicketsTooltip(View):
    __slots__ = ()

    def __init__(self, tickets):
        super(FestivalTicketsTooltip, self).__init__(R.views.lobby.festival.festival_tickets_tooltip.FestivalTicketsTooltip(), ViewFlags.COMPONENT, FestivalTicketsTooltipModel, tickets)

    def _initialize(self, tickets):
        super(FestivalTicketsTooltip, self)._initialize()
        self.viewModel.setTicketsStr(tickets)

    @property
    def viewModel(self):
        return super(FestivalTicketsTooltip, self).getViewModel()

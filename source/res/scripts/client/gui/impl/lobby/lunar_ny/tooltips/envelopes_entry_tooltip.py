# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/tooltips/envelopes_entry_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.tooltips.envelopes_entry_tooltip_model import EnvelopesEntryTooltipModel
from gui.impl.pub import ViewImpl

class EnvelopesEntryTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.lunar_ny.tooltips.EnvelopesEntryTooltip())
        settings.model = EnvelopesEntryTooltipModel()
        super(EnvelopesEntryTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

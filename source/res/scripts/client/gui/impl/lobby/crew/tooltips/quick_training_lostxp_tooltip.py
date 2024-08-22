# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/quick_training_lostxp_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class QuickTrainingLostXpTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.crew.tooltips.QuickTrainingLostXpTooltip(), model=ViewModel())
        super(QuickTrainingLostXpTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QuickTrainingLostXpTooltip, self).getViewModel()

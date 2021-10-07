# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/accelerate_training_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.accelerate_training_tooltip_view_model import AccelerateTrainingTooltipViewModel
from gui.impl.pub import ViewImpl

class AccelerateTrainingTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.crew.AccelerateTrainingTooltipView(), model=AccelerateTrainingTooltipViewModel())
        super(AccelerateTrainingTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AccelerateTrainingTooltipView, self).getViewModel()

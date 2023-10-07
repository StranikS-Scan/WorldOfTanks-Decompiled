# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/experience_stepper_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class ExperienceStepperTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.crew.tooltips.ExperienceStepperTooltip(), model=ViewModel())
        super(ExperienceStepperTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ExperienceStepperTooltip, self).getViewModel()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/armory_yard_token_stepper_tooltip_view.py
from frameworks.wulf import ViewSettings
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips import armory_yard_token_stepper_tooltip_view_model as tooltip_view_model
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class ArmoryYardTokenStepperTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.ArmoryYardTokenStepperTooltipView())
        settings.model = tooltip_view_model.ArmoryYardTokenStepperTooltipViewModel()
        super(ArmoryYardTokenStepperTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmoryYardTokenStepperTooltipView, self).getViewModel()

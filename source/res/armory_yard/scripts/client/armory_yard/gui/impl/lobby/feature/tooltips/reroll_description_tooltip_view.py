# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/reroll_description_tooltip_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.reroll_description_tooltip_view_model import RerollDescriptionTooltipViewModel
from gui.impl.pub import ViewImpl

class RerollDescriptionTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = RerollDescriptionTooltipViewModel()
        super(RerollDescriptionTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RerollDescriptionTooltipView, self).getViewModel()

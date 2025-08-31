# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/play_streak/random_goodie_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.tooltips.random_goodie_tooltip_model import RandomGoodieTooltipModel
from gui.impl.pub import ViewImpl

class RandomGoodieTooltip(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.daily.tooltips.RandomGoodieTooltip())
        settings.model = RandomGoodieTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(RandomGoodieTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RandomGoodieTooltip, self).getViewModel()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/advanced_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.advanced_tooltip_view_model import AdvancedTooltipViewModel
from gui.impl.pub import ViewImpl

class AdvancedTooltipView(ViewImpl):
    __slots__ = ('_movie', '_header', '_description')

    def __init__(self, movie, header, description):
        settings = ViewSettings(R.views.lobby.crew.tooltips.AdvancedTooltipView(), model=AdvancedTooltipViewModel())
        super(AdvancedTooltipView, self).__init__(settings)
        self._movie = movie
        self._header = header
        self._description = description

    @property
    def viewModel(self):
        return super(AdvancedTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(AdvancedTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setMovie(self._movie)
            tx.setHeader(self._header)
            tx.setDescription(self._description)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/wt_event/players_panel_view.py
import logging
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.wt_event.players_panel_view_model import PlayersPanelViewModel
from gui.impl.pub import ViewImpl, WindowImpl
_logger = logging.getLogger(__name__)

class PlayersPanelView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.battle.wt_event.PlayersPanelView(), flags=ViewFlags.COMPONENT, model=PlayersPanelViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(PlayersPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PlayersPanelView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self._updateViewModel()

    def _updateViewModel(self):
        _logger.debug('PlayersPanelView::UpdatingViewModel')
        with self.getViewModel().transaction() as tx:
            tx.setTitle('ATATA')


class PlayersPanelWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(PlayersPanelWindow, self).__init__(WindowFlags.WINDOW, content=PlayersPanelView(), parent=parent)

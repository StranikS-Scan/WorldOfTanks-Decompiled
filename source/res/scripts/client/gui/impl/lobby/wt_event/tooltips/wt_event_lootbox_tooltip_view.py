# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_lootbox_tooltip_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view_model import WtEventLootboxTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
_logger = logging.getLogger(__name__)

class WtEventLootBoxTooltipView(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.tooltips.WtEventLootBoxTooltipView(), model=WtEventLootboxTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventLootBoxTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventLootBoxTooltipView, self)._onLoading(*args, **kwargs)
        isHunterLootBox = kwargs.get('isHunterLootBox')
        if isHunterLootBox is None:
            _logger.error('Incorrect type of the lootBox to show the tooltip')
            return
        else:
            with self.viewModel.transaction() as model:
                model.setIsHunterLootBox(isHunterLootBox)
            return

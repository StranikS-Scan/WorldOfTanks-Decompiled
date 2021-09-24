# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_info_tooltip_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_info_tooltip_view_model import WtEventInfoTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.wt_event.wt_event_simple_bonus_packers import STATUS_GETTERS
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.event.WtEventPortals.collectionTooltip

class WtEventInfoTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.tooltips.WtEventInfoTooltipView(), model=WtEventInfoTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventInfoTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventInfoTooltipView, self)._onLoading(*args, **kwargs)
        tooltipType = kwargs.get('tooltipType')
        if tooltipType is None:
            _logger.error('Invalid tooltipType to show EventInfoTooltip')
            return
        else:
            with self.viewModel.transaction() as model:
                model.setTitle(_STR_PATH.dyn(tooltipType).title())
                model.setDescription(_STR_PATH.dyn(tooltipType).description())
                statusGetter = STATUS_GETTERS.get(tooltipType)
                if statusGetter is not None:
                    statusResID = statusGetter()
                    model.setInfo(_STR_PATH.dyn(tooltipType).status.dyn(statusResID)())
            return

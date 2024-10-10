# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_event_info_tooltip_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_event_info_tooltip_view_model import WtEventInfoTooltipViewModel
from gui.impl.pub import ViewImpl
from white_tiger.gui.impl.lobby.packers.wt_event_simple_bonus_packers import STATUS_GETTERS
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.event.WtEventPortals.collectionTooltip

class WtEventInfoTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.tooltips.InfoTooltipView(), model=WtEventInfoTooltipViewModel())
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
                tooltip = _STR_PATH.dyn(tooltipType)
                model.setTitle(tooltip.title())
                if tooltip.dyn('description').exists():
                    model.setDescription(tooltip.description())
                statusGetter = STATUS_GETTERS.get(tooltipType)
                if statusGetter is not None:
                    statusResID = statusGetter()
                    model.setInfo(tooltip.status.dyn(statusResID)())
            return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/simply_format_tooltip.py
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel

class SimplyFormatTooltipView(ViewImpl):

    def __init__(self, header, body):
        settings = ViewSettings(R.views.halloween.lobby.tooltips.SimplyFormatTooltip(), model=SimpleTooltipContentModel())
        settings.args = (header, body)
        super(SimplyFormatTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SimplyFormatTooltipView, self).getViewModel()

    def _onLoading(self, header, body):
        self.viewModel.setHeader(header)
        self.viewModel.setBody(body)

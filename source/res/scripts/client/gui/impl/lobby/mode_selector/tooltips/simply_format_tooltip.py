# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/tooltips/simply_format_tooltip.py
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel

def createSimpleTooltip(parent, event, header='', body=''):
    window = DecoratedTooltipWindow(parent=parent, content=SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), body=body, header=header))
    window.load()
    window.move(event.mouse.positionX, event.mouse.positionY)
    return window


class SimplyFormatTooltipView(ViewImpl):

    def __init__(self, header, body):
        settings = ViewSettings(R.views.lobby.mode_selector.tooltips.SimplyFormatTooltip(), model=SimpleTooltipContentModel())
        settings.args = (header, body)
        super(SimplyFormatTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SimplyFormatTooltipView, self).getViewModel()

    def _onLoading(self, header, body):
        self.viewModel.setHeader(header)
        self.viewModel.setBody(body)

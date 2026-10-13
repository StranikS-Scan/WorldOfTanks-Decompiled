# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/simple_format_tooltip.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel

class SimpleFormatTooltipView(ViewImpl):

    def __init__(self, header, body):
        settings = ViewSettings(R.views.halloween.mono.lobby.tooltips.simple_format_tooltip(), model=SimpleTooltipContentModel())
        settings.args = (header, body)
        super(SimpleFormatTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SimpleFormatTooltipView, self).getViewModel()

    def _onLoading(self, header, body):
        self.viewModel.setHeader(header)
        self.viewModel.setBody(body)

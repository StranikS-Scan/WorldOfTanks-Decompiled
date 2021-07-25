# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/colored_simple_tooltip.py
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel

class ColoredSimpleTooltip(View):
    __slots__ = ()

    def __init__(self, header, body, note='', alert=''):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.ColoredSimpleTooltip())
        settings.model = SimpleTooltipContentModel()
        settings.args = (header,
         body,
         note,
         alert)
        super(ColoredSimpleTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ColoredSimpleTooltip, self).getViewModel()

    def _onLoading(self, header, body, note, alert):
        with self.viewModel.transaction() as tx:
            tx.setHeader(header)
            tx.setBody(body)
            tx.setNote(note)
            tx.setAlert(alert)

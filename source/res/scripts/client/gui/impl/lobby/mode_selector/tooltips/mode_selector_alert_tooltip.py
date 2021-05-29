# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/tooltips/mode_selector_alert_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.pub import ViewImpl

class AlertTooltip(ViewImpl):

    def __init__(self, header, body, alert):
        self.__header = header
        self.__body = body
        self.__alert = alert
        settings = ViewSettings(R.views.lobby.mode_selector.tooltips.AlertTooltip(), model=SimpleTooltipContentModel())
        super(AlertTooltip, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        model = self.getViewModel()
        model.setHeader(self.__header)
        model.setBody(self.__body)
        model.setAlert(self.__alert)

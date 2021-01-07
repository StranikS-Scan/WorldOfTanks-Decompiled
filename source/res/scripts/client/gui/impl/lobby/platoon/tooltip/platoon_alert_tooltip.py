# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/tooltip/platoon_alert_tooltip.py
from gui.impl.gen import R
from gui.impl import backport
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.platoon.alert_tooltip_model import AlertTooltipModel

class AlertTooltip(ViewImpl):

    def __init__(self, header, body):
        self.__header = header
        self.__body = body
        settings = ViewSettings(R.views.lobby.platoon.AlertTooltip(), model=AlertTooltipModel())
        super(AlertTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setHeader(backport.text(self.__header))
            model.setBody(backport.text(self.__body))

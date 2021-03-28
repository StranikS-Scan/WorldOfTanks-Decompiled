# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/bootcamp_progress_widget_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.bootcamp.bootcamp_progress_model import BootcampProgressModel
from bootcamp.Bootcamp import g_bootcamp

class BootcampProgressWidgetView(ViewImpl):
    __slots__ = ('__tooltipData',)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.bootcamp.BootcampProgressWidget())
        settings.flags = flags
        settings.model = BootcampProgressModel()
        self.__tooltipData = {}
        super(BootcampProgressWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BootcampProgressWidgetView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId:
                tooltipData = self.__tooltipData[int(tooltipId)]
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
        return

    def _onLoading(self, *args, **kwargs):
        super(BootcampProgressWidgetView, self)._onLoading()
        with self.viewModel.transaction() as model:
            g_bootcamp.fillProgressBar(model, self.__tooltipData)

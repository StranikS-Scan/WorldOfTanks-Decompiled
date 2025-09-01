# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/info_page_view.py
import typing
from config_schemas.umg_config import umgConfigSchema
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.user_missions.info_page_model import InfoPageModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_helpers import getRerollTimeout

class InfoPageView(ViewImpl):

    def __init__(self, settings, *args, **kwargs):
        super(InfoPageView, self).__init__(settings, args, kwargs)

    @property
    def viewModel(self):
        return super(InfoPageView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onViewClose),)

    def _onLoading(self, *args, **kwargs):
        super(InfoPageView, self)._onLoading(*args, **kwargs)
        self.viewModel.setRerollInterval(getRerollTimeout())
        self.viewModel.setIsWeeklySectionAvailable(umgConfigSchema.getModel().enableAllWeekly)

    def _onViewClose(self):
        self.destroyWindow()

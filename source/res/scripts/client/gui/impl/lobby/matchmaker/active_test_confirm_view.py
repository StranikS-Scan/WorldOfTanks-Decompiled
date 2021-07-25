# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/matchmaker/active_test_confirm_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.matchmaker.active_test_confirm_view_model import ActiveTestConfirmViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared import g_eventBus, events
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager

class ActiveTestConfirmView(FullScreenDialogView):
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.matchmaker.ActiveTestConfirmView(), model=ActiveTestConfirmViewModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__startTime = kwargs.pop('startTime')
        self.__finishTime = kwargs.pop('finishTime')
        self.__link = kwargs.pop('link')
        super(ActiveTestConfirmView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ActiveTestConfirmView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setClusterName(self.__connectionMgr.serverUserNameShort)
            tx.setTimeRangeStart(self.__startTime)
            tx.setTimeRangeEnd(self.__finishTime)
        self.viewModel.onOpenPortalClicked += self.__onOpenPortalClicked

    def _onInventoryResync(self, *args, **kwargs):
        pass

    def _finalize(self):
        self.viewModel.onOpenPortalClicked -= self.__onOpenPortalClicked

    def __onOpenPortalClicked(self):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=self.__link))

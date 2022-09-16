# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/base.py
import typing
if typing.TYPE_CHECKING:
    from typing import Union
    from gui.impl.gen.view_models.views.lobby.account_dashboard.account_dashboard_model import AccountDashboardModel

class FeatureItem(object):

    def __init__(self, viewModel):
        self._viewModel = viewModel

    def initialize(self, *args, **kwargs):
        pass

    def finalize(self):
        self._viewModel = None
        return

    def createToolTipContent(self, event, contentID):
        pass

    def createPopOverContent(self, event):
        pass

    def _fillModel(self, model):
        raise NotImplementedError

    def fill(self, ctx=None):
        if ctx is None:
            with self._viewModel.transaction() as tx:
                self._fillModel(tx)
        else:
            self._fillModel(ctx)
        return

    def getViewModel(self):
        return self._viewModel

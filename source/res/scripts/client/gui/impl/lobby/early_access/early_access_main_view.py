# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_main_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.early_access.early_access_quests_view_model import EarlyAccessQuestsViewModel
from gui.impl.pub import ViewImpl

class EarlyAccessMainView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = EarlyAccessQuestsViewModel()
        super(EarlyAccessMainView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessMainView, self).getViewModel()

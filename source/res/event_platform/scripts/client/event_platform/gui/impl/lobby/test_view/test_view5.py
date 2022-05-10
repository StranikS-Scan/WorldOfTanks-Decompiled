# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/lobby/test_view/test_view5.py
from frameworks.wulf import ViewFlags, ViewSettings
from event_platform.gui.impl.gen.view_models.views.lobby.test_view.test_view5_model import TestView5Model
from gui.impl.pub import ViewImpl

class TestView5(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = TestView5Model()
        super(TestView5, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TestView5, self).getViewModel()

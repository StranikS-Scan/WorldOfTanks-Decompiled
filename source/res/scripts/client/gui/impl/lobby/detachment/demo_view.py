# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/demo_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.demo.demo_view_model import DemoViewModel
from gui.development.ui.demo.wtypes_example.wtypes_popup import WTypesPopUpContent
_logger = logging.getLogger(__name__)

class DemoView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = DemoViewModel()
        super(DemoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DemoView, self).getViewModel()

    def createPopOverContent(self, event):
        return WTypesPopUpContent(R.images.gui.maps.icons.awards.battleSwords(), layoutID=R.views.GFDemoPopover())

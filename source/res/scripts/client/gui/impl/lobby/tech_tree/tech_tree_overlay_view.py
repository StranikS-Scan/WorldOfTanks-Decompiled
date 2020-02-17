# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tech_tree/tech_tree_overlay_view.py
import logging
from frameworks.wulf import ViewFlags
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.tech_tree.tech_tree_overlay_view_model import TechTreeOverlayViewModel
from gui.impl.pub import ViewImpl
logger = logging.getLogger(__name__)

class TechTreeOverlayView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = TechTreeOverlayViewModel()
        super(TechTreeOverlayView, self).__init__(settings)

    def _initialize(self, *args, **kwargs):
        super(TechTreeOverlayView, self)._initialize(*args, **kwargs)
        self.getViewModel().onCloseEvent += self.__onCloseEventHandler

    def _finalize(self):
        self.getViewModel().onCloseEvent -= self.__onCloseEventHandler
        super(TechTreeOverlayView, self)._finalize()

    def __onCloseEventHandler(self, _=None):
        self.destroyWindow()

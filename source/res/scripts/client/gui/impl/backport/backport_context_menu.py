# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_context_menu.py
import logging
from collections import namedtuple
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.context_menu_content_model import ContextMenuContentModel
from gui.impl.pub.context_menu_window import ContextMenuContent
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_logger = logging.getLogger(__name__)
_ContextMenuData = namedtuple('ContextMenuData', ('type', 'args'))

def createContextMenuData(contextMenuType, args=None):
    return _ContextMenuData(contextMenuType, args)


class BackportContextMenuContent(ContextMenuContent):
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, contextMenuData):
        settings = ViewSettings(R.views.common.BackportContextMenu())
        settings.model = ContextMenuContentModel()
        settings.args = (contextMenuData,)
        super(BackportContextMenuContent, self).__init__(settings)

    def _initialize(self, contextMenuData):
        super(BackportContextMenuContent, self)._initialize()
        contextMenuMgr = self.__appLoader.getApp().contextMenuManager
        if contextMenuMgr is not None:
            contextMenuMgr.onContextMenuHide += self.__contextMenuHideHandler
            contextMenuMgr.show(contextMenuData.type, contextMenuData.args)
        else:
            _logger.error("contextMenuMgr doesn't exist.")
        return

    def _initItems(self):
        pass

    def _onAction(self, actionID):
        pass

    def _finalize(self):
        contextMenuMgr = self.__appLoader.getApp().contextMenuManager
        if contextMenuMgr is not None:
            contextMenuMgr.onContextMenuHide -= self.__contextMenuHideHandler
            contextMenuMgr.pyHide()
        super(BackportContextMenuContent, self)._finalize()
        return

    def __contextMenuHideHandler(self):
        self.destroyWindow()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_context_menu.py
import logging
from collections import namedtuple
from frameworks.wulf import View, ViewModel, Window, ViewSettings, WindowSettings, WindowFlags
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_logger = logging.getLogger(__name__)
_ContextMenuData = namedtuple('ContextMenuData', ('type', 'args'))

def createContextMenuData(contextMenuType, args=None):
    return _ContextMenuData(contextMenuType, args)


class _BackportContextMenuContent(View):
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, contextMenuData):
        settings = ViewSettings(R.views.common.BackportContextMenu())
        settings.model = ViewModel()
        settings.args = (contextMenuData,)
        super(_BackportContextMenuContent, self).__init__(settings)

    def _initialize(self, contextMenuData):
        super(_BackportContextMenuContent, self)._initialize()
        contextMenuMgr = self.__appLoader.getApp().contextMenuManager
        if contextMenuMgr is not None:
            contextMenuMgr.onContextMenuHide += self.__contextMenuHideHandler
            contextMenuMgr.show(contextMenuData.type, contextMenuData.args)
        else:
            _logger.error("contextMenuMgr doesn't exist.")
        return

    def _finalize(self):
        contextMenuMgr = self.__appLoader.getApp().contextMenuManager
        if contextMenuMgr is not None:
            contextMenuMgr.onContextMenuHide -= self.__contextMenuHideHandler
            contextMenuMgr.pyHide()
        super(_BackportContextMenuContent, self)._finalize()
        return

    def __contextMenuHideHandler(self):
        self.destroyWindow()


class BackportContextMenuWindow(Window):
    __slots__ = ()

    def __init__(self, contextMenuData, parent):
        settings = WindowSettings()
        settings.flags = WindowFlags.CONTEXT_MENU
        settings.content = _BackportContextMenuContent(contextMenuData)
        settings.parent = parent
        super(BackportContextMenuWindow, self).__init__(settings)

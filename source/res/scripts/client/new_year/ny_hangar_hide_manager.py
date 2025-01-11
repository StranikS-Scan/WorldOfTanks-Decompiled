# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_hangar_hide_manager.py
import logging
import typing
import BigWorld
import AnimationSequence
import WebBrowser
from frameworks.wulf import WindowStatus, WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from helpers import dependency, isPlayerAccount
from skeletons.gui.impl import IGuiLoader
from gui.shared.event_dispatcher import showHangar
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)

def _subViewPredicate(window):
    return window.layer == WindowLayer.SUB_VIEW


@dependency.replace_none_kwargs(gui=IGuiLoader)
def _closeSubView(viewType, gui=None):
    windows = gui.windowsManager.findWindows(_subViewPredicate)
    if not windows:
        return
    window = windows[0]
    if isinstance(window, SFWindow) and window.content and window.content.alias == viewType:
        _logger.info('Close %r', window)
        window.destroy()


class NewYearHangarHideManager(object):
    __gui = dependency.descriptor(IGuiLoader)
    __instance = None

    def __init__(self):
        super(NewYearHangarHideManager, self).__init__()
        self.__isHangarInvisible = False
        self.__isStyleOpened = False
        self.__blockedByWindow = set()

    @classmethod
    def isInited(cls):
        return cls.__instance is not None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = NewYearHangarHideManager()
            cls.__instance.init()
        return cls.__instance

    def init(self):
        self.__gui.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def fini(self):
        self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        NewYearHangarHideManager.__instance = None
        return

    def openStyle(self):
        _logger.info('open style')
        self.__isStyleOpened = True
        self.__tryHideHangar()
        self.__updateStageVisibility()

    def closeStyle(self):
        _logger.info('close style')
        self.__isStyleOpened = False
        _closeSubView(VIEW_ALIAS.STYLE_PREVIEW)
        self.__tryShowHangar()
        self.__updateStageVisibility()

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        from gui.impl.lobby.loot_box.loot_box_helper import LootBoxHideableView
        window = self.__gui.windowsManager.getWindow(uniqueID)
        if newStatus == WindowStatus.LOADING:
            if window.content and isinstance(window.content, LootBoxHideableView):
                self.__block(uniqueID)
        elif newStatus == WindowStatus.DESTROYING:
            if window.content and isinstance(window.content, LootBoxHideableView):
                self.__release(uniqueID)

    def __block(self, uniqueID):
        self.__blockedByWindow.add(uniqueID)
        self.__tryHideHangar()

    def __release(self, uniqueID):
        self.__blockedByWindow.remove(uniqueID)
        self.__tryShowHangar()

    def __tryHideHangar(self):
        if self.__isHangarInvisible or not self.__blockedByWindow:
            return
        _logger.info('hide hangar')
        _closeSubView(VIEW_ALIAS.LOBBY_HANGAR)
        self.__isHangarInvisible = True
        self.__updateStageVisibility()

    def __tryShowHangar(self):
        if not self.__isHangarInvisible or self.__blockedByWindow or self.__isStyleOpened:
            return
        _logger.info('show hangar')
        windows = self.__gui.windowsManager.findWindows(_subViewPredicate)
        _logger.info(windows)
        if not windows and isPlayerAccount():
            showHangar()
        self.__isHangarInvisible = False
        self.__updateStageVisibility()
        self.fini()

    def __updateStageVisibility(self):
        value = not self.__isHangarInvisible or self.__isStyleOpened
        _logger.info('stage visible %r', value)
        if isPlayerAccount() and dependency.instance(IHangarSpace).spaceInited:
            BigWorld.worldDrawEnabled(value)
            AnimationSequence.setEnableAnimationSequenceUpdate(value)
            WebBrowser.pauseExternalCache(not value)

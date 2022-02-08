# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/__init__.py
import typing
from gui.impl.pub.window_loader_controller import WindowLoaderController
from skeletons.gui.game_control import IGameStateTracker
from skeletons.gui.impl import IGuiLoader, IFullscreenManager, INotificationWindowController
if typing.TYPE_CHECKING:
    from helpers.dependency import DependencyManager
__all__ = ('getGuiImplConfig',)

def getGuiImplConfig(manager):
    from gui.impl.gui_loader import GuiLoader
    from gui.impl.pub.fullscreen_manager import FullscreenManager
    from gui.impl.pub.notification_window_controller import NotificationWindowController
    from gui.impl.gen.view_models.common.tutorial.tutorial_model import TutorialModel
    from gui.impl.gen.view_models.common.ui_logger_model import UiLoggerModel
    loader = GuiLoader()
    loader.init(TutorialModel(), UiLoggerModel())
    manager.addInstance(IGuiLoader, loader, finalizer='fini')
    notifications = NotificationWindowController()
    tracker = manager.getService(IGameStateTracker)
    tracker.addController(notifications)
    notifications.init()
    manager.addInstance(INotificationWindowController, notifications, finalizer='fini')
    windowLoader = WindowLoaderController()
    tracker.addController(windowLoader)
    windowLoader.init()
    manager.addInstance(WindowLoaderController, windowLoader, finalizer='fini')
    fullscreen = FullscreenManager()
    fullscreen.init()
    manager.addInstance(IFullscreenManager, fullscreen, finalizer='fini')

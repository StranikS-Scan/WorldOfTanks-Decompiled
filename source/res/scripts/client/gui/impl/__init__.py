# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/__init__.py
__all__ = ('getGuiImplConfig',)

def getGuiImplConfig(manager):
    from gui.impl.gui_loader import GuiLoader
    from gui.impl.pub.lobby_overlay_mgr import LobbyOverlaysManager
    from skeletons.gui.impl import IGuiLoader, IOverlaysManager
    loader = GuiLoader()
    loader.init()
    manager.addInstance(IGuiLoader, loader, finalizer='fini')
    overlays = LobbyOverlaysManager()
    overlays.init()
    manager.addInstance(IOverlaysManager, overlays, finalizer='fini')

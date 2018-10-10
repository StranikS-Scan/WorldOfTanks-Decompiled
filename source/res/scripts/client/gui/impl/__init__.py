# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/__init__.py
__all__ = ('getGuiImplConfig',)

def getGuiImplConfig(manager):
    from gui.impl.gui_loader import GuiLoader
    from skeletons.gui.impl import IGuiLoader
    loader = GuiLoader()
    loader.init()
    manager.addInstance(IGuiLoader, loader, finalizer='fini')

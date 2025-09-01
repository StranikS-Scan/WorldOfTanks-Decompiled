# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/shared/hide_tooltips.py
from frameworks.wulf import WindowFlags
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader

@dependency.replace_none_kwargs(appLoader=IAppLoader, guiLoader=IGuiLoader)
def hideTooltips(appLoader=None, guiLoader=None):
    appLoader.getApp().getToolTipMgr().hide()

    def predicate(window):
        return window.windowFlags & WindowFlags.WINDOW_TYPE_MASK == WindowFlags.TOOLTIP

    windows = guiLoader.windowsManager.findWindows(predicate)
    for window in windows:
        window.destroy()

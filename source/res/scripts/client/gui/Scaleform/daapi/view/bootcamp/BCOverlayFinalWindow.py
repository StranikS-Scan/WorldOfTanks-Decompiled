# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCOverlayFinalWindow.py
from gui.Scaleform.daapi.view.meta.BCOverlayFinalWindowMeta import BCOverlayFinalWindowMeta
import BigWorld

class BCOverlayFinalWindow(BCOverlayFinalWindowMeta):

    def __init__(self, settings):
        super(BCOverlayFinalWindow, self).__init__()

    def _populate(self):
        super(BCOverlayFinalWindow, self)._populate()
        from gui.app_loader.settings import APP_NAME_SPACE
        from gui.app_loader import g_appLoader
        g_appLoader.detachCursor(APP_NAME_SPACE.SF_BATTLE)
        from bootcamp.Bootcamp import g_bootcamp
        resultType, _, resultTypeStr, _, _ = g_bootcamp.getBattleResults()
        from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
        LOG_DEBUG_DEV_BOOTCAMP('BCOverlayFinalWindow', resultType)
        self.as_msgTypeHandlerS(resultType, resultTypeStr)

    def _dispose(self):
        super(BCOverlayFinalWindow, self)._dispose()

    def animFinish(self):
        BigWorld.player().showBattleResults()

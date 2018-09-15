# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCOverlayFinalWindow.py
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform.daapi.view.meta.BCOverlayFinalWindowMeta import BCOverlayFinalWindowMeta
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui.app_loader.settings import APP_NAME_SPACE
from gui.app_loader import g_appLoader
from bootcamp.Bootcamp import g_bootcamp

class BCOverlayFinalWindow(BCOverlayFinalWindowMeta):

    def __init__(self, settings):
        super(BCOverlayFinalWindow, self).__init__()

    def animFinish(self):
        g_bootcampEvents.onBattleFinishAnimationComplete()

    def _populate(self):
        super(BCOverlayFinalWindow, self)._populate()
        g_appLoader.detachCursor(APP_NAME_SPACE.SF_BATTLE)
        battleResults = g_bootcamp.getBattleResults()
        LOG_DEBUG_DEV_BOOTCAMP('BCOverlayFinalWindow', battleResults.type)
        self.as_msgTypeHandlerS(battleResults.type, battleResults.typeStr)

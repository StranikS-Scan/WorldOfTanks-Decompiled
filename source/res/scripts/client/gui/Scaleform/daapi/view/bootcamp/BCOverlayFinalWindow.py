# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCOverlayFinalWindow.py
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform.daapi.view.meta.BCOverlayFinalWindowMeta import BCOverlayFinalWindowMeta
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui.app_loader import settings as app_settings
from bootcamp.Bootcamp import g_bootcamp
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

class BCOverlayFinalWindow(BCOverlayFinalWindowMeta):
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings):
        super(BCOverlayFinalWindow, self).__init__()

    def animFinish(self):
        g_bootcampEvents.onBattleFinishAnimationComplete()

    def _populate(self):
        super(BCOverlayFinalWindow, self)._populate()
        self.appLoader.detachCursor(app_settings.APP_NAME_SPACE.SF_BATTLE)
        battleResults = g_bootcamp.getBattleResults()
        LOG_DEBUG_DEV_BOOTCAMP('BCOverlayFinalWindow', battleResults.type)
        self.as_msgTypeHandlerS(battleResults.type, battleResults.typeStr)

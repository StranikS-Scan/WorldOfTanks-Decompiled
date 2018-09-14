# Embedded file name: scripts/client/gui/Scaleform/GameLoading.py
import GUI
import BigWorld
import constants
from debug_utils import LOG_DEBUG
from gui.Scaleform.Flash import Flash
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils import graphics
from helpers import getFullClientVersion, getClientOverride

class GameLoading(Flash):

    def __init__(self, component = None):
        Flash.__init__(self, 'gameLoading.swf', path=SCALEFORM_SWF_PATH_V3)
        self._displayRoot = self.getMember('root.main')
        if self._displayRoot is not None:
            self._displayRoot.resync()
            self._displayRoot.setLocale(getClientOverride())
            self._displayRoot.setVersion(getFullClientVersion())
            if constants.IS_KOREA:
                self._displayRoot.setInfo(MENU.LOADING_GAMEINFO)
            width, height = GUI.screenResolution()
            scaleLength = len(graphics.getInterfaceScalesList(BigWorld.wg_getCurrentResolution(True)))
            self._displayRoot.updateStage(width, height, scaleLength - 1)
        return

    def onLoad(self, dataSection):
        self.active(True)

    def onDelete(self):
        if self._displayRoot is not None:
            self._displayRoot.cleanup()
            self._displayRoot = None
        return

    def setProgress(self, value):
        self._displayRoot.setProgress(value)

    def addMessage(self, message):
        LOG_DEBUG(message)

    def reset(self):
        self._displayRoot.setProgress(0)

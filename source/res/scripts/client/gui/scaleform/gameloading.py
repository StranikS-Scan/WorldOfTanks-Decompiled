# Embedded file name: scripts/client/gui/Scaleform/GameLoading.py
import GUI
from debug_utils import LOG_DEBUG
from gui.Scaleform.Flash import Flash
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from helpers import getClientVersion, getClientOverride

class GameLoading(Flash):

    def __init__(self, component = None):
        Flash.__init__(self, 'gameLoading.swf', path=SCALEFORM_SWF_PATH_V3)
        self._displayRoot = self.getMember('root.main')
        if self._displayRoot is not None:
            self._displayRoot.resync()
            self._displayRoot.setLocale(getClientOverride())
            self._displayRoot.setVersion(getClientVersion())
            width, height = GUI.screenResolution()
            self._displayRoot.updateStage(width, height)
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

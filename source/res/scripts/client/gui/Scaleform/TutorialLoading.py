# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/TutorialLoading.py
import GUI
from gui import g_guiResetters
from gui.Scaleform.Flash import Flash
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.shared.utils import graphics

class LessonResultScreen(Flash):

    def __init__(self, isVictory):
        Flash.__init__(self, 'Victory.swf' if isVictory else 'tutorialDefeat.swf', path=SCALEFORM_SWF_PATH_V3)
        self._displayRoot = self.getMember('root.main')
        if self._displayRoot is not None:
            self._displayRoot.resync()
        return

    def onLoad(self, dataSection):
        self.active(True)

    def onDelete(self):
        if self._displayRoot is not None:
            self._displayRoot.cleanup()
            self._displayRoot = None
        return


class TutorialGarage(Flash):
    GARAGE_SWF_NAMES = ['hangar_hangar01.swf',
     'hangar_hangar02.swf',
     'hangar_hangar03.swf',
     'hangar_hangar04.swf',
     'hangar_hangar05.swf',
     'hangar_hangar06.swf']

    def __init__(self, garageNum):
        Flash.__init__(self, TutorialGarage.GARAGE_SWF_NAMES[garageNum], path=SCALEFORM_SWF_PATH_V3)

    def onLoad(self, dataSection):
        self.active(True)


class TutorialLoading(Flash):

    def __init__(self, finishCallback=None):
        Flash.__init__(self, 'tutorialLoadingPicture.swf', path=SCALEFORM_SWF_PATH_V3)
        self._displayRoot = self.getMember('root.main')
        self.__finishCallback = finishCallback
        if self._displayRoot is not None:
            self._displayRoot.resync()
            g_guiResetters.add(self.onUpdateStage)
            self.onUpdateStage()
        return

    def onUpdateStage(self):
        width, height = GUI.screenResolution()
        scaleLength = len(graphics.getInterfaceScalesList([width, height]))
        self._displayRoot.updateStage(width, height, scaleLength - 1)

    def onLoad(self, dataSection):
        self.active(True)
        if self.__finishCallback is not None:
            self.__finishCallback()
        return

    def onDelete(self):
        if self._displayRoot is not None:
            self._displayRoot.cleanup()
            self._displayRoot = None
        return


class FlashOverlay(Flash):

    def __init__(self, swfFile, finishCallback=None):
        Flash.__init__(self, swfFile, path=SCALEFORM_SWF_PATH_V3)
        self._displayRoot = self.getMember('root.main')
        self.__finishCallback = finishCallback
        if self._displayRoot is not None:
            self._displayRoot.resync()
            g_guiResetters.add(self.onUpdateStage)
            self.onUpdateStage()
        return

    def onUpdateStage(self):
        width, height = GUI.screenResolution()
        scaleLength = len(graphics.getInterfaceScalesList([width, height]))
        self._displayRoot.updateStage(width, height, scaleLength - 1)

    def onLoad(self, dataSection):
        self.active(True)
        if self.__finishCallback is not None:
            self.__finishCallback()
        return

    def onDelete(self):
        if self._displayRoot is not None:
            self._displayRoot.cleanup()
            self._displayRoot = None
        return

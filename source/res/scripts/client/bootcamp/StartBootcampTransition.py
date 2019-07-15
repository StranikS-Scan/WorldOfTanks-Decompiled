# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/StartBootcampTransition.py
import GUI
from gui import g_guiResetters
from gui.Scaleform.genConsts.ROOT_SWF_CONSTANTS import ROOT_SWF_CONSTANTS
from gui.Scaleform.daapi.view.meta.StartBootcampTransitionMeta import StartBootcampTransitionMeta
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.impl import backport
from gui.impl.gen import R

class StartBootcampTransition(ExternalFlashComponent, StartBootcampTransitionMeta):

    def __init__(self, name):
        super(StartBootcampTransition, self).__init__(ExternalFlashSettings('transitionFlash', name, 'root.main', ROOT_SWF_CONSTANTS.BOOTCAMP_TRANISITION_CALLBACK))
        self.createExternalComponent()
        self.movie.scaleMode = 'NoScale'
        self.movie.backgroundAlpha = 0.6

    def _populate(self):
        super(StartBootcampTransition, self)._populate()
        self.__onUpdateStage()
        g_guiResetters.add(self.__onUpdateStage)
        self.as_setTransitionTextS(backport.msgid(R.strings.waiting.loadHangarSpace()))

    def _dispose(self):
        g_guiResetters.discard(self.__onUpdateStage)
        super(StartBootcampTransition, self)._dispose()

    def __onUpdateStage(self):
        width, height = GUI.screenResolution()
        self.as_updateStageS(width, height)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BattleResultTransition.py
import GUI
from gui import g_guiResetters
from gui.Scaleform.daapi.view.meta.BCBattleResultTransitionMeta import BCBattleResultTransitionMeta
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from Bootcamp import g_bootcamp

class BattleResultTransition(ExternalFlashComponent, BCBattleResultTransitionMeta):

    def __init__(self):
        super(BattleResultTransition, self).__init__(ExternalFlashSettings('transitionFlash', 'bootcampBattleResultTransitionsApp.swf', 'root.main', ''))
        self.createExternalComponent()
        self.movie.scaleMode = 'NoScale'

    def _populate(self):
        super(BattleResultTransition, self)._populate()
        self.__onUpdateStage()
        g_guiResetters.add(self.__onUpdateStage)
        resultTypeStr = g_bootcamp.getBattleResults().typeStr
        self.as_msgTypeHandlerS(resultTypeStr)

    def _dispose(self):
        g_guiResetters.discard(self.__onUpdateStage)
        super(BattleResultTransition, self)._dispose()

    def __onUpdateStage(self):
        width, height = GUI.screenResolution()
        self.as_updateStageS(width, height)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/game_loading.py
import GUI
from debug_utils import LOG_DEBUG
from gui import g_guiResetters
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.meta.GameLoadingMeta import GameLoadingMeta
from gui.Scaleform.genConsts.ROOT_SWF_CONSTANTS import ROOT_SWF_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils import graphics
from helpers import getFullClientVersion, getClientOverride, getClientLanguage
from helpers import uniprof

class GameLoading(ExternalFlashComponent, GameLoadingMeta):

    def __init__(self, _):
        super(GameLoading, self).__init__(ExternalFlashSettings('gameLoading', 'gameLoadingApp.swf', 'root.main', ROOT_SWF_CONSTANTS.GAME_LOADING_REGISTER_CALLBACK))

    @uniprof.regionDecorator(label='offline.game_loading', scope='enter')
    def afterCreate(self):
        super(GameLoading, self).afterCreate()
        self.as_setLocaleS(getClientOverride())
        self.as_setVersionS(getFullClientVersion())
        if getClientLanguage() == 'ko':
            self.as_setInfoS(MENU.LOADING_GAMEINFO)
        self._updateStage()

    def onUpdateStage(self):
        self._updateStage()

    def onLoad(self, dataSection):
        g_guiResetters.add(self.onUpdateStage)
        self.active(True)

    @uniprof.regionDecorator(label='offline.game_loading', scope='exit')
    def onDelete(self):
        g_guiResetters.discard(self.onUpdateStage)
        self.close()

    def setProgress(self, value):
        self.as_setProgressS(value)

    def addMessage(self, message):
        LOG_DEBUG(message)

    def reset(self):
        self.as_setProgressS(0)

    def _updateStage(self):
        width, height = GUI.screenResolution()
        scaleLength = len(graphics.getInterfaceScalesList([width, height]))
        self.as_updateStageS(width, height, scaleLength - 1)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/game_loading.py
import logging
import GUI
from gui import g_guiResetters
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.meta.GameLoadingMeta import GameLoadingMeta
from gui.Scaleform.genConsts.ROOT_SWF_CONSTANTS import ROOT_SWF_CONSTANTS
from gui.shared.utils import graphics
from helpers import getFullClientVersion, getClientOverride, getClientLanguage
from helpers import uniprof
from gui.impl import backport
from gui.impl.gen import R
from gui import makeHtmlString
_logger = logging.getLogger(__name__)

class GameLoading(ExternalFlashComponent, GameLoadingMeta):

    def __init__(self, _):
        super(GameLoading, self).__init__(ExternalFlashSettings('gameLoading', 'gameLoadingApp.swf', 'root.main', ROOT_SWF_CONSTANTS.GAME_LOADING_REGISTER_CALLBACK))
        self.createExternalComponent()

    @uniprof.regionDecorator(label='offline.game_loading', scope='enter')
    def afterCreate(self):
        super(GameLoading, self).afterCreate()
        self.as_setLocaleS(getClientOverride())
        self.as_setVersionS(getFullClientVersion())
        if getClientLanguage() == 'ko':
            self.as_setInfoS(backport.text(R.strings.menu.loading.gameInfo(), age=makeHtmlString('html_templates:loading', 'game-info-age')))
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
        _logger.info(message)

    def reset(self):
        self.as_setProgressS(0)

    def _updateStage(self):
        width, height = GUI.screenResolution()
        scaleLength = len(graphics.getInterfaceScalesList([width, height]))
        self.as_updateStageS(width, height, scaleLength - 1)

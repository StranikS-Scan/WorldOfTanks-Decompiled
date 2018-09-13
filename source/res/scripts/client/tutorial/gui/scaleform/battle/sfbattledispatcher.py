# Embedded file name: scripts/client/tutorial/gui/Scaleform/battle/SfBattleDispatcher.py
from gui.Scaleform.windows import UIInterface
from tutorial import LOG_MEMORY, LOG_ERROR
from tutorial.data.chapter import SimpleEffect, Effect
from tutorial.gui import GUIDispatcher

class SfBattleDispatcher(GUIDispatcher, UIInterface):

    def __init__(self, config):
        super(SfBattleDispatcher, self).__init__()
        self.__layout = None
        self.__config = config
        return

    def __del__(self):
        LOG_MEMORY('SfBattleDispatcher deleted')

    def start(self, ctx):
        pass

    def stop(self):
        self.clearGUI()

    def findGUI(self, root = None):
        gfxObj = getattr(root, 'dispatcher', None)
        if gfxObj is not None:
            self.__layout = root
        else:
            LOG_ERROR('GFx object of dispatcher not found')
        return

    def clearGUI(self):
        self.__layout = None
        return

    def populateUI(self, proxy):
        super(SfBattleDispatcher, self).populateUI(proxy)
        self.uiHolder.addFsCallbacks({'Tutorial.Dispatcher.Refuse': self.__gfx_onRefuseTraining})

    def dispossessUI(self):
        self.uiHolder.removeFsCallbacks('Tutorial.Dispatcher.Refuse')
        super(SfBattleDispatcher, self).dispossessUI()

    def setChapterInfo(self, title, description):
        if self.__layout is not None:
            self.__layout.dispatcher.setChapterInfo(title, description)
        return

    def clearChapterInfo(self):
        if self.__layout is not None:
            self.__layout.dispatcher.clearChapterInfo()
        return

    def __gfx_onRefuseTraining(self, _):
        if self._mode == GUIDispatcher.RUN_MODE:
            from tutorial.loader import g_loader
            funcEffect = g_loader.tutorial._ctrlFactory.createFuncEffect(SimpleEffect(Effect.REFUSE_TRAINING))
            funcEffect.triggerEffect()
        else:
            LOG_ERROR('TUTORIAL. Tutorial is not run.', self._mode)

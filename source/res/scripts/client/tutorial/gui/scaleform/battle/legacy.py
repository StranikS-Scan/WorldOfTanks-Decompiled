# Embedded file name: scripts/client/tutorial/gui/Scaleform/battle/legacy.py
import weakref
import GUI
from gui.Scaleform.windows import UIInterface
from gui.app_loader import g_appLoader
from tutorial.data.events import ClickEvent
from tutorial.doc_loader import gui_config
from tutorial.gui import GUIProxy
from tutorial.gui.commands import GUICommand, GUICommandsFactory
from tutorial.logger import LOG_ERROR, LOG_DEBUG, LOG_CURRENT_EXCEPTION

class TutorialUILoader(object):

    def __init__(self, handler, swf):
        super(TutorialUILoader, self).__init__()
        self._loader = None
        self._handler = handler
        self._swf = swf
        return

    def __del__(self):
        LOG_DEBUG('TutorialUILoader deleted')

    def init(self, ui):
        loader = ui.getMember('tutorialLoader')
        if loader is None:
            LOG_ERROR('Tutorial loader not found')
            return
        else:
            self._loader = loader
            self._loader.script = self
            return

    def fini(self):
        if self._loader is not None:
            self._loader.script = None
        self._loader = None
        self._handler = None
        return

    def load(self):
        if self._loader is None:
            return False
        else:
            result = True
            try:
                self._loader.loadTutorial(self._swf)
                LOG_DEBUG('UILoader.load:', self._swf)
            except AttributeError:
                result = False

            return result

    def unload(self, isItemsRevert = True):
        if self._loader is None:
            return False
        else:
            result = True
            try:
                self._loader.unloadTutorial(isItemsRevert)
                LOG_DEBUG('UILoader.unload:', self._swf)
            except AttributeError:
                result = False

            return result

    def gc_onLoadComplete(self, movieView):
        LOG_DEBUG('gc_onLoadComplete', movieView)
        self._handler._setMovieView(movieView)

    def gc_getScreenSize(self):
        LOG_DEBUG('gc_getScreenSize')
        return GUI.screenResolution()


class ScaleformCommand(GUICommand):

    def invoke(self, gui, cmdData):
        gui.call(cmdData.name, cmdData.args[:])


class ScaleformCommandsFactory(GUICommandsFactory):

    def __init__(self):
        super(ScaleformCommandsFactory, self).__init__({'flash-call': ScaleformCommand})


class ScaleformLayout(GUIProxy, UIInterface):

    def __init__(self, swf):
        super(ScaleformLayout, self).__init__()
        self.config = None
        self.loader = TutorialUILoader(weakref.proxy(self), swf)
        self._guiRef = None
        self._movieView = None
        self._commands = ScaleformCommandsFactory()
        return

    def _resolveGuiRoot(self):
        proxy = None
        try:
            app = g_appLoader.getDefBattleApp()
            if not app:
                return
            self._guiRef = weakref.ref(app)
            proxy = weakref.proxy(app)
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

        return proxy

    def populateUI(self, proxy):
        super(ScaleformLayout, self).populateUI(proxy)
        self.loader.init(proxy)

    def dispossessUI(self):
        self.loader.fini()
        super(ScaleformLayout, self).dispossessUI()

    def init(self):
        proxy = self._resolveGuiRoot()
        result = False
        if proxy is not None:
            self.populateUI(proxy)
            if self.loader.load():
                result = True
        return result

    def _setMovieView(self, movie):
        if self._movieView is not None:
            self._movieView.script = None
        self._movieView = movie
        self._movieView.resync()
        self._movieView.script = self
        self.onGUILoaded()
        return

    def fini(self, isItemsRevert = True):
        self.eManager.clear()
        if self._guiRef is None or self._guiRef() is None:
            return
        else:
            self.loader.unload(isItemsRevert=isItemsRevert)
            if self._movieView is not None:
                self._movieView.script = None
                self._movieView = None
            self.dispossessUI()
            return

    def loadConfig(self, filePath):
        self.config = gui_config.readConfig(filePath)

    def reloadConfig(self, filePath):
        self.config = gui_config.readConfig(filePath, forced=True)

    def playEffect(self, effectName, args, itemRef = None, containerRef = None):
        if itemRef is not None:
            item = self.config.getItem(itemRef)
            if item is None:
                LOG_ERROR('GUI Item not found', effectName, itemRef)
                return
            if args is None:
                args = []
            args.append(item.path)
        if containerRef is not None:
            container = self.config.getItem(containerRef)
            if container is None:
                LOG_ERROR('GUI Item not found', effectName, containerRef)
                return
            if args is None:
                args = []
            args.append(container.path)
        return self._movieView.effects.play(effectName, args)

    def stopEffect(self, effectName, effectID):
        self._movieView.effects.stop(effectName, effectID)

    def setItemProps(self, itemRef, props, revert = False):
        item = self.config.getItem(itemRef)
        if item is None:
            LOG_ERROR('GUI Item not found', itemRef)
            return
        else:
            self._movieView.items.setProps(itemRef, item.path, props, revert)
            return

    def isGuiDialogDisplayed(self):
        return self._movieView.isGuiDialogOnStage()

    def isTutorialDialogDisplayed(self, dialogID):
        return self._movieView.isTutorialDialogOnStage(dialogID)

    def isTutorialWindowDisplayed(self, windowID):
        return self._movieView.isTutorialWindowOnStage(windowID)

    def invokeCommand(self, data):
        self._commands.invoke(self.uiHolder, data)

    def getGuiRoot(self):
        try:
            root = g_appLoader.getApp()
        except AttributeError:
            LOG_CURRENT_EXCEPTION()
            root = None

        return root

    def setChapterInfo(self, title, description):
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.setChapterInfo(title, description)
        else:
            LOG_ERROR('Tutorial dispatcher is not defined.')
        return

    def clearChapterInfo(self):
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.clearChapterInfo()
        else:
            LOG_ERROR('Tutorial dispatcher is not defined.')
        return

    def gc_proxyMouseClick(self, targetID):
        self.onGUIInput(ClickEvent(targetID))

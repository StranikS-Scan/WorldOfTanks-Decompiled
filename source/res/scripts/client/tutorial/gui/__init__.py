# Embedded file name: scripts/client/tutorial/gui/__init__.py
from ConnectionManager import connectionManager
import Event
from debug_utils import LOG_ERROR

class GUIEvent(object):

    def __init__(self, guiType, targetID):
        super(GUIEvent, self).__init__()
        self.type = guiType
        self.targetID = targetID


class GUI_EFFECT_NAME:
    SHOW_DIALOG = 'ShowDialog'
    SHOW_WINDOW = 'ShowWindow'
    UPDATE_CONTENT = 'UpdateContent'


class GUIProxy(object):
    eManager = Event.EventManager()
    onGUILoaded = Event.Event(eManager)
    onMouseClicked = Event.Event(eManager)
    onPageChanging = Event.Event(eManager)

    def init(self):
        pass

    def show(self):
        pass

    def fini(self, isItemsRevert = True):
        pass

    def clear(self):
        pass

    def lock(self):
        pass

    def release(self):
        pass

    def loadConfig(self, filePath):
        pass

    def reloadConfig(self, filePath):
        pass

    def getSceneID(self):
        pass

    def goToScene(self, sceneID):
        pass

    def playEffect(self, effectName, args, itemRef = None, containerRef = None):
        return False

    def stopEffect(self, effectName, effectID):
        pass

    def showWaiting(self, messageID, isSingle = False):
        pass

    def hideWaiting(self, messageID = None):
        pass

    def showMessage(self, text, lookupType = None):
        pass

    def showI18nMessage(self, key, *args, **kwargs):
        pass

    def showServiceMessage(self, data, msgTypeName):
        return 0

    def setItemProps(self, itemRef, props, revert = False):
        pass

    def isGuiDialogDisplayed(self):
        return False

    def isTutorialDialogDisplayed(self, dialogID):
        return False

    def isTutorialWindowDisplayed(self, windowID):
        return False

    def findItem(self, itemID, criteria):
        pass

    def invokeCommand(self, command):
        pass

    def getGuiRoot(self):
        return None

    @classmethod
    def windowsManager(cls):
        from gui import WindowsManager
        return WindowsManager.g_windowsManager

    @classmethod
    def setDispatcher(cls, dispatcher):
        pass

    @classmethod
    def getDispatcher(cls):
        return None

    def setChapterInfo(self, title, description):
        pass

    def clearChapterInfo(self):
        pass

    def setPlayerXPLevel(self, level):
        pass

    def setTrainingPeriod(self, currentIdx, total):
        pass

    def setTrainingProgress(self, mask):
        pass

    def setChapterProgress(self, total, mask):
        pass

    def setTrainingRestartMode(self):
        pass

    def setTrainingRunMode(self):
        pass


class GUIDispatcher(object):
    DEFAULT_MODE = 0
    RUN_MODE = 1
    RESTART_MODE = 2

    def __init__(self):
        super(GUIDispatcher, self).__init__()
        self._mode = GUIDispatcher.DEFAULT_MODE
        self._isDisabled = False

    def start(self, ctx):
        pass

    def stop(self):
        pass

    def findGUI(self, root = None):
        return False

    def clearGUI(self):
        pass

    def refuseTraining(self):
        result = True
        if self._mode == GUIDispatcher.RUN_MODE:
            from tutorial.loader import g_loader
            g_loader.refuse()
        else:
            result = False
            LOG_ERROR('TUTORIAL. Tutorial is not run.', self._mode)
        return result

    def restartTraining(self, reloadIfRun = False, afterBattle = False):
        result = False
        if self._mode == GUIDispatcher.RESTART_MODE:
            if self._isDisabled:
                LOG_ERROR('Tutorial is not enabled')
            else:
                from tutorial.loader import g_loader
                result = True
                g_loader.restart(afterBattle=afterBattle)
        elif reloadIfRun:
            from tutorial.loader import g_loader
            result = g_loader.reload(afterBattle=afterBattle)
        else:
            LOG_ERROR('TUTORIAL. Tutorial is not stopped.', self._mode)
        return result

    def setPlayerXPLevel(self, level):
        pass

    def setChapterInfo(self, title, description):
        pass

    def clearChapterInfo(self):
        pass

    def setDisabled(self, disabled):
        self._isDisabled = disabled

    def setTrainingRestartMode(self):
        self._mode = GUIDispatcher.RESTART_MODE

    def setTrainingRunMode(self):
        self._mode = GUIDispatcher.RUN_MODE


class LobbyDispatcher(GUIDispatcher):

    def _subscribe(self):
        connectionManager.onDisconnected += self.__cm_onDisconnected

    def _unsubscribe(self):
        connectionManager.onDisconnected -= self.__cm_onDisconnected

    def __cm_onDisconnected(self):
        self.clearChapterInfo()

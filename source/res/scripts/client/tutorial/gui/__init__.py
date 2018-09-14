# Embedded file name: scripts/client/tutorial/gui/__init__.py
import Event
from debug_utils import LOG_ERROR

class GUI_EFFECT_NAME:
    SHOW_DIALOG = 'ShowDialog'
    SHOW_WINDOW = 'ShowWindow'
    SHOW_HINT = 'ShowHint'
    UPDATE_CONTENT = 'UpdateContent'
    SET_CRITERIA = 'SetCriteria'
    SET_TRIGGER = 'SetTrigger'


class GUIProxy(object):
    eManager = Event.EventManager()
    onGUILoaded = Event.Event(eManager)
    onGUIInput = Event.Event(eManager)
    onPageChanging = Event.Event(eManager)
    onItemFound = Event.Event(eManager)
    onItemLost = Event.Event(eManager)

    def init(self):
        return True

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

    def isEffectRunning(self, effectName, effectID = None):
        return False

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

    def getItemsOnScene(self):
        return set()

    def setItemProps(self, itemRef, props, revert = False):
        pass

    def closePopUps(self):
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

    def setDispatcher(self, dispatcher):
        pass

    def getDispatcher(self):
        return None

    def setChapterInfo(self, title, description):
        pass

    def clearChapterInfo(self):
        pass

    def setTrainingPeriod(self, currentIdx, total):
        pass

    def setTrainingProgress(self, mask):
        pass

    def setChapterProgress(self, total, mask):
        pass


class GUIDispatcher(object):

    def __init__(self):
        super(GUIDispatcher, self).__init__()
        self._loader = None
        self._isDisabled = False
        self._isStarted = False
        return

    def start(self, loader):
        if self._isStarted:
            return False
        self._isStarted = True
        self._loader = loader
        return True

    def stop(self):
        if not self._isStarted:
            return False
        else:
            self.clearGUI()
            self._loader = None
            return True

    def findGUI(self, root = None):
        return False

    def clearGUI(self):
        pass

    def stopTraining(self):
        result = False
        if self._loader:
            result = self._loader.stop()
        else:
            LOG_ERROR('Tutorial can not be stopped, loader is not defined')
        return result

    def startTraining(self, settingsID, state):
        result = False
        if self._loader:
            result = self._loader.run(settingsID, state)
        else:
            LOG_ERROR('Tutorial can not be run, loader is not defined')
        return result

    def setChapterInfo(self, title, description):
        pass

    def clearChapterInfo(self):
        pass

    def setDisabled(self, disabled):
        self._isDisabled = disabled

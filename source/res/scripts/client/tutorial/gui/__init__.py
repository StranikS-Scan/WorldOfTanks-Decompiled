# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/__init__.py
import typing
from enum import unique, IntEnum
import Event
from debug_utils import LOG_ERROR
if typing.TYPE_CHECKING:
    from skeletons.tutorial import ComponentID

class GUI_EFFECT_NAME(object):
    SHOW_DIALOG = 'ShowDialog'
    SHOW_WINDOW = 'ShowWindow'
    SHOW_HINT = 'ShowHint'
    SET_CRITERIA = 'SetCriteria'
    SET_VIEW_CRITERIA = 'SetViewCriteria'
    SET_TRIGGER = 'SetTrigger'
    SET_ITEM_PROPS = 'SetItemProps'
    PLAY_ANIMATION = 'PlayAnimation'


class GUIProxy(object):

    def __init__(self):
        super(GUIProxy, self).__init__()
        self.eManager = Event.EventManager()
        self.onGUILoaded = Event.Event(self.eManager)
        self.onGUIInput = Event.Event(self.eManager)
        self.onPageChanging = Event.Event(self.eManager)
        self.onPageReady = Event.Event(self.eManager)
        self.onItemFound = Event.Event(self.eManager)
        self.onItemLost = Event.Event(self.eManager)
        self.onViewLoaded = Event.Event(self.eManager)
        self.onViewDisposed = Event.Event(self.eManager)

    def init(self):
        return True

    def show(self):
        pass

    def fini(self):
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

    def isViewPresent(self, layer, criteria):
        return False

    def closeView(self, layer, criteria):
        pass

    def playEffect(self, effectName, args):
        return False

    def stopEffect(self, effectName, effectID, effectSubType=None):
        pass

    def isEffectRunning(self, effectName, effectID=None, effectSubType=None):
        return False

    def showWaiting(self, messageID, isSingle=False):
        pass

    def hideWaiting(self, messageID=None):
        pass

    def showMessage(self, text, lookupType=None):
        pass

    def showI18nMessage(self, key, *args, **kwargs):
        pass

    def showServiceMessage(self, data, msgTypeName):
        pass

    def getItemsOnScene(self):
        return set()

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

    def setDispatcher(self, dispatcher):
        pass

    def getDispatcher(self):
        return None


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

    def findGUI(self, root=None):
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

    def refuseTraining(self):
        result = False
        if self._loader:
            result = self._loader.refuse()
        else:
            LOG_ERROR('Tutorial can not be refuse, loader is not defined')
        return result

    def startTraining(self, settingsID, state):
        result = False
        if self._loader:
            result = self._loader.run(settingsID, state)
        else:
            LOG_ERROR('Tutorial can not be run, loader is not defined')
        return result

    def setDisabled(self, disabled):
        self._isDisabled = disabled


@unique
class GuiType(IntEnum):
    UNDEFINED = 0
    SCALEFORM = 1
    WULF = 2


ComponentDescr = typing.NamedTuple('ComponentDescr', (('ID', str),
 ('viewType', GuiType),
 ('viewId', str),
 ('path', str)))

class IGuiImpl(object):
    __slots__ = ('onComponentFound', 'onTriggerActivated', 'onComponentDisposed', 'onEffectCompleted', 'onInit')
    if typing.TYPE_CHECKING:
        onComponentFound = None
        onComponentDisposed = None
        onTriggerActivated = None
        onEffectCompleted = None
        onInit = None

    def clear(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def showEffect(self, componentID, viewID, effectType, effectData, effectBuilder=''):
        raise NotImplementedError

    def hideEffect(self, componentID, viewID, effectType, effectBuilder=''):
        raise NotImplementedError

    def setDescriptions(self, items):
        raise NotImplementedError

    def setSystemEnabled(self, enabled):
        raise NotImplementedError

    def setCriteria(self, name, value):
        raise NotImplementedError

    def setViewCriteria(self, componentID, viewUniqueName):
        raise NotImplementedError

    def setTriggers(self, componentID, triggers):
        raise NotImplementedError

    def supportedViewTypes(self):
        raise NotImplementedError

    def isInited(self):
        raise NotImplementedError

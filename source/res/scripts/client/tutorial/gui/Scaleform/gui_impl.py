# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/gui_impl.py
import typing
from collections import defaultdict
from Event import Event, EventManager
from gui.Scaleform.framework.managers.TutorialManager import ScaleformTutorialManager
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from tutorial.gui import GuiType, IGuiImpl
if typing.TYPE_CHECKING:
    from skeletons.tutorial import ComponentID
    from tutorial.gui import ComponentDescr

class ScaleformGuiImpl(IGuiImpl):
    __slots__ = ('__proxy', '__eventMgr')
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(ScaleformGuiImpl, self).__init__()
        self.__proxy = None
        self.__eventMgr = EventManager()
        self.onComponentFound = Event(self.__eventMgr)
        self.onComponentDisposed = Event(self.__eventMgr)
        self.onTriggerActivated = Event(self.__eventMgr)
        self.onEffectCompleted = Event(self.__eventMgr)
        self.onInit = Event(self.__eventMgr)
        self.__appLoader.onGUISpaceBeforeEnter += self.__onBeforeEnterSpace
        return

    def fini(self):
        self.__appLoader.onGUISpaceBeforeEnter -= self.__onBeforeEnterSpace
        self.__appLoader.onGUIInitialized -= self.__setProxy
        self.clear()
        self.__eventMgr.clear()

    def clear(self):
        if self.__proxy is not None:
            self.__proxy.onCreated -= self.__onProxyCreated
            self.__proxy.onComponentFoundEvent -= self.__onComponentFound
            self.__proxy.onComponentDisposedEvent -= self.__onComponentDisposed
            self.__proxy.onEffectCompletedEvent -= self.__onEffectCompleted
            self.__proxy.onTriggerActivatedEvent -= self.__onTriggerActivated
            self.__proxy = None
        return

    def showEffect(self, componentID, viewID, effectType, effectData, effectBuilder=''):
        self.__proxy.as_showEffectS(viewID, componentID, effectType, {'data': effectData,
         'builder': effectBuilder})

    def hideEffect(self, componentID, viewID, effectType, effectBuilder=''):
        self.__proxy.as_hideEffectS(viewID, componentID, effectType, effectBuilder)

    def setDescriptions(self, descriptions):
        descrs = defaultdict(list)
        for descr in descriptions:
            descrs[descr.viewId].append({'id': descr.ID,
             'viewName': descr.viewId,
             'path': descr.path})

        self.__proxy.as_setDescriptionsS(descrs)

    def setSystemEnabled(self, enabled):
        self.__proxy.as_setSystemEnabledS(enabled)

    def setCriteria(self, name, value):
        self.__proxy.as_setCriteriaS(name, value)

    def setViewCriteria(self, componentID, viewUniqueName):
        self.__proxy.as_setComponentViewCriteriaS(componentID, viewUniqueName)

    def setTriggers(self, componentID, triggers):
        self.__proxy.as_setTriggersS(componentID, triggers)

    def supportedViewTypes(self):
        return (GuiType.SCALEFORM, GuiType.WULF)

    def isInited(self):
        return self.__proxy is not None and self.__proxy.isCreated()

    def __onBeforeEnterSpace(self, spaceID):
        if spaceID in (GuiGlobalSpaceID.LOBBY, GuiGlobalSpaceID.BATTLE):
            self.__setProxy()

    def __setProxy(self):
        self.clear()
        self.__proxy = self.__appLoader.getApp().tutorialManager
        if self.__proxy is None:
            self.__appLoader.onGUIInitialized += self.__setProxy
            return
        else:
            self.__proxy.onCreated += self.__onProxyCreated
            self.__proxy.onComponentFoundEvent += self.__onComponentFound
            self.__proxy.onComponentDisposedEvent += self.__onComponentDisposed
            self.__proxy.onEffectCompletedEvent += self.__onEffectCompleted
            self.__proxy.onTriggerActivatedEvent += self.__onTriggerActivated
            self.__appLoader.onGUIInitialized -= self.__setProxy
            return

    def __onComponentFound(self, componentId, viewTutorialId):
        self.onComponentFound(componentId, viewTutorialId)

    def __onTriggerActivated(self, componentId, triggerId, state):
        self.onTriggerActivated(componentId, triggerId, state)

    def __onComponentDisposed(self, componentId):
        self.onComponentDisposed(componentId)

    def __onEffectCompleted(self, componentId, effectType):
        self.onEffectCompleted(componentId, effectType)

    def __onProxyCreated(self):
        self.onInit()

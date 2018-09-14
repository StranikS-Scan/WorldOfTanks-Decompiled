# Embedded file name: scripts/client/gui/Scaleform/framework/managers/TutorialManager.py
from collections import defaultdict
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.framework.entities.abstract.TutorialManagerMeta import TutorialManagerMeta
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
try:
    from tutorial.doc_loader import gui_config
except ImportError:
    LOG_ERROR('Can not load package tutorial')

    class gui_config(object):

        @classmethod
        def readConfig(cls, path, forced = False):
            return None


_Event = events.TutorialEvent
_TRIGGER_TYPES = TUTORIAL_TRIGGER_TYPES
_CUSTOM_COMPONENTS = ('TankCarousel', 'PremiumButton', 'FreeXpButton', 'ResearchRootNode')

class TutorialManager(TutorialManagerMeta):

    def __init__(self, isEnabled = False, path = ''):
        super(TutorialManager, self).__init__()
        self._isEnabled = isEnabled
        self._aliases = {}
        self._components = set()
        if isEnabled:
            self._config = gui_config.readConfig(path)
        else:
            self._config = None
        return

    def getViewTutorialID(self, alias):
        if not self._isEnabled:
            return None
        elif alias in self._aliases.values():
            return alias
        else:
            return None
            return None

    def getFoundComponentsIDs(self):
        return self._components

    def setCriteria(self, name, value, noCached):
        self.as_setCriteriaS(name, value, noCached)

    def requestCriteriaValue(self, criteriaName):
        LOG_DEBUG('TutorialManager.requestCriteriaValue(criteriaName)', criteriaName)

    def setTriggers(self, componentID, triggers):
        if not self._validate(componentID):
            return
        self.as_setTriggersS(componentID, triggers)

    def clearTriggers(self, componentID):
        self.setTriggers(componentID, ())

    def showInteractiveHint(self, componentID, content, triggers = None):
        if not self._validate(componentID):
            return
        else:
            if 'padding' not in content:
                content['padding'] = self._config.getItem(componentID).padding
            isCustomCmp = True if componentID in _CUSTOM_COMPONENTS else False
            self.as_showHintS(self._aliases[componentID], componentID, content, isCustomCmp)
            if triggers is not None:
                self.as_setTriggersS(componentID, triggers)
            return

    def closeInteractiveHint(self, componentID):
        if not self._validate(componentID):
            return
        self.as_setTriggersS(componentID, ())
        self.as_hideHintS(self._aliases[componentID], componentID)

    def onComponentFound(self, componentID):
        self._components.add(componentID)
        self.fireEvent(_Event(_Event.ON_COMPONENT_FOUND, targetID=componentID), scope=EVENT_BUS_SCOPE.GLOBAL)

    def onComponentDisposed(self, componentID):
        self._components.discard(componentID)
        self.fireEvent(_Event(_Event.ON_COMPONENT_LOST, targetID=componentID), scope=EVENT_BUS_SCOPE.GLOBAL)

    def onTriggerActivated(self, componentID, triggerType):
        self.fireEvent(_Event(_Event.ON_TRIGGER_ACTIVATED, targetID=componentID, settingsID=triggerType), scope=EVENT_BUS_SCOPE.GLOBAL)

    def _populate(self):
        super(TutorialManager, self)._populate()
        self.as_setSystemEnabledS(self._isEnabled)
        if self._isEnabled and self._config:
            descriptions = defaultdict(list)
            for componentID, item in self._config.getItems():
                descriptions[item.view].append({'id': componentID,
                 'viewName': item.view,
                 'path': item.path})
                self._aliases[componentID] = item.view

            self.as_setDescriptionsS(descriptions)

    def _validate(self, componentID):
        if not self._isEnabled or self._config is None:
            return False
        elif not self._isCreated():
            raise AssertionError('TutorialManager must be initialised')
            component = self._config.getItem(componentID)
            component is None and LOG_DEBUG('Component is not found', componentID)
            return False
        else:
            return True

    def _dispose(self):
        self._isEnabled = False
        self._config = None
        self._aliases.clear()
        self._components.clear()
        super(TutorialManager, self)._dispose()
        return

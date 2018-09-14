# Embedded file name: scripts/client/tutorial/gui/Scaleform/hints/proxy.py
import Event
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from tutorial.data.events import ClickEvent
from tutorial.doc_loader.sub_parsers import ACTION_TAGS
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.gui.Scaleform import effects_player
from tutorial.gui.Scaleform.lobby.proxy import SfLobbyProxy

class HintsProxy(SfLobbyProxy):

    def __init__(self):
        effects = {GUI_EFFECT_NAME.SHOW_HINT: effects_player.ShowOnceOnlyHint(),
         GUI_EFFECT_NAME.SET_TRIGGER: effects_player.SetTriggerEffect()}
        super(HintsProxy, self).__init__(effects_player.EffectsPlayer(effects))
        self.__eManager = Event.EventManager()
        self.onHintClicked = Event.Event(self.__eManager)
        self.onHintItemFound = Event.Event(self.__eManager)
        self.onHintItemLost = Event.Event(self.__eManager)

    def init(self):
        addListener = g_eventBus.addListener
        addListener(events.TutorialEvent.ON_COMPONENT_FOUND, self.__onItemFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(events.TutorialEvent.ON_COMPONENT_LOST, self.__onItemLost, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(events.TutorialEvent.ON_TRIGGER_ACTIVATED, self.__onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)

    def fini(self, isItemsRevert = True):
        self.__eManager.clear()
        self.effects.stopAll()
        removeListener = g_eventBus.removeListener
        removeListener(events.TutorialEvent.ON_COMPONENT_FOUND, self.__onItemFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(events.TutorialEvent.ON_COMPONENT_LOST, self.__onItemLost, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(events.TutorialEvent.ON_TRIGGER_ACTIVATED, self.__onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)

    def showHint(self, props):
        self.playEffect(GUI_EFFECT_NAME.SHOW_HINT, (props, (ACTION_TAGS['click'],)))

    def hideHint(self, hintID):
        self.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, hintID)

    def __onItemFound(self, event):
        if event.targetID:
            self.onHintItemFound(event.targetID)

    def __onItemLost(self, event):
        if event.targetID:
            self.onHintItemLost(event.targetID)

    def __onTriggerActivated(self, event):
        if event.settingsID == TUTORIAL_TRIGGER_TYPES.CLICK_TYPE and event.targetID:
            self.onHintClicked(ClickEvent(event.targetID))

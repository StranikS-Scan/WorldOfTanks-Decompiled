# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/lobby/story_mode_event_entry_point_view.py
from story_mode.gui.impl.lobby.event_entry_point_view import EventEntryPointView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class StoryModeEventEntryPointView(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = EventEntryPointView()
        return self.__view

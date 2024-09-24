# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/lobby/story_mode_newbie_entry_point_view.py
from story_mode.gui.impl.lobby.newbie_entry_point_view import NewbieEntryPointView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class StoryModeNewbieEntryPointView(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = NewbieEntryPointView()
        return self.__view

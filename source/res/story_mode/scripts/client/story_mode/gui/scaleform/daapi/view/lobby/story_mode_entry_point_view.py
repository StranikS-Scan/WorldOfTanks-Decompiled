# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/lobby/story_mode_entry_point_view.py
from story_mode.gui.impl.lobby.entry_point_view import EntryPointView
from story_mode.gui.scaleform.daapi.view.meta.StoryModeEntryPointMeta import StoryModeEntryPointMeta

class StoryModeEntryPointView(StoryModeEntryPointMeta):

    def _makeInjectView(self):
        self.__view = EntryPointView()
        return self.__view

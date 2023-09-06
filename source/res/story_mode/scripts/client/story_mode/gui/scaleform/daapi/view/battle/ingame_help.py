# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/ingame_help.py
import typing
from gui.Scaleform.daapi.view.battle.shared.ingame_help import IngameHelpWindow
from story_mode.uilogging.story_mode.consts import LogWindows
from story_mode.uilogging.story_mode.loggers import WindowLogger

class StoryModeIngameHelpWindow(IngameHelpWindow):

    def __init__(self, ctx=None):
        super(StoryModeIngameHelpWindow, self).__init__(ctx)
        self._uiLogger = WindowLogger(LogWindows.HELP)

    def _populate(self):
        self._uiLogger.logOpen()
        super(StoryModeIngameHelpWindow, self)._populate()

    def _dispose(self):
        super(StoryModeIngameHelpWindow, self)._dispose()
        self._uiLogger.logClose()

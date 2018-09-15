# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/pve_goal_panel.py
import BigWorld
from gui.Scaleform.daapi.view.meta.PvEGoalPanelMeta import PvEGoalPanelMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from constants import LEVIATHAN_HALFWAY_PROGRESS, LEVIATHAN_PROGRESS_CLOSE
_HINT_KILL_LEVIATHAN = 0
_HINT_HALF_WAY = 1
_HINT_IS_CLOSE_TO_GATE = 2
_HINT_ENTERED_CAPTURE = 3
_TITLE = 0
_MESSAGE = 1

class PvEGoalPanel(PvEGoalPanelMeta):

    def __init__(self):
        super(PvEGoalPanel, self).__init__()
        self.__curHint = _HINT_KILL_LEVIATHAN
        self.__goalHints = {_HINT_KILL_LEVIATHAN: (INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_KILLLEVIATHANTITLE, INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_KILLLEVIATHANMSG),
         _HINT_HALF_WAY: (INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_KILLLEVIATHANTITLE, INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_HALFWAYLEVIATHANMSG),
         _HINT_IS_CLOSE_TO_GATE: (INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_KILLLEVIATHANTITLE, INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_LEVIATHANCLOSEMSG),
         _HINT_ENTERED_CAPTURE: (INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_ENTERSCAPTURETITLE, INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_ENTERSCAPTUREMSG)}

    def _dispose(self):
        BigWorld.player().arena.onTeamBasePointsUpdate -= self.__arena_onTeamBasePointsUpdated
        BigWorld.player().onLeviathanProgressUpdate -= self.__avatar_onLeviathanProgressUpdated
        super(PvEGoalPanel, self)._dispose()

    def _populate(self):
        super(PvEGoalPanel, self)._populate()
        BigWorld.player().onLeviathanProgressUpdate += self.__avatar_onLeviathanProgressUpdated
        BigWorld.player().arena.onTeamBasePointsUpdate += self.__arena_onTeamBasePointsUpdated
        self.as_showPanelS()
        self.__submitGoalMessage(_HINT_KILL_LEVIATHAN)

    def __submitGoalMessage(self, stage):
        hint = self.__goalHints.get(stage)
        if hint is not None:
            self.__curHint = stage
            self.as_setMessageS(hint[_TITLE], hint[_MESSAGE])
        return

    def __avatar_onLeviathanProgressUpdated(self, leviathanHealth, progress):
        newHint = self.__curHint
        if progress > LEVIATHAN_HALFWAY_PROGRESS and newHint < _HINT_HALF_WAY:
            newHint = _HINT_HALF_WAY
        if progress > LEVIATHAN_PROGRESS_CLOSE and newHint < _HINT_IS_CLOSE_TO_GATE:
            newHint = _HINT_IS_CLOSE_TO_GATE
        if newHint != self.__curHint:
            self.__submitGoalMessage(newHint)

    def __arena_onTeamBasePointsUpdated(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        if points > 0 and self.__curHint < _HINT_ENTERED_CAPTURE:
            self.__submitGoalMessage(_HINT_ENTERED_CAPTURE)

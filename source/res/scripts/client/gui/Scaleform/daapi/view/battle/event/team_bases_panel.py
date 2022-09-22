# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/team_bases_panel.py
from gui.Scaleform.daapi.view.meta.TeamBasesPanelMeta import TeamBasesPanelMeta
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from skeletons.gui.battle_session import IBattleSessionProvider

class EventTeamBasesPanel(TeamBasesPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _COLOR = 'eventPurple'

    def __init__(self):
        super(EventTeamBasesPanel, self).__init__()
        self.__activeList = []

    def _populate(self):
        super(EventTeamBasesPanel, self)._populate()
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onGeneratorCapture += self.__onGeneratorCapture
            feedback.onGeneratorStopCapture += self.__onGeneratorStopCapture
        return

    def _dispose(self):
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onGeneratorCapture -= self.__onGeneratorCapture
            feedback.onGeneratorStopCapture -= self.__onGeneratorStopCapture
        super(EventTeamBasesPanel, self)._dispose()
        return

    def __onGeneratorCapture(self, index, progress, timeLeft, numInvaders):
        text = backport.text(R.strings.event.teamBasePanel.capturing(), num=index, percent=progress)
        timeText = time_utils.getTimeLeftFormat(timeLeft)
        invadersText = str(numInvaders)
        if index not in self.__activeList:
            self.as_addS(index, 0, self._COLOR, text, 0, timeText, invadersText)
            self.__activeList.append(index)
        self.as_updateCaptureDataS(index, progress, 1, timeText, invadersText, text, self._COLOR)

    def __onGeneratorStopCapture(self, index):
        if index in self.__activeList:
            self.as_updateCaptureDataS(index, 0, 0, '', '', '', self._COLOR)
            self.as_removeS(index)
            self.__activeList.remove(index)

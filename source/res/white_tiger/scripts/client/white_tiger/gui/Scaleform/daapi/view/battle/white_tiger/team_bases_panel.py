# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/team_bases_panel.py
from gui.Scaleform.daapi.view.meta.TeamBasesPanelMeta import TeamBasesPanelMeta
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from skeletons.gui.battle_session import IBattleSessionProvider

class WhiteTigerTeamBasesPanel(TeamBasesPanelMeta):
    _COLOR = 'eventPurple'
    _GENERATOR_ID_TO_NAME = {1: 'A',
     2: 'B',
     3: 'C'}
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerTeamBasesPanel, self).__init__()
        self.__activeList = []

    def _populate(self):
        super(WhiteTigerTeamBasesPanel, self)._populate()
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
        super(WhiteTigerTeamBasesPanel, self)._dispose()
        return

    def __onGeneratorCapture(self, index, progress, timeLeft, numInvaders):
        text = backport.text(R.strings.white_tiger.teamBasePanel.capturing(), num=self._GENERATOR_ID_TO_NAME.get(index), percent=progress)
        timeText = time_utils.getTimeLeftFormat(timeLeft)
        invadersText = str(numInvaders)
        if index not in self.__activeList:
            self.as_addS(index, 0, self._COLOR, text, 0, timeText, invadersText)
            self.__activeList.append(index)
        self.as_updateCaptureDataS(index, progress, 1, timeText, invadersText, text, self._COLOR)

    def __onGeneratorStopCapture(self, index, wasCaptured):
        if index in self.__activeList:
            self.as_updateCaptureDataS(index, 0, 0, '', '', '', self._COLOR)
            self.as_removeS(index)
            self.__activeList.remove(index)

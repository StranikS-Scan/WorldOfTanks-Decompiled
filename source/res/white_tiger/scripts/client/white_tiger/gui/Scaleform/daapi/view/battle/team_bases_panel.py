# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/team_bases_panel.py
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerTeamBasesPanelMeta import WhiteTigerTeamBasesPanelMeta
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.cgf_components.wt_helpers import getBattleStateComponent

class WhiteTigerTeamBasesPanel(WhiteTigerTeamBasesPanelMeta):
    _COLOR = 'WhiteTigerPurple'
    _GENERATOR_ID_TO_NAME = {1: 'A',
     2: 'B',
     3: 'C'}
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerTeamBasesPanel, self).__init__()
        self.__activeList = []
        self.__isInCaptureProgress = False

    def _populate(self):
        super(WhiteTigerTeamBasesPanel, self)._populate()
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.onGeneratorCapture += self.__onGeneratorCapture
            battleStateComponent.onGeneratorStopCapture += self.__onGeneratorStopCapture

    def __onGeneratorCapture(self, index, progress, timeLeft, numInvaders, isBlocked):
        self.__isInCaptureProgress = True
        text = backport.text(R.strings.white_tiger_battle.teamBasePanel.capturing(), num=self._GENERATOR_ID_TO_NAME.get(index), percent=progress)
        timeText = time_utils.getTimeLeftFormat(timeLeft)
        invadersText = str(numInvaders)
        if index not in self.__activeList:
            self.as_addS(index, 0, self._COLOR, text, 0, timeText, invadersText)
            self.__activeList.append(index)
        self.as_updateCaptureS(index, progress, 1, timeText, invadersText, text, self._COLOR, isBlocked)

    def __onGeneratorStopCapture(self, index, wasCaptured):
        self.__isInCaptureProgress = False
        if index in self.__activeList:
            self.as_updateCaptureDataS(index, 0, 0, '', '', '', self._COLOR)
            self.as_removeS(index)
            self.__activeList.remove(index)

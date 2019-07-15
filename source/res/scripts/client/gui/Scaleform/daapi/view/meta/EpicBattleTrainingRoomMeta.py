# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattleTrainingRoomMeta.py
from gui.Scaleform.daapi.view.lobby.trainings.TrainingRoomBase import TrainingRoomBase

class EpicBattleTrainingRoomMeta(TrainingRoomBase):

    def onChangeTeamLane(self, accID, team, lane):
        self._printOverrideError('onChangeTeamLane')

    def onSwapTeamLane(self, fromTeam, fromLane, toTeam, toLane):
        self._printOverrideError('onSwapTeamLane')

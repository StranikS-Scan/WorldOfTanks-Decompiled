# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportRespawnFormMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class CyberSportRespawnFormMeta(BaseRallyRoomView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyRoomView
    """

    def as_updateEnemyStatusS(self, statusID, enemyStatusLabel):
        return self.flashObject.as_updateEnemyStatus(statusID, enemyStatusLabel) if self._isDAAPIInited() else None

    def as_setTeamNameS(self, name):
        return self.flashObject.as_setTeamName(name) if self._isDAAPIInited() else None

    def as_setTeamEmblemS(self, teamEmblemId):
        return self.flashObject.as_setTeamEmblem(teamEmblemId) if self._isDAAPIInited() else None

    def as_setArenaTypeIdS(self, mapName, arenaTypeID):
        return self.flashObject.as_setArenaTypeId(mapName, arenaTypeID) if self._isDAAPIInited() else None

    def as_timerUpdateS(self, timeLeft):
        return self.flashObject.as_timerUpdate(timeLeft) if self._isDAAPIInited() else None

    def as_statusUpdateS(self, status, level, tooltip):
        return self.flashObject.as_statusUpdate(status, level, tooltip) if self._isDAAPIInited() else None

    def as_setTotalLabelS(self, hasTotalLevelError, totalLevelLabel, totalLevel):
        return self.flashObject.as_setTotalLabel(hasTotalLevelError, totalLevelLabel, totalLevel) if self._isDAAPIInited() else None

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportRespawnFormMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class CyberSportRespawnFormMeta(BaseRallyRoomView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyRoomView
    null
    """

    def as_updateEnemyStatusS(self, statusID, enemyStatusLabel):
        """
        :param statusID:
        :param enemyStatusLabel:
        :return :
        """
        return self.flashObject.as_updateEnemyStatus(statusID, enemyStatusLabel) if self._isDAAPIInited() else None

    def as_setTeamNameS(self, name):
        """
        :param name:
        :return :
        """
        return self.flashObject.as_setTeamName(name) if self._isDAAPIInited() else None

    def as_setTeamEmblemS(self, teamEmblemId):
        """
        :param teamEmblemId:
        :return :
        """
        return self.flashObject.as_setTeamEmblem(teamEmblemId) if self._isDAAPIInited() else None

    def as_setArenaTypeIdS(self, mapName, arenaTypeID):
        """
        :param mapName:
        :param arenaTypeID:
        :return :
        """
        return self.flashObject.as_setArenaTypeId(mapName, arenaTypeID) if self._isDAAPIInited() else None

    def as_timerUpdateS(self, timeLeft):
        """
        :param timeLeft:
        :return :
        """
        return self.flashObject.as_timerUpdate(timeLeft) if self._isDAAPIInited() else None

    def as_statusUpdateS(self, status, level, tooltip):
        """
        :param status:
        :param level:
        :param tooltip:
        :return :
        """
        return self.flashObject.as_statusUpdate(status, level, tooltip) if self._isDAAPIInited() else None

    def as_setTotalLabelS(self, hasTotalLevelError, totalLevelLabel, totalLevel):
        """
        :param hasTotalLevelError:
        :param totalLevelLabel:
        :param totalLevel:
        :return :
        """
        return self.flashObject.as_setTotalLabel(hasTotalLevelError, totalLevelLabel, totalLevel) if self._isDAAPIInited() else None

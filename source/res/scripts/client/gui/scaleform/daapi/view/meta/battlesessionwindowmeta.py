# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleSessionWindowMeta.py
from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattleWindow import PrebattleWindow

class BattleSessionWindowMeta(PrebattleWindow):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends PrebattleWindow
    """

    def requestToAssignMember(self, accId):
        self._printOverrideError('requestToAssignMember')

    def requestToUnassignMember(self, accId):
        self._printOverrideError('requestToUnassignMember')

    def canMoveToAssigned(self):
        self._printOverrideError('canMoveToAssigned')

    def canMoveToUnassigned(self):
        self._printOverrideError('canMoveToUnassigned')

    def as_setStartTimeS(self, value):
        return self.flashObject.as_setStartTime(value) if self._isDAAPIInited() else None

    def as_setTotalPlayersCountS(self, value):
        return self.flashObject.as_setTotalPlayersCount(value) if self._isDAAPIInited() else None

    def as_setInfoS(self, wins, map, firstTeam, secondTeam, count, description, comment):
        return self.flashObject.as_setInfo(wins, map, firstTeam, secondTeam, count, description, comment) if self._isDAAPIInited() else None

    def as_setNationsLimitsS(self, nations):
        """
        :param nations: Represented by DataProvider (AS)
        """
        return self.flashObject.as_setNationsLimits(nations) if self._isDAAPIInited() else None

    def as_setClassesLimitsS(self, vehicleLevels, classesLimitsAreIdentical):
        return self.flashObject.as_setClassesLimits(vehicleLevels, classesLimitsAreIdentical) if self._isDAAPIInited() else None

    def as_setCommonLimitsS(self, teamLevel, maxPlayers):
        return self.flashObject.as_setCommonLimits(teamLevel, maxPlayers) if self._isDAAPIInited() else None

    def as_setPlayersCountTextS(self, playersCountText):
        return self.flashObject.as_setPlayersCountText(playersCountText) if self._isDAAPIInited() else None

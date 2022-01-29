# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleSessionWindowMeta.py
from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattleWindow import PrebattleWindow

class BattleSessionWindowMeta(PrebattleWindow):

    def requestToAssignMember(self, accId):
        self._printOverrideError('requestToAssignMember')

    def requestToUnassignMember(self, accId):
        self._printOverrideError('requestToUnassignMember')

    def canMoveToAssigned(self, accId):
        self._printOverrideError('canMoveToAssigned')

    def canMoveToUnassigned(self, accId):
        self._printOverrideError('canMoveToUnassigned')

    def setSelectedFilter(self, value):
        self._printOverrideError('setSelectedFilter')

    def onCantMoveS(self, accId):
        self._printOverrideError('onCantMoveS')

    def as_setStartTimeS(self, value):
        return self.flashObject.as_setStartTime(value) if self._isDAAPIInited() else None

    def as_setTotalPlayersCountS(self, value):
        return self.flashObject.as_setTotalPlayersCount(value) if self._isDAAPIInited() else None

    def as_setInfoS(self, isTurnamentBattle, wins, map, firstTeam, secondTeam, count, description, comment, unitLetter, vehicleLevel, teamIndex):
        return self.flashObject.as_setInfo(isTurnamentBattle, wins, map, firstTeam, secondTeam, count, description, comment, unitLetter, vehicleLevel, teamIndex) if self._isDAAPIInited() else None

    def as_setWinnerIfDrawS(self, value=0):
        return self.flashObject.as_setWinnerIfDraw(value) if self._isDAAPIInited() else None

    def as_setNationsLimitsS(self, nations):
        return self.flashObject.as_setNationsLimits(nations) if self._isDAAPIInited() else None

    def as_setClassesLimitsS(self, vehicleLevels, classesLimitsAreIdentical):
        return self.flashObject.as_setClassesLimits(vehicleLevels, classesLimitsAreIdentical) if self._isDAAPIInited() else None

    def as_setCommonLimitsS(self, teamLevel, maxPlayers):
        return self.flashObject.as_setCommonLimits(teamLevel, maxPlayers) if self._isDAAPIInited() else None

    def as_setPlayersCountTextS(self, playersCountText):
        return self.flashObject.as_setPlayersCountText(playersCountText) if self._isDAAPIInited() else None

    def as_setFiltersS(self, data, selectedIndex):
        return self.flashObject.as_setFilters(data, selectedIndex) if self._isDAAPIInited() else None

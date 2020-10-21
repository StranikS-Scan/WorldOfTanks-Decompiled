# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBattleResultScreenMeta.py
from gui.Scaleform.framework.entities.View import View

class EventBattleResultScreenMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def playSliderSound(self):
        self._printOverrideError('playSliderSound')

    def playPointsSound(self):
        self._printOverrideError('playPointsSound')

    def playQuestSound(self):
        self._printOverrideError('playQuestSound')

    def playRewardSound(self):
        self._printOverrideError('playRewardSound')

    def playProgressBarSound(self):
        self._printOverrideError('playProgressBarSound')

    def addToSquad(self, databaseID):
        self._printOverrideError('addToSquad')

    def addToFriend(self, databaseID, userName):
        self._printOverrideError('addToFriend')

    def as_setVictoryDataS(self, data, canInvite, friends):
        return self.flashObject.as_setVictoryData(data, canInvite, friends) if self._isDAAPIInited() else None

    def as_playAnimationS(self):
        return self.flashObject.as_playAnimation() if self._isDAAPIInited() else None

    def as_addToSquadResultS(self, result, databaseID):
        return self.flashObject.as_addToSquadResult(result, databaseID) if self._isDAAPIInited() else None

    def as_addToFriendResultS(self, result, databaseID):
        return self.flashObject.as_addToFriendResult(result, databaseID) if self._isDAAPIInited() else None

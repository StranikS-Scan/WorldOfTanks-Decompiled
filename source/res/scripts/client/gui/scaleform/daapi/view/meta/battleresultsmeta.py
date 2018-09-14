# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleResultsMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BattleResultsMeta(AbstractWindowView):

    def saveSorting(self, iconType, sortDirection, bonusType):
        self._printOverrideError('saveSorting')

    def showEventsWindow(self, questID, eventType):
        self._printOverrideError('showEventsWindow')

    def getClanEmblem(self, uid, clanID):
        self._printOverrideError('getClanEmblem')

    def getTeamEmblem(self, uid, teamID, isUseHtmlWrap):
        self._printOverrideError('getTeamEmblem')

    def startCSAnimationSound(self):
        self._printOverrideError('startCSAnimationSound')

    def onResultsSharingBtnPress(self):
        self._printOverrideError('onResultsSharingBtnPress')

    def onTeamCardClick(self, teamDBID):
        self._printOverrideError('onTeamCardClick')

    def showUnlockWindow(self, itemId, unlockType):
        self._printOverrideError('showUnlockWindow')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setClanEmblemS(self, uid, iconTag):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanEmblem(uid, iconTag)

    def as_setTeamInfoS(self, uid, iconTag, teamName):
        if self._isDAAPIInited():
            return self.flashObject.as_setTeamInfo(uid, iconTag, teamName)

    def as_setAnimationS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setAnimation(data)

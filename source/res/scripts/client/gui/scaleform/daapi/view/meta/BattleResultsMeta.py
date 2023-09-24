# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleResultsMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BattleResultsMeta(AbstractWindowView):

    def saveSorting(self, iconType, sortDirection, bonusType):
        self._printOverrideError('saveSorting')

    def showEventsWindow(self, questID, eventType):
        self._printOverrideError('showEventsWindow')

    def getClanEmblem(self, uid, clanID):
        self._printOverrideError('getClanEmblem')

    def onResultsSharingBtnPress(self):
        self._printOverrideError('onResultsSharingBtnPress')

    def showUnlockWindow(self, itemId, unlockType):
        self._printOverrideError('showUnlockWindow')

    def showProgressiveRewardView(self):
        self._printOverrideError('showProgressiveRewardView')

    def onAppliedPremiumBonus(self):
        self._printOverrideError('onAppliedPremiumBonus')

    def onShowDetailsPremium(self):
        self._printOverrideError('onShowDetailsPremium')

    def showDogTagWindow(self, componentId):
        self._printOverrideError('showDogTagWindow')

    def showVehicleStats(self, vehCD):
        self._printOverrideError('showVehicleStats')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, uid, iconTag):
        return self.flashObject.as_setClanEmblem(uid, iconTag) if self._isDAAPIInited() else None

    def as_setTeamInfoS(self, uid, iconTag, teamName):
        return self.flashObject.as_setTeamInfo(uid, iconTag, teamName) if self._isDAAPIInited() else None

    def as_setIsInBattleQueueS(self, value):
        return self.flashObject.as_setIsInBattleQueue(value) if self._isDAAPIInited() else None

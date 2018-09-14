# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AccountPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class AccountPopoverMeta(SmartPopOverView):

    def openBoostersWindow(self, slotId):
        self._printOverrideError('openBoostersWindow')

    def openClanStatistic(self):
        self._printOverrideError('openClanStatistic')

    def openCrewStatistic(self):
        self._printOverrideError('openCrewStatistic')

    def openReferralManagement(self):
        self._printOverrideError('openReferralManagement')

    def as_setDataS(self, userData, isTeamKiller, mainAchievements, infoBtnEnabled, clanData, crewData, boostersBlockTitle):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(userData, isTeamKiller, mainAchievements, infoBtnEnabled, clanData, crewData, boostersBlockTitle)

    def as_setClanEmblemS(self, emblemId):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanEmblem(emblemId)

    def as_setCrewEmblemS(self, emblemId):
        if self._isDAAPIInited():
            return self.flashObject.as_setCrewEmblem(emblemId)

    def as_setReferralDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setReferralData(data)

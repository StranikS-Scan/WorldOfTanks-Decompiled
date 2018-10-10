# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileHofMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection

class ProfileHofMeta(ProfileSection):

    def showVehiclesRating(self):
        self._printOverrideError('showVehiclesRating')

    def showAchievementsRating(self):
        self._printOverrideError('showAchievementsRating')

    def changeStatus(self):
        self._printOverrideError('changeStatus')

    def as_setStatusS(self, state):
        return self.flashObject.as_setStatus(state) if self._isDAAPIInited() else None

    def as_setBackgroundS(self, source):
        return self.flashObject.as_setBackground(source) if self._isDAAPIInited() else None

    def as_setBtnCountersS(self, counters):
        return self.flashObject.as_setBtnCounters(counters) if self._isDAAPIInited() else None

    def as_showServiceViewS(self, header, description):
        return self.flashObject.as_showServiceView(header, description) if self._isDAAPIInited() else None

    def as_hideServiceViewS(self):
        return self.flashObject.as_hideServiceView() if self._isDAAPIInited() else None

    def as_showWaitingS(self, description):
        return self.flashObject.as_showWaiting(description) if self._isDAAPIInited() else None

    def as_hideWaitingS(self):
        return self.flashObject.as_hideWaiting() if self._isDAAPIInited() else None

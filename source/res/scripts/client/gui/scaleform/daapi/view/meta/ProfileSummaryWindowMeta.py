# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileSummaryWindowMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSummary import ProfileSummary

class ProfileSummaryWindowMeta(ProfileSummary):

    def openClanStatistic(self):
        self._printOverrideError('openClanStatistic')

    def as_setClanDataS(self, data):
        return self.flashObject.as_setClanData(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, source):
        return self.flashObject.as_setClanEmblem(source) if self._isDAAPIInited() else None

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileSectionWithTabsMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection

class ProfileSectionWithTabsMeta(ProfileSection):

    def setSeasonStatisticsFilter(self, value):
        self._printOverrideError('setSeasonStatisticsFilter')

    def as_setTabsDataS(self, tabs):
        return self.flashObject.as_setTabsData(tabs) if self._isDAAPIInited() else None

    def as_setTabCounterS(self, sectionIdx, value):
        return self.flashObject.as_setTabCounter(sectionIdx, value) if self._isDAAPIInited() else None

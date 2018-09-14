# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileAchievementSectionMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection

class ProfileAchievementSectionMeta(ProfileSection):

    def as_setRareAchievementDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setRareAchievementData(data)

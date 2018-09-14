# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileAchievementSectionMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection

class ProfileAchievementSectionMeta(ProfileSection):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ProfileSection
    null
    """

    def as_setRareAchievementDataS(self, rareID, rareIconId):
        """
        :param rareID:
        :param rareIconId:
        :return :
        """
        return self.flashObject.as_setRareAchievementData(rareID, rareIconId) if self._isDAAPIInited() else None

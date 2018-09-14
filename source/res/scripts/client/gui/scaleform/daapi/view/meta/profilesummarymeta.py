# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileSummaryMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileAchievementSection import ProfileAchievementSection

class ProfileSummaryMeta(ProfileAchievementSection):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ProfileAchievementSection
    null
    """

    def getPersonalScoreWarningText(self, data):
        """
        :param data:
        :return String:
        """
        self._printOverrideError('getPersonalScoreWarningText')

    def getGlobalRating(self, userName):
        """
        :param userName:
        :return Number:
        """
        self._printOverrideError('getGlobalRating')

    def as_setUserDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setUserData(data) if self._isDAAPIInited() else None

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileSummaryWindowMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSummary import ProfileSummary

class ProfileSummaryWindowMeta(ProfileSummary):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ProfileSummary
    null
    """

    def openClanStatistic(self):
        """
        :return :
        """
        self._printOverrideError('openClanStatistic')

    def openClubProfile(self, clubDbID):
        """
        :param clubDbID:
        :return :
        """
        self._printOverrideError('openClubProfile')

    def as_setClanDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setClanData(data) if self._isDAAPIInited() else None

    def as_setClubDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setClubData(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, source):
        """
        :param source:
        :return :
        """
        return self.flashObject.as_setClanEmblem(source) if self._isDAAPIInited() else None

    def as_setClubEmblemS(self, source):
        """
        :param source:
        :return :
        """
        return self.flashObject.as_setClubEmblem(source) if self._isDAAPIInited() else None

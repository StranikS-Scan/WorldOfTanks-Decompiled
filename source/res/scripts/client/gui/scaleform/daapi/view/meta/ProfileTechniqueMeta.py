# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTechniqueMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection

class ProfileTechniqueMeta(ProfileSection):

    def setSelectedTableColumn(self, index, sortDirection):
        self._printOverrideError('setSelectedTableColumn')

    def showVehiclesRating(self):
        self._printOverrideError('showVehiclesRating')

    def as_responseVehicleDossierS(self, data):
        """
        :param data: Represented by ProfileVehicleDossierVO (AS)
        """
        return self.flashObject.as_responseVehicleDossier(data) if self._isDAAPIInited() else None

    def as_setRatingButtonS(self, data):
        """
        :param data: Represented by RatingButtonVO (AS)
        """
        return self.flashObject.as_setRatingButton(data) if self._isDAAPIInited() else None

    def as_setBtnCountersS(self, counters):
        """
        :param counters: Represented by Vector.<CountersVo> (AS)
        """
        return self.flashObject.as_setBtnCounters(counters) if self._isDAAPIInited() else None

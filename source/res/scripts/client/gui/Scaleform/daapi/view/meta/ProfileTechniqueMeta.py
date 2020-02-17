# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTechniqueMeta.py
from gui.Scaleform.daapi.view.meta.ProfileSectionWithTabsMeta import ProfileSectionWithTabsMeta

class ProfileTechniqueMeta(ProfileSectionWithTabsMeta):

    def setSelectedTableColumn(self, index, sortDirection):
        self._printOverrideError('setSelectedTableColumn')

    def showVehiclesRating(self):
        self._printOverrideError('showVehiclesRating')

    def as_responseVehicleDossierS(self, data):
        return self.flashObject.as_responseVehicleDossier(data) if self._isDAAPIInited() else None

    def as_setRatingButtonS(self, data):
        return self.flashObject.as_setRatingButton(data) if self._isDAAPIInited() else None

    def as_setBtnCountersS(self, counters):
        return self.flashObject.as_setBtnCounters(counters) if self._isDAAPIInited() else None

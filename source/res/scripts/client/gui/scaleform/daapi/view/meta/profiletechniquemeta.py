# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTechniqueMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection

class ProfileTechniqueMeta(ProfileSection):

    def as_responseVehicleDossierS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_responseVehicleDossier(data)

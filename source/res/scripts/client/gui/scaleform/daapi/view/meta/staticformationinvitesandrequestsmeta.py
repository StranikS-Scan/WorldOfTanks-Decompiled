# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationInvitesAndRequestsMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class StaticFormationInvitesAndRequestsMeta(AbstractWindowView):

    def setDescription(self, value):
        self._printOverrideError('setDescription')

    def setShowOnlyInvites(self, value):
        self._printOverrideError('setShowOnlyInvites')

    def resolvePlayerRequest(self, playerId, playerAccepted):
        self._printOverrideError('resolvePlayerRequest')

    def as_getDataProviderS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getDataProvider()

    def as_setStaticDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setStaticData(data)

    def as_setTeamDescriptionS(self, description):
        if self._isDAAPIInited():
            return self.flashObject.as_setTeamDescription(description)

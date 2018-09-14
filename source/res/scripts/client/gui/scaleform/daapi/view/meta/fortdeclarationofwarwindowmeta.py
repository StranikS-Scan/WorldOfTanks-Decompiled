# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDeclarationOfWarWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortDeclarationOfWarWindowMeta(AbstractWindowView):

    def onDirectonChosen(self, directionUID):
        self._printOverrideError('onDirectonChosen')

    def onDirectionSelected(self):
        self._printOverrideError('onDirectionSelected')

    def as_setupHeaderS(self, title, description):
        if self._isDAAPIInited():
            return self.flashObject.as_setupHeader(title, description)

    def as_setupClansS(self, myClan, enemyClan):
        if self._isDAAPIInited():
            return self.flashObject.as_setupClans(myClan, enemyClan)

    def as_setDirectionsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setDirections(data)

    def as_selectDirectionS(self, uid):
        if self._isDAAPIInited():
            return self.flashObject.as_selectDirection(uid)

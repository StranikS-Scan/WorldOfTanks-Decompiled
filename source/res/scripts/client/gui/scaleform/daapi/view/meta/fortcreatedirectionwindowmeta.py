# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCreateDirectionWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortCreateDirectionWindowMeta(AbstractWindowView):

    def openNewDirection(self):
        self._printOverrideError('openNewDirection')

    def closeDirection(self, id):
        self._printOverrideError('closeDirection')

    def as_setDescriptionS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setDescription(value)

    def as_setupButtonS(self, enabled, visible, ttHeader, ttDescr):
        if self._isDAAPIInited():
            return self.flashObject.as_setupButton(enabled, visible, ttHeader, ttDescr)

    def as_setDirectionsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setDirections(data)

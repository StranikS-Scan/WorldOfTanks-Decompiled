# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationLadderViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StaticFormationLadderViewMeta(DAAPIModule):

    def showFormationProfile(self, fromationId):
        self._printOverrideError('showFormationProfile')

    def as_updateHeaderDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateHeaderData(data)

    def as_updateLadderDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateLadderData(data)

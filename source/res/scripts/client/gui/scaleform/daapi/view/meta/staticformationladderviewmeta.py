# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationLadderViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StaticFormationLadderViewMeta(BaseDAAPIComponent):

    def showFormationProfile(self, fromationId):
        self._printOverrideError('showFormationProfile')

    def updateClubIcons(self, ids):
        self._printOverrideError('updateClubIcons')

    def as_updateHeaderDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateHeaderData(data)

    def as_updateLadderDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateLadderData(data)

    def as_setLadderStateS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setLadderState(data)

    def as_onUpdateClubIconsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_onUpdateClubIcons(data)

    def as_onUpdateClubIconS(self, clubId, iconPath):
        if self._isDAAPIInited():
            return self.flashObject.as_onUpdateClubIcon(clubId, iconPath)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CrewMeta(BaseDAAPIComponent):

    def onFilterToggle(self, index):
        self._printOverrideError('onFilterToggle')

    def unloadAllTankman(self):
        self._printOverrideError('unloadAllTankman')

    def equipTankman(self, tankmanID, slot):
        self._printOverrideError('equipTankman')

    def onCrewDogMoreInfoClick(self):
        self._printOverrideError('onCrewDogMoreInfoClick')

    def onCrewDogItemClick(self):
        self._printOverrideError('onCrewDogItemClick')

    def onConvertClick(self):
        self._printOverrideError('onConvertClick')

    def openChangeRoleWindow(self, tankmanID):
        self._printOverrideError('openChangeRoleWindow')

    def onPlayVideoClick(self):
        self._printOverrideError('onPlayVideoClick')

    def as_tankmenResponseS(self, data):
        return self.flashObject.as_tankmenResponse(data) if self._isDAAPIInited() else None

    def as_dogResponseS(self, dogName):
        return self.flashObject.as_dogResponse(dogName) if self._isDAAPIInited() else None

    def as_setDogTooltipS(self, tooltipId):
        return self.flashObject.as_setDogTooltip(tooltipId) if self._isDAAPIInited() else None

    def as_setConvertDataS(self, data):
        return self.flashObject.as_setConvertData(data) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

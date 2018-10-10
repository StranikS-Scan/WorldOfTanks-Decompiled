# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CrewMeta(BaseDAAPIComponent):

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        self._printOverrideError('onShowRecruitWindowClick')

    def unloadAllTankman(self):
        self._printOverrideError('unloadAllTankman')

    def equipTankman(self, tankmanID, slot):
        self._printOverrideError('equipTankman')

    def updateTankmen(self):
        self._printOverrideError('updateTankmen')

    def openPersonalCase(self, value, tabNumber):
        self._printOverrideError('openPersonalCase')

    def onCrewDogMoreInfoClick(self):
        self._printOverrideError('onCrewDogMoreInfoClick')

    def onCrewDogItemClick(self):
        self._printOverrideError('onCrewDogItemClick')

    def as_tankmenResponseS(self, data):
        return self.flashObject.as_tankmenResponse(data) if self._isDAAPIInited() else None

    def as_dogResponseS(self, dogName):
        return self.flashObject.as_dogResponse(dogName) if self._isDAAPIInited() else None

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventPlayersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventPlayersPanelMeta(BaseDAAPIComponent):

    def as_setPlayerPanelInfoS(self, data):
        return self.flashObject.as_setPlayerPanelInfo(data) if self._isDAAPIInited() else None

    def as_setPlayerPanelCountLivesS(self, vehID, countLives):
        return self.flashObject.as_setPlayerPanelCountLives(vehID, countLives) if self._isDAAPIInited() else None

    def as_setPlayerPanelHpS(self, vehID, hpMax, hpCurrent):
        return self.flashObject.as_setPlayerPanelHp(vehID, hpMax, hpCurrent) if self._isDAAPIInited() else None

    def as_setPlayerDeadS(self, vehID):
        return self.flashObject.as_setPlayerDead(vehID) if self._isDAAPIInited() else None

    def as_setBotPanelInfoS(self, vehID, power, nameVehicle, typeVehicle):
        return self.flashObject.as_setBotPanelInfo(vehID, power, nameVehicle, typeVehicle) if self._isDAAPIInited() else None

    def as_setBotDeadS(self, vehID):
        return self.flashObject.as_setBotDead(vehID) if self._isDAAPIInited() else None

    def as_setPlayerPanelDescriptionsS(self, descriptionTabButton, descriptionZButton):
        return self.flashObject.as_setPlayerPanelDescriptions(descriptionTabButton, descriptionZButton) if self._isDAAPIInited() else None

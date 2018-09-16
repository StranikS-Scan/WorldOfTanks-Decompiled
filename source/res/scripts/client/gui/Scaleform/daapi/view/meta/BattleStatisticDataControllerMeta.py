# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleStatisticDataControllerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleStatisticDataControllerMeta(BaseDAAPIComponent):

    def onRefreshComplete(self):
        self._printOverrideError('onRefreshComplete')

    def as_refreshS(self):
        return self.flashObject.as_refresh() if self._isDAAPIInited() else None

    def as_setVehiclesDataS(self, vehData):
        return self.flashObject.as_setVehiclesData(vehData) if self._isDAAPIInited() else None

    def as_addVehiclesInfoS(self, vehInfo):
        return self.flashObject.as_addVehiclesInfo(vehInfo) if self._isDAAPIInited() else None

    def as_updateVehiclesInfoS(self, upVehInfo):
        return self.flashObject.as_updateVehiclesInfo(upVehInfo) if self._isDAAPIInited() else None

    def as_updateVehicleStatusS(self, data):
        return self.flashObject.as_updateVehicleStatus(data) if self._isDAAPIInited() else None

    def as_setFragsS(self, data):
        return self.flashObject.as_setFrags(data) if self._isDAAPIInited() else None

    def as_updateVehiclesStatsS(self, data):
        return self.flashObject.as_updateVehiclesStats(data) if self._isDAAPIInited() else None

    def as_updatePlayerStatusS(self, data):
        return self.flashObject.as_updatePlayerStatus(data) if self._isDAAPIInited() else None

    def as_setArenaInfoS(self, data):
        return self.flashObject.as_setArenaInfo(data) if self._isDAAPIInited() else None

    def as_setUserTagsS(self, data):
        return self.flashObject.as_setUserTags(data) if self._isDAAPIInited() else None

    def as_updateUserTagsS(self, data):
        return self.flashObject.as_updateUserTags(data) if self._isDAAPIInited() else None

    def as_updateInvitationsStatusesS(self, data):
        return self.flashObject.as_updateInvitationsStatuses(data) if self._isDAAPIInited() else None

    def as_setPersonalStatusS(self, bitmask):
        return self.flashObject.as_setPersonalStatus(bitmask) if self._isDAAPIInited() else None

    def as_updatePersonalStatusS(self, added=0, removed=0):
        return self.flashObject.as_updatePersonalStatus(added, removed) if self._isDAAPIInited() else None

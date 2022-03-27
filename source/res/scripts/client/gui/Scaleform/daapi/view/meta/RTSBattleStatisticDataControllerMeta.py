# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RTSBattleStatisticDataControllerMeta.py
from gui.Scaleform.daapi.view.battle.shared.stats_exchange.stats_ctrl import BattleStatisticsDataController

class RTSBattleStatisticDataControllerMeta(BattleStatisticsDataController):

    def as_setRTSCommanderInfoS(self, data):
        return self.flashObject.as_setRTSCommanderInfo(data) if self._isDAAPIInited() else None

    def as_setRTSCommanderDataS(self, data):
        return self.flashObject.as_setRTSCommanderData(data) if self._isDAAPIInited() else None

    def as_setRTSOrderS(self, vehicleID, orderId, isActive):
        return self.flashObject.as_setRTSOrder(vehicleID, orderId, isActive) if self._isDAAPIInited() else None

    def as_setDeviceDamagedS(self, vehicleID, deviceName):
        return self.flashObject.as_setDeviceDamaged(vehicleID, deviceName) if self._isDAAPIInited() else None

    def as_setDeviceRepairedS(self, vehicleID, deviceName):
        return self.flashObject.as_setDeviceRepaired(vehicleID, deviceName) if self._isDAAPIInited() else None

    def as_setRTSCommanderModeS(self, value):
        return self.flashObject.as_setRTSCommanderMode(value) if self._isDAAPIInited() else None

    def as_setRTSPlayerCommanderS(self, value):
        return self.flashObject.as_setRTSPlayerCommander(value) if self._isDAAPIInited() else None

    def as_setRTSSupplyDataS(self, value):
        return self.flashObject.as_setRTSSupplyData(value) if self._isDAAPIInited() else None

    def as_setRTSVehicleGroupS(self, vehicleID, groupID):
        return self.flashObject.as_setRTSVehicleGroup(vehicleID, groupID) if self._isDAAPIInited() else None

    def as_setRTSSelectedVehiclesS(self, vehicleIDs):
        return self.flashObject.as_setRTSSelectedVehicles(vehicleIDs) if self._isDAAPIInited() else None

    def as_setRTSVehicleInFocusS(self, vehicleID):
        return self.flashObject.as_setRTSVehicleInFocus(vehicleID) if self._isDAAPIInited() else None

    def as_setRTSVehiclesInFocusS(self, vehicleIDs, focused):
        return self.flashObject.as_setRTSVehiclesInFocus(vehicleIDs, focused) if self._isDAAPIInited() else None

    def as_setRTSReloadingS(self, vehicleID, updateTime, timeLeft, baseTime):
        return self.flashObject.as_setRTSReloading(vehicleID, updateTime, timeLeft, baseTime) if self._isDAAPIInited() else None

    def as_setRTSSpeakingVehicleS(self, vehicleID, value):
        return self.flashObject.as_setRTSSpeakingVehicle(vehicleID, value) if self._isDAAPIInited() else None

    def as_setRTSVehicleDisabledS(self, vehicleID, value):
        return self.flashObject.as_setRTSVehicleDisabled(vehicleID, value) if self._isDAAPIInited() else None

    def as_setRTSClipDataS(self, vehicleID, maxCount, currentCount, isAutoload, isDualgun):
        return self.flashObject.as_setRTSClipData(vehicleID, maxCount, currentCount, isAutoload, isDualgun) if self._isDAAPIInited() else None

    def as_setRTSVehicleConditionS(self, vehicleID, condition):
        return self.flashObject.as_setRTSVehicleCondition(vehicleID, condition) if self._isDAAPIInited() else None

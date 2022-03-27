# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SpawnMenuMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SpawnMenuMeta(BaseDAAPIComponent):

    def onBGClick(self):
        self._printOverrideError('onBGClick')

    def onAutoSetBtnClick(self):
        self._printOverrideError('onAutoSetBtnClick')

    def onResetBtnClick(self):
        self._printOverrideError('onResetBtnClick')

    def onBattleBtnClick(self):
        self._printOverrideError('onBattleBtnClick')

    def onSupplySelect(self, classTag):
        self._printOverrideError('onSupplySelect')

    def onVehicleSelect(self, vehicleID):
        self._printOverrideError('onVehicleSelect')

    def onPointClick(self, pointID):
        self._printOverrideError('onPointClick')

    def as_setDataS(self, data, mapData):
        return self.flashObject.as_setData(data, mapData) if self._isDAAPIInited() else None

    def as_setItemsDataS(self, alliesData, suppliesData):
        return self.flashObject.as_setItemsData(alliesData, suppliesData) if self._isDAAPIInited() else None

    def as_updateEntriesDataS(self, placePointsData, suppliesData, vehiclesData):
        return self.flashObject.as_updateEntriesData(placePointsData, suppliesData, vehiclesData) if self._isDAAPIInited() else None

    def as_setIsWaitingPlayersS(self, isWaitingPlayers):
        return self.flashObject.as_setIsWaitingPlayers(isWaitingPlayers) if self._isDAAPIInited() else None

    def as_setIsAutoSetBtnEnabledS(self, isAutoSetBtnEnabled):
        return self.flashObject.as_setIsAutoSetBtnEnabled(isAutoSetBtnEnabled) if self._isDAAPIInited() else None

    def as_setIsResetBtnEnabledS(self, isResetBtnEnabled):
        return self.flashObject.as_setIsResetBtnEnabled(isResetBtnEnabled) if self._isDAAPIInited() else None

    def as_setIsBattleBtnEnabledS(self, isBattleBtnEnabled):
        return self.flashObject.as_setIsBattleBtnEnabled(isBattleBtnEnabled) if self._isDAAPIInited() else None

    def as_setIsBootcampS(self, isBootcamp):
        return self.flashObject.as_setIsBootcamp(isBootcamp) if self._isDAAPIInited() else None

    def as_showMapHintS(self, isVisible, colorState, textValue):
        return self.flashObject.as_showMapHint(isVisible, colorState, textValue) if self._isDAAPIInited() else None

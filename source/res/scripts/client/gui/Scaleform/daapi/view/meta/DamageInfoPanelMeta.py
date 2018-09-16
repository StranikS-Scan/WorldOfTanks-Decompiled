# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DamageInfoPanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DamageInfoPanelMeta(BaseDAAPIComponent):

    def as_showS(self, itemList, showFire):
        """
        :param itemList: Represented by Array (AS)
        """
        return self.flashObject.as_show(itemList, showFire) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_updateEngineS(self, stateId, isHit):
        return self.flashObject.as_updateEngine(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideEngineS(self):
        return self.flashObject.as_hideEngine() if self._isDAAPIInited() else None

    def as_updateAmmoBayS(self, stateId, isHit):
        return self.flashObject.as_updateAmmoBay(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideAmmoBayS(self):
        return self.flashObject.as_hideAmmoBay() if self._isDAAPIInited() else None

    def as_updateFuelTankS(self, stateId, isHit):
        return self.flashObject.as_updateFuelTank(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideFuelTankS(self):
        return self.flashObject.as_hideFuelTank() if self._isDAAPIInited() else None

    def as_updateRadioS(self, stateId, isHit):
        return self.flashObject.as_updateRadio(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideRadioS(self):
        return self.flashObject.as_hideRadio() if self._isDAAPIInited() else None

    def as_updateLeftTrackS(self, stateId, isHit):
        return self.flashObject.as_updateLeftTrack(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideLeftTrackS(self):
        return self.flashObject.as_hideLeftTrack() if self._isDAAPIInited() else None

    def as_updateRightTrackS(self, stateId, isHit):
        return self.flashObject.as_updateRightTrack(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideRightTrackS(self):
        return self.flashObject.as_hideRightTrack() if self._isDAAPIInited() else None

    def as_updateGunS(self, stateId, isHit):
        return self.flashObject.as_updateGun(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideGunS(self):
        return self.flashObject.as_hideGun() if self._isDAAPIInited() else None

    def as_updateTurretRotatorS(self, stateId, isHit):
        return self.flashObject.as_updateTurretRotator(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideTurretRotatorS(self):
        return self.flashObject.as_hideTurretRotator() if self._isDAAPIInited() else None

    def as_updateSurveyingDeviceS(self, stateId, isHit):
        return self.flashObject.as_updateSurveyingDevice(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideSurveyingDeviceS(self):
        return self.flashObject.as_hideSurveyingDevice() if self._isDAAPIInited() else None

    def as_updateCommanderS(self, stateId, isHit):
        return self.flashObject.as_updateCommander(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideCommanderS(self):
        return self.flashObject.as_hideCommander() if self._isDAAPIInited() else None

    def as_updateFirstGunnerS(self, stateId, isHit):
        return self.flashObject.as_updateFirstGunner(stateId, isHit) if self._isDAAPIInited() else None

    def as_updateSecondGunnerS(self, stateId, isHit):
        return self.flashObject.as_updateSecondGunner(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideFirstGunnerS(self):
        return self.flashObject.as_hideFirstGunner() if self._isDAAPIInited() else None

    def as_hideSecondGunnerS(self):
        return self.flashObject.as_hideSecondGunner() if self._isDAAPIInited() else None

    def as_updateDriverS(self, stateId, isHit):
        return self.flashObject.as_updateDriver(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideDriverS(self):
        return self.flashObject.as_hideDriver() if self._isDAAPIInited() else None

    def as_updateFirstRadiomanS(self, stateId, isHit):
        return self.flashObject.as_updateFirstRadioman(stateId, isHit) if self._isDAAPIInited() else None

    def as_updateSecondRadiomanS(self, stateId, isHit):
        return self.flashObject.as_updateSecondRadioman(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideFirstRadiomanS(self):
        return self.flashObject.as_hideFirstRadioman() if self._isDAAPIInited() else None

    def as_hideSecondRadiomanS(self):
        return self.flashObject.as_hideSecondRadioman() if self._isDAAPIInited() else None

    def as_updateFirstLoaderS(self, stateId, isHit):
        return self.flashObject.as_updateFirstLoader(stateId, isHit) if self._isDAAPIInited() else None

    def as_updateSecondLoaderS(self, stateId, isHit):
        return self.flashObject.as_updateSecondLoader(stateId, isHit) if self._isDAAPIInited() else None

    def as_hideFirstLoaderS(self):
        return self.flashObject.as_hideFirstLoader() if self._isDAAPIInited() else None

    def as_hideSecondLoaderS(self):
        return self.flashObject.as_hideSecondLoader() if self._isDAAPIInited() else None

    def as_showFireS(self, isHit):
        return self.flashObject.as_showFire(isHit) if self._isDAAPIInited() else None

    def as_hideFireS(self):
        return self.flashObject.as_hideFire() if self._isDAAPIInited() else None

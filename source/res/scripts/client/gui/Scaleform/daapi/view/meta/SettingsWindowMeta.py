# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SettingsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SettingsWindowMeta(AbstractWindowView):

    def applySettings(self, settings, isCloseWnd):
        self._printOverrideError('applySettings')

    def autodetectQuality(self):
        self._printOverrideError('autodetectQuality')

    def startVOIPTest(self, isVoiceTestStarted):
        self._printOverrideError('startVOIPTest')

    def updateCaptureDevices(self):
        self._printOverrideError('updateCaptureDevices')

    def onSettingsChange(self, controlID, controlVal):
        self._printOverrideError('onSettingsChange')

    def altVoicesPreview(self):
        self._printOverrideError('altVoicesPreview')

    def altBulbPreview(self, sampleID):
        self._printOverrideError('altBulbPreview')

    def isSoundModeValid(self):
        self._printOverrideError('isSoundModeValid')

    def showWarningDialog(self, dialogID, settings, isCloseWnd):
        self._printOverrideError('showWarningDialog')

    def onTabSelected(self, tabId):
        self._printOverrideError('onTabSelected')

    def onCounterTargetVisited(self, viewId, subViewId, controlId):
        self._printOverrideError('onCounterTargetVisited')

    def autodetectAcousticType(self):
        self._printOverrideError('autodetectAcousticType')

    def canSelectAcousticType(self, index):
        self._printOverrideError('canSelectAcousticType')

    def openGammaWizard(self, x, y, size):
        self._printOverrideError('openGammaWizard')

    def openColorSettings(self):
        self._printOverrideError('openColorSettings')

    def as_setDataS(self, settingsData):
        return self.flashObject.as_setData(settingsData) if self._isDAAPIInited() else None

    def as_setCaptureDevicesS(self, captureDeviceIdx, devicesData):
        return self.flashObject.as_setCaptureDevices(captureDeviceIdx, devicesData) if self._isDAAPIInited() else None

    def as_onVibroManagerConnectS(self, isConnect):
        return self.flashObject.as_onVibroManagerConnect(isConnect) if self._isDAAPIInited() else None

    def as_updateVideoSettingsS(self, videoSettings):
        return self.flashObject.as_updateVideoSettings(videoSettings) if self._isDAAPIInited() else None

    def as_confirmWarningDialogS(self, isOk, dialogID):
        return self.flashObject.as_confirmWarningDialog(isOk, dialogID) if self._isDAAPIInited() else None

    def as_ConfirmationOfApplicationS(self, isApplied):
        return self.flashObject.as_ConfirmationOfApplication(isApplied) if self._isDAAPIInited() else None

    def as_openTabS(self, tabIndex):
        return self.flashObject.as_openTab(tabIndex) if self._isDAAPIInited() else None

    def as_setGraphicsPresetS(self, presetNum):
        return self.flashObject.as_setGraphicsPreset(presetNum) if self._isDAAPIInited() else None

    def as_isPresetAppliedS(self):
        return self.flashObject.as_isPresetApplied() if self._isDAAPIInited() else None

    def as_setCountersDataS(self, countersData):
        return self.flashObject.as_setCountersData(countersData) if self._isDAAPIInited() else None

    def as_onSoundSpeakersPresetApplyS(self, isApply):
        return self.flashObject.as_onSoundSpeakersPresetApply(isApply) if self._isDAAPIInited() else None

    def as_disableControlS(self, tabId, controlID, subTabId):
        return self.flashObject.as_disableControl(tabId, controlID, subTabId) if self._isDAAPIInited() else None

    def as_setInitDataS(self, isWinXP):
        return self.flashObject.as_setInitData(isWinXP) if self._isDAAPIInited() else None

    def as_setColorGradingTechniqueS(self, icon, label):
        return self.flashObject.as_setColorGradingTechnique(icon, label) if self._isDAAPIInited() else None

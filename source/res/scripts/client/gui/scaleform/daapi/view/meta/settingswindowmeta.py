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

    def isSoundModeValid(self):
        self._printOverrideError('isSoundModeValid')

    def showWarningDialog(self, dialogID, settings, isCloseWnd):
        self._printOverrideError('showWarningDialog')

    def onTabSelected(self, tabId):
        self._printOverrideError('onTabSelected')

    def as_setDataS(self, settingsData):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(settingsData)

    def as_setCaptureDevicesS(self, captureDeviceIdx, devicesData):
        if self._isDAAPIInited():
            return self.flashObject.as_setCaptureDevices(captureDeviceIdx, devicesData)

    def as_onVibroManagerConnectS(self, isConnect):
        if self._isDAAPIInited():
            return self.flashObject.as_onVibroManagerConnect(isConnect)

    def as_updateVideoSettingsS(self, videoSettings):
        if self._isDAAPIInited():
            return self.flashObject.as_updateVideoSettings(videoSettings)

    def as_confirmWarningDialogS(self, isOk, dialogID):
        if self._isDAAPIInited():
            return self.flashObject.as_confirmWarningDialog(isOk, dialogID)

    def as_ConfirmationOfApplicationS(self, isApplied):
        if self._isDAAPIInited():
            return self.flashObject.as_ConfirmationOfApplication(isApplied)

    def as_openTabS(self, tabIndex):
        if self._isDAAPIInited():
            return self.flashObject.as_openTab(tabIndex)

    def as_setGraphicsPresetS(self, presetNum):
        if self._isDAAPIInited():
            return self.flashObject.as_setGraphicsPreset(presetNum)

    def as_isPresetAppliedS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_isPresetApplied()

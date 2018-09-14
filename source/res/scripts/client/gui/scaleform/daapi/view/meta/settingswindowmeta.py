# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SettingsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SettingsWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def applySettings(self, settings, isCloseWnd):
        """
        :param settings:
        :param isCloseWnd:
        :return :
        """
        self._printOverrideError('applySettings')

    def autodetectQuality(self):
        """
        :return Number:
        """
        self._printOverrideError('autodetectQuality')

    def startVOIPTest(self, isVoiceTestStarted):
        """
        :param isVoiceTestStarted:
        :return Boolean:
        """
        self._printOverrideError('startVOIPTest')

    def updateCaptureDevices(self):
        """
        :return :
        """
        self._printOverrideError('updateCaptureDevices')

    def onSettingsChange(self, controlID, controlVal):
        """
        :param controlID:
        :param controlVal:
        :return :
        """
        self._printOverrideError('onSettingsChange')

    def altVoicesPreview(self):
        """
        :return :
        """
        self._printOverrideError('altVoicesPreview')

    def isSoundModeValid(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isSoundModeValid')

    def showWarningDialog(self, dialogID, settings, isCloseWnd):
        """
        :param dialogID:
        :param settings:
        :param isCloseWnd:
        :return :
        """
        self._printOverrideError('showWarningDialog')

    def onTabSelected(self, tabId):
        """
        :param tabId:
        :return :
        """
        self._printOverrideError('onTabSelected')

    def as_setDataS(self, settingsData):
        """
        :param settingsData:
        :return :
        """
        return self.flashObject.as_setData(settingsData) if self._isDAAPIInited() else None

    def as_setCaptureDevicesS(self, captureDeviceIdx, devicesData):
        """
        :param captureDeviceIdx:
        :param devicesData:
        :return :
        """
        return self.flashObject.as_setCaptureDevices(captureDeviceIdx, devicesData) if self._isDAAPIInited() else None

    def as_onVibroManagerConnectS(self, isConnect):
        """
        :param isConnect:
        :return :
        """
        return self.flashObject.as_onVibroManagerConnect(isConnect) if self._isDAAPIInited() else None

    def as_updateVideoSettingsS(self, videoSettings):
        """
        :param videoSettings:
        :return :
        """
        return self.flashObject.as_updateVideoSettings(videoSettings) if self._isDAAPIInited() else None

    def as_confirmWarningDialogS(self, isOk, dialogID):
        """
        :param isOk:
        :param dialogID:
        :return :
        """
        return self.flashObject.as_confirmWarningDialog(isOk, dialogID) if self._isDAAPIInited() else None

    def as_ConfirmationOfApplicationS(self, isApplied):
        """
        :param isApplied:
        :return :
        """
        return self.flashObject.as_ConfirmationOfApplication(isApplied) if self._isDAAPIInited() else None

    def as_openTabS(self, tabIndex):
        """
        :param tabIndex:
        :return :
        """
        return self.flashObject.as_openTab(tabIndex) if self._isDAAPIInited() else None

    def as_setGraphicsPresetS(self, presetNum):
        """
        :param presetNum:
        :return :
        """
        return self.flashObject.as_setGraphicsPreset(presetNum) if self._isDAAPIInited() else None

    def as_isPresetAppliedS(self):
        """
        :return Boolean:
        """
        return self.flashObject.as_isPresetApplied() if self._isDAAPIInited() else None

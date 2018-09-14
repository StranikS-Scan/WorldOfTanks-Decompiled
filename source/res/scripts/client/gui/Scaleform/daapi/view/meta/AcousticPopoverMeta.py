# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AcousticPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class AcousticPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    """

    def onActionStart(self, actionID):
        self._printOverrideError('onActionStart')

    def onSpeakerClick(self, speakerID):
        self._printOverrideError('onSpeakerClick')

    def as_setDataS(self, data):
        """
        :param data: Represented by AcousticPopoverVo (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_onItemPlayS(self, itemsID):
        return self.flashObject.as_onItemPlay(itemsID) if self._isDAAPIInited() else None

    def as_onItemSelectS(self, itemsID):
        return self.flashObject.as_onItemSelect(itemsID) if self._isDAAPIInited() else None

    def as_setEnableS(self, isEnable):
        return self.flashObject.as_setEnable(isEnable) if self._isDAAPIInited() else None

    def as_updateBtnEnabledS(self, btnId, isEnabled):
        return self.flashObject.as_updateBtnEnabled(btnId, isEnabled) if self._isDAAPIInited() else None

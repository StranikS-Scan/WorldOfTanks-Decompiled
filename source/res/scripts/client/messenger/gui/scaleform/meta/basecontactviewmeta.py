# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/BaseContactViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BaseContactViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onOk(self, data):
        self._printOverrideError('onOk')

    def onCancel(self):
        self._printOverrideError('onCancel')

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None

    def as_setOkBtnEnabledS(self, isEnabled):
        return self.flashObject.as_setOkBtnEnabled(isEnabled) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_closeViewS(self):
        return self.flashObject.as_closeView() if self._isDAAPIInited() else None

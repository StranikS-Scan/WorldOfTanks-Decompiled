# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCompareConfiguratorBaseViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehicleCompareConfiguratorBaseViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def applyConfig(self):
        self._printOverrideError('applyConfig')

    def resetConfig(self):
        self._printOverrideError('resetConfig')

    def onCloseView(self):
        self._printOverrideError('onCloseView')

    def as_setResetEnabledS(self, value):
        return self.flashObject.as_setResetEnabled(value) if self._isDAAPIInited() else None

    def as_setApplyEnabledS(self, value):
        return self.flashObject.as_setApplyEnabled(value) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        """
        :param data: Represented by VehicleCompareConfiguratorInitDataVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

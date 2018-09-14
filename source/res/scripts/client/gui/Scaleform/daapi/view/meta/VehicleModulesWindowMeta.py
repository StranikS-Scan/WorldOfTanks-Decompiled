# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleModulesWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleModulesWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def onModuleHover(self, id):
        self._printOverrideError('onModuleHover')

    def onModuleClick(self, id):
        self._printOverrideError('onModuleClick')

    def onResetBtnBtnClick(self):
        self._printOverrideError('onResetBtnBtnClick')

    def onCompareBtnClick(self):
        self._printOverrideError('onCompareBtnClick')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by VehicleModulesWindowInitDataVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setItemS(self, nation, raw):
        return self.flashObject.as_setItem(nation, raw) if self._isDAAPIInited() else None

    def as_setNodesStatesS(self, data):
        return self.flashObject.as_setNodesStates(data) if self._isDAAPIInited() else None

    def as_setStateS(self, stateText, stateEnabled):
        return self.flashObject.as_setState(stateText, stateEnabled) if self._isDAAPIInited() else None

    def as_setAttentionVisibleS(self, value):
        return self.flashObject.as_setAttentionVisible(value) if self._isDAAPIInited() else None

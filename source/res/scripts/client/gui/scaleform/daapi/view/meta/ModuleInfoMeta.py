# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ModuleInfoMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ModuleInfoMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def onActionButtonClick(self):
        self._printOverrideError('onActionButtonClick')

    def as_setModuleInfoS(self, moduleInfo):
        return self.flashObject.as_setModuleInfo(moduleInfo) if self._isDAAPIInited() else None

    def as_setActionButtonS(self, data):
        """
        :param data: Represented by ModuleInfoActionVO (AS)
        """
        return self.flashObject.as_setActionButton(data) if self._isDAAPIInited() else None

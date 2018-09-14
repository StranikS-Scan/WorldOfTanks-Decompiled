# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrewOperationsPopOverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class CrewOperationsPopOverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def invokeOperation(self, operationName):
        """
        :param operationName:
        :return :
        """
        self._printOverrideError('invokeOperation')

    def as_updateS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None
